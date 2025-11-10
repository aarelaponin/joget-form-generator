"""Dual validation pipeline: JSON Schema + Pydantic."""

from typing import Any
from pathlib import Path

from .schema.validator import SchemaValidator, ValidationResult
from pydantic import ValidationError as PydanticValidationError


class DualValidator:
    """Runs both JSON Schema and Pydantic validation."""

    def __init__(self, schema_path: Path | None = None):
        self.schema_validator = SchemaValidator(schema_path)

    def validate(
        self, spec_dict: dict[str, Any]
    ) -> tuple[ValidationResult, Any | None]:
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
                loc = " → ".join(str(l) for l in error["loc"])
                msg = error["msg"]
                errors.append(f"[{loc}] {msg}")

            pydantic_result = ValidationResult(
                valid=False,
                errors=errors,
                warnings=json_result.warnings,  # Keep JSON Schema warnings
            )

            return pydantic_result, None
