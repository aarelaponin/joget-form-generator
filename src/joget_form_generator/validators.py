"""Dual validation pipeline: JSON Schema + Pydantic."""

from typing import Any
from pathlib import Path

from .schema.validator import SchemaValidator, ValidationResult, FormRegistry
from pydantic import ValidationError as PydanticValidationError


class DualValidator:
    """Runs both JSON Schema and Pydantic validation."""

    def __init__(
        self,
        schema_path: Path | None = None,
        mdm_dir: Path | None = None,
        specs_dir: Path | None = None,
        strict_dependencies: bool = False,
    ):
        """
        Initialize dual validator.

        Args:
            schema_path: Path to JSON Schema file. If None, uses bundled schema.
            mdm_dir: Directory containing MDM CSV files for form registry.
            specs_dir: Directory containing YAML form specs for form registry.
            strict_dependencies: If True, unknown form references are errors.
        """
        # Build form registry if directories provided
        form_registry = None
        if mdm_dir or specs_dir:
            form_registry = FormRegistry.from_directories(mdm_dir, specs_dir)

        self.schema_validator = SchemaValidator(
            schema_path, form_registry=form_registry, strict_dependencies=strict_dependencies
        )

    def validate(self, spec_dict: dict[str, Any]) -> tuple[ValidationResult, Any | None]:
        """
        Run dual validation.

        Args:
            spec_dict: Form specification dictionary

        Returns:
            Tuple of (ValidationResult, FormSpec or None)
            - If validation fails, FormSpec is None
            - If validation succeeds, FormSpec is populated Pydantic model
        """
        # Phase 1: JSON Schema validation (structural)
        json_result = self.schema_validator.validate(spec_dict)

        if not json_result.valid:
            # Early exit if structural validation fails
            return json_result, None

        # Phase 2: Pydantic validation (semantic)
        try:
            # Import here to avoid circular dependency
            from .models.spec import JogetFormSpecification

            form_spec = JogetFormSpecification(**spec_dict)

            # Run custom Pydantic validators
            # (These are defined in generated spec.py with @field_validator)

            return json_result, form_spec

        except PydanticValidationError as e:
            # Convert Pydantic errors to our format
            errors = []
            for error in e.errors():
                loc = " → ".join(str(part) for part in error["loc"])
                msg = error["msg"]
                errors.append(f"[{loc}] {msg}")

            pydantic_result = ValidationResult(
                valid=False,
                errors=errors,
                warnings=json_result.warnings,  # Keep JSON Schema warnings
            )

            return pydantic_result, None
