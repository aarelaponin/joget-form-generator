"""JSON Schema validation for form specifications."""

import json
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

import jsonschema
from jsonschema import Draft202012Validator, ValidationError


@dataclass
class ValidationResult:
    """Result of schema validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid


class FormRegistry:
    """Registry of known forms for dependency validation."""

    def __init__(self) -> None:
        self._known_forms: set[str] = set()
        self._form_sources: dict[str, str] = {}  # formId -> source description

    def add_form(self, form_id: str, source: str = "unknown") -> None:
        """Register a known form."""
        self._known_forms.add(form_id)
        self._form_sources[form_id] = source

    def is_known(self, form_id: str) -> bool:
        """Check if a form is registered."""
        return form_id in self._known_forms

    def get_source(self, form_id: str) -> str | None:
        """Get the source of a form."""
        return self._form_sources.get(form_id)

    def get_all_forms(self) -> set[str]:
        """Get all known form IDs."""
        return self._known_forms.copy()

    def find_similar(self, form_id: str, threshold: float = 0.6) -> list[str]:
        """Find similar form IDs (for suggestions)."""
        scored: list[tuple[str, int]] = []
        form_id_lower = form_id.lower()

        for known_id in self._known_forms:
            known_lower = known_id.lower()
            score = 0

            # Exact substring match (highest priority)
            if form_id_lower in known_lower:
                score = 100 + len(form_id_lower)  # Longer match = higher score
            elif known_lower in form_id_lower:
                score = 90 + len(known_lower)
            # Check if form_id words appear in known_id
            else:
                # Split camelCase/snake_case into words
                import re

                form_words = set(re.split(r"[_\s]|(?=[A-Z])", form_id_lower))
                known_words = set(re.split(r"[_\s]|(?=[A-Z])", known_lower))
                form_words = {w.lower() for w in form_words if len(w) > 2}
                known_words = {w.lower() for w in known_words if len(w) > 2}

                # Count matching words
                common_words = form_words & known_words
                if common_words:
                    score = 50 + len(common_words) * 10

            if score > 0:
                scored.append((known_id, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [form_id for form_id, _ in scored[:5]]

    @classmethod
    def from_directories(
        cls, mdm_dir: Path | None = None, specs_dir: Path | None = None
    ) -> "FormRegistry":
        """
        Build registry from existing MDM CSV files and YAML specs.

        Args:
            mdm_dir: Directory containing MDM CSV files (e.g., md01maritalStatus.csv)
            specs_dir: Directory containing YAML form specs
        """
        registry = cls()

        # Load from MDM CSV files
        if mdm_dir and mdm_dir.exists():
            for csv_file in mdm_dir.glob("*.csv"):
                # Form ID is the filename without extension
                form_id = csv_file.stem
                registry.add_form(form_id, f"MDM: {csv_file.name}")

        # Load from YAML specs
        if specs_dir and specs_dir.exists():
            for yaml_file in specs_dir.glob("*.yaml"):
                # Try to extract form ID from the file
                form_id = yaml_file.stem
                registry.add_form(form_id, f"YAML: {yaml_file.name}")

        return registry


class SchemaValidator:
    """Validates form specifications against JSON Schema."""

    def __init__(
        self,
        schema_path: Path | None = None,
        form_registry: FormRegistry | None = None,
        strict_dependencies: bool = False,
    ):
        """
        Initialize validator with schema file.

        Args:
            schema_path: Path to JSON Schema file. If None, uses bundled schema.
            form_registry: Registry of known forms for dependency validation.
            strict_dependencies: If True, unknown form references are errors. If False, warnings.
        """
        if schema_path is None:
            schema_path = Path(__file__).parent / "form_spec_schema.json"

        with open(schema_path) as f:
            self.schema = json.load(f)

        # Enable format validation (e.g., "format": "uri")
        self.validator = Draft202012Validator(
            self.schema, format_checker=jsonschema.FormatChecker()
        )

        self.form_registry = form_registry
        self.strict_dependencies = strict_dependencies

    def validate(self, spec: dict[str, Any]) -> ValidationResult:
        """
        Validate specification against schema.

        Args:
            spec: Form specification dictionary (parsed YAML)

        Returns:
            ValidationResult with errors and warnings
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Run JSON Schema validation
        for error in sorted(self.validator.iter_errors(spec), key=str):
            error_msg = self._format_error(error)
            errors.append(error_msg)

        # Additional business logic errors (fatal)
        if len(errors) == 0:
            errors.extend(self._check_business_rules(spec))

        # Additional business logic warnings (non-fatal)
        if len(errors) == 0:
            warnings.extend(self._check_warnings(spec))

        # Form dependency validation (if registry provided)
        if self.form_registry and len(errors) == 0:
            dep_errors, dep_warnings = self._validate_form_dependencies(spec)
            if self.strict_dependencies:
                errors.extend(dep_errors)
            else:
                warnings.extend(dep_errors)
            warnings.extend(dep_warnings)

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def _extract_form_references(self, spec: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract all formId references from a specification.

        Returns list of dicts with: field_id, form_id, context (where it's used), required
        """
        references: list[dict[str, Any]] = []

        for field_spec in spec.get("fields", []):
            field_id = field_spec.get("id", "unknown")
            field_type = field_spec.get("type", "")
            is_required = field_spec.get("required", False)

            # Check optionsSource.formId (selectBox, checkBox, radio)
            options_src = field_spec.get("optionsSource", {})
            if options_src.get("type") == "formData" and options_src.get("formId"):
                references.append(
                    {
                        "field_id": field_id,
                        "form_id": options_src["formId"],
                        "context": "optionsSource",
                        "required": is_required,
                    }
                )

            # Check formGrid.formId
            if field_type == "formGrid" and field_spec.get("formId"):
                references.append(
                    {
                        "field_id": field_id,
                        "form_id": field_spec["formId"],
                        "context": "formGrid",
                        "required": True,  # FormGrid always needs the child form
                    }
                )

            # Check subform.formId
            if field_type == "subform" and field_spec.get("formId"):
                references.append(
                    {
                        "field_id": field_id,
                        "form_id": field_spec["formId"],
                        "context": "subform",
                        "required": True,
                    }
                )

        return references

    def _validate_form_dependencies(self, spec: dict[str, Any]) -> tuple[list[str], list[str]]:
        """
        Validate all form references against the registry.

        Returns:
            Tuple of (errors, warnings)
        """
        errors: list[str] = []
        warnings: list[str] = []

        if not self.form_registry:
            return errors, warnings

        references = self._extract_form_references(spec)

        for ref in references:
            form_id = ref["form_id"]
            field_id = ref["field_id"]
            context = ref["context"]
            is_required = ref["required"]

            if not self.form_registry.is_known(form_id):
                # Build error/warning message
                msg = f"Field '{field_id}' references unknown form '{form_id}' " f"in {context}"

                # Try to find similar forms for suggestion
                similar = self.form_registry.find_similar(form_id)
                if similar:
                    msg += f"\n  💡 Did you mean: {', '.join(similar)}?"

                # Critical fields (required or formGrid) are errors
                if is_required or context in ("formGrid", "subform"):
                    errors.append(msg)
                else:
                    warnings.append(msg)

        return errors, warnings

    def _format_error(self, error: ValidationError) -> str:
        """
        Format validation error with path and suggestion.

        Args:
            error: jsonschema ValidationError

        Returns:
            Formatted error message with suggestion
        """
        # Build path to error location
        path_parts = [str(p) for p in error.absolute_path]
        path = " → ".join(path_parts) if path_parts else "root"

        message = error.message

        # Add contextual suggestions
        suggestion = self._get_suggestion(error)
        if suggestion:
            message = f"{message}\n  💡 {suggestion}"

        return f"[{path}] {message}"

    def _get_suggestion(self, error: ValidationError) -> str | None:
        """Get actionable suggestion for common errors."""

        # Pattern validation errors (ID format)
        if error.validator == "pattern":
            if "id" in error.absolute_path:
                return (
                    "ID must start with letter, contain only alphanumeric/underscore, max 20 chars"
                )

        # Missing required field
        if error.validator == "required":
            missing_field = error.message.split("'")[1] if "'" in error.message else "field"
            return f"Add required property: {missing_field}"

        # Enum mismatch (wrong field type)
        if error.validator == "enum":
            valid_values = error.schema.get("enum", [])
            if len(valid_values) <= 5:
                return f"Valid values: {', '.join(valid_values)}"
            else:
                return f"See schema for valid values (total: {len(valid_values)})"

        # oneOf errors (selectBox needs options OR optionsSource)
        if error.validator == "oneOf":
            if "selectBox" in str(error.instance):
                return "SelectBox must have either 'options' (static) or 'optionsSource' (dynamic)"

        return None

    def _check_business_rules(self, spec: dict[str, Any]) -> list[str]:
        """Check for critical business rule violations that must fail validation."""
        errors = []

        # Rule: valueColumn must NEVER be 'id' - always use 'code' or specific code field
        for field_spec in spec.get("fields", []):
            field_id = field_spec.get("id", "unknown")
            options_src = field_spec.get("optionsSource", {})

            if options_src.get("type") == "formData":
                value_column = options_src.get("valueColumn", "")
                if value_column == "id":
                    form_id = options_src.get("formId", "unknown")
                    errors.append(
                        f"Field '{field_id}': valueColumn 'id' is not allowed. "
                        f"Use 'code' or the appropriate code field (e.g., 'campaignCode') "
                        f"for form '{form_id}'. Joget internal IDs should never be used as FK values."
                    )

        # Rule: Field IDs ending in 'Id' with optionsSource should use '*Code' instead
        # Exception: actual ID fields like 'nationalId', 'taxId', 'deviceId' are allowed
        import re

        allowed_id_suffixes = {"nationalId", "taxId", "deviceId", "officerId", "registrationId"}
        for field_spec in spec.get("fields", []):
            field_id = field_spec.get("id", "")
            options_src = field_spec.get("optionsSource", {})
            field_type = field_spec.get("type", "")

            # Check if field ends with 'Id' (but not in allowed list) and has optionsSource
            if (
                re.search(r"[a-z]Id$", field_id)
                and field_id not in allowed_id_suffixes
                and not any(field_id.endswith(suffix) for suffix in allowed_id_suffixes)
            ):

                # If it has optionsSource, it's a FK field and should use *Code
                if options_src.get("type") == "formData":
                    suggested_name = re.sub(r"Id$", "Code", field_id)
                    errors.append(
                        f"Field '{field_id}': FK field names should end with 'Code', not 'Id'. "
                        f"Rename to '{suggested_name}'. "
                        f"Joget reserves 'id' and '*Id' patterns can cause conflicts."
                    )
                # If it's a hidden field used as FK (e.g., in child forms), also flag it
                elif field_type == "hiddenField" and re.search(
                    r"(campaign|program|entitlement|distribution|dealer|farmer)Id$", field_id, re.I
                ):
                    suggested_name = re.sub(r"Id$", "Code", field_id)
                    errors.append(
                        f"Field '{field_id}': FK field names should end with 'Code', not 'Id'. "
                        f"Rename to '{suggested_name}'. "
                        f"Joget reserves 'id' and '*Id' patterns can cause conflicts."
                    )

        return errors

    def _check_warnings(self, spec: dict[str, Any]) -> list[str]:
        """Check for non-critical issues that should warn user."""
        warnings = []

        # Check form ID matches tableName
        form_meta = spec.get("form", {})
        form_id = form_meta.get("id")
        table_name = form_meta.get("tableName")

        if form_id and table_name and form_id != table_name:
            warnings.append(
                f"Form 'id' ({form_id}) and 'tableName' ({table_name}) should match. "
                "Joget requires identical values for proper table creation."
            )

        # Check for cascading selectBox without parent field
        for idx, field_spec in enumerate(spec.get("fields", [])):
            if field_spec.get("type") == "selectBox":
                options_src = field_spec.get("optionsSource", {})
                if options_src.get("type") == "formData":
                    if not options_src.get("parentField") and not options_src.get("filterField"):
                        field_id = field_spec.get("id", f"field[{idx}]")
                        warnings.append(
                            f"Field '{field_id}' uses formData options but missing "
                            "'parentField' for cascading dropdown (may be intentional)"
                        )

        # Check for duplicate field IDs
        field_ids = [f.get("id") for f in spec.get("fields", []) if f.get("id")]
        duplicates = {fid for fid in field_ids if field_ids.count(fid) > 1}
        if duplicates:
            warnings.append(
                f"Duplicate field IDs found: {', '.join(duplicates)}. "
                "This will cause database column conflicts."
            )

        return warnings
