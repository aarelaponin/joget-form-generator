"""
Validation tools for MCP server.

Provides tools to validate YAML specifications and Joget JSON.
"""

import json
import logging
from typing import Any

import yaml

from joget_form_generator.validators import DualValidator
from joget_form_generator.schema.validator import SchemaValidator

logger = logging.getLogger(__name__)


class ValidationTools:
    """Tools for validating form specifications and Joget JSON."""

    def __init__(self):
        """Initialize validation tools."""
        self.dual_validator = DualValidator()
        self.schema_validator = SchemaValidator()

    def validate_spec(self, yaml_spec: str) -> dict[str, Any]:
        """
        Validate a YAML form specification.

        Performs two-phase validation:
        1. JSON Schema validation (structural)
        2. Pydantic validation (semantic)

        Args:
            yaml_spec: YAML string to validate

        Returns:
            Dictionary with:
                - valid: bool
                - errors: list[str] (if invalid)
                - warnings: list[str] (if any)
                - form_info: dict (if valid, contains form metadata)
        """
        try:
            # Parse YAML
            spec = yaml.safe_load(yaml_spec)

            if not spec:
                return {"valid": False, "errors": ["Empty or invalid YAML specification"]}

            # Run dual validation
            result, form_spec = self.dual_validator.validate(spec)

            response = {
                "valid": result.valid,
                "errors": result.errors if result.errors else None,
                "warnings": result.warnings if result.warnings else None,
            }

            if result.valid and form_spec:
                # Add form metadata
                form_meta = spec.get("form", {})
                fields = spec.get("fields", [])
                response["form_info"] = {
                    "form_id": form_meta.get("id"),
                    "form_name": form_meta.get("name"),
                    "field_count": len(fields),
                    "field_types": list(set(f.get("type") for f in fields if "type" in f)),
                }

            return response

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return {"valid": False, "errors": [f"Invalid YAML syntax: {e}"]}
        except Exception as e:
            logger.exception("Unexpected error during validation")
            return {"valid": False, "errors": [f"Validation failed: {e}"]}

    def validate_joget_json(self, joget_json_str: str) -> dict[str, Any]:
        """
        Validate Joget form JSON structure.

        Checks that the JSON follows Joget's expected format including:
        - Required className and properties
        - Valid element structure (Section → Column → Fields)
        - Required binders (loadBinder, storeBinder)

        Args:
            joget_json_str: JSON string to validate

        Returns:
            Dictionary with:
                - valid: bool
                - errors: list[str] (if invalid)
                - structure: dict (if valid, describes structure)
        """
        try:
            joget_json = json.loads(joget_json_str)
        except json.JSONDecodeError as e:
            return {"valid": False, "errors": [f"Invalid JSON syntax: {e}"]}

        errors = []

        # Check root structure
        if not isinstance(joget_json, dict):
            return {"valid": False, "errors": ["Root element must be an object"]}

        # Check className
        class_name = joget_json.get("className")
        if class_name != "org.joget.apps.form.model.Form":
            errors.append(
                f"Invalid className: expected 'org.joget.apps.form.model.Form', "
                f"got '{class_name}'"
            )

        # Check properties
        props = joget_json.get("properties", {})
        required_props = ["id", "name", "tableName"]
        for prop in required_props:
            if prop not in props:
                errors.append(f"Missing required property: {prop}")

        # Check binders
        if "loadBinder" not in props:
            errors.append("Missing loadBinder configuration")
        if "storeBinder" not in props:
            errors.append("Missing storeBinder configuration")

        # Check elements structure
        elements = joget_json.get("elements", [])
        if not elements:
            errors.append("Form has no elements (sections)")
        else:
            for i, section in enumerate(elements):
                section_errors = self._validate_section(section, i)
                errors.extend(section_errors)

        if errors:
            return {"valid": False, "errors": errors}

        # Build structure summary
        structure = self._analyze_structure(joget_json)

        return {"valid": True, "structure": structure, "message": "Joget JSON is valid"}

    def _validate_section(self, section: dict, index: int) -> list[str]:
        """Validate a section element."""
        errors = []
        prefix = f"Section {index}"

        if not isinstance(section, dict):
            return [f"{prefix}: Must be an object"]

        class_name = section.get("className", "")
        if "Section" not in class_name:
            errors.append(f"{prefix}: Invalid className '{class_name}', expected Section")

        # Check for columns
        columns = section.get("elements", [])
        for j, column in enumerate(columns):
            column_errors = self._validate_column(column, index, j)
            errors.extend(column_errors)

        return errors

    def _validate_column(self, column: dict, section_idx: int, col_idx: int) -> list[str]:
        """Validate a column element."""
        errors = []
        prefix = f"Section {section_idx}, Column {col_idx}"

        if not isinstance(column, dict):
            return [f"{prefix}: Must be an object"]

        class_name = column.get("className", "")
        if "Column" not in class_name:
            errors.append(f"{prefix}: Invalid className '{class_name}', expected Column")

        return errors

    def _analyze_structure(self, joget_json: dict) -> dict[str, Any]:
        """Analyze and summarize form structure."""
        props = joget_json.get("properties", {})
        elements = joget_json.get("elements", [])

        field_count = 0
        field_types = set()

        def count_fields(elems: list):
            nonlocal field_count
            for elem in elems:
                class_name = elem.get("className", "")
                if "Section" not in class_name and "Column" not in class_name:
                    field_count += 1
                    # Extract field type from className
                    type_name = class_name.split(".")[-1] if class_name else "Unknown"
                    field_types.add(type_name)
                if "elements" in elem:
                    count_fields(elem["elements"])

        for section in elements:
            count_fields(section.get("elements", []))

        return {
            "form_id": props.get("id"),
            "form_name": props.get("name"),
            "table_name": props.get("tableName"),
            "section_count": len(elements),
            "field_count": field_count,
            "field_types": list(field_types),
        }
