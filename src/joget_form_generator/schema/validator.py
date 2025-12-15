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


class SchemaValidator:
    """Validates form specifications against JSON Schema."""

    def __init__(self, schema_path: Path | None = None):
        """
        Initialize validator with schema file.

        Args:
            schema_path: Path to JSON Schema file. If None, uses bundled schema.
        """
        if schema_path is None:
            schema_path = Path(__file__).parent / "form_spec_schema.json"

        with open(schema_path) as f:
            self.schema = json.load(f)

        # Enable format validation (e.g., "format": "uri")
        self.validator = Draft202012Validator(
            self.schema, format_checker=jsonschema.FormatChecker()
        )

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

        # Additional business logic warnings (non-fatal)
        if len(errors) == 0:
            warnings.extend(self._check_warnings(spec))

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

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
