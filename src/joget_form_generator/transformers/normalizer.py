"""Normalization phase: apply defaults and resolve references."""

from typing import Any


class Normalizer:
    """Applies defaults and resolves references in specification."""

    DEFAULT_FIELD_VALUES = {"required": False, "readonly": False, "size": "medium"}

    DEFAULT_FORM_VALUES = {"description": ""}

    def normalize(self, spec: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize specification by applying defaults.

        Args:
            spec: Validated specification

        Returns:
            Normalized specification
        """
        normalized = spec.copy()

        # Apply form-level defaults
        normalized["form"] = self._apply_defaults(
            normalized["form"], self.DEFAULT_FORM_VALUES
        )

        # Ensure id matches tableName (critical for Joget)
        form_meta = normalized["form"]
        if "tableName" not in form_meta:
            form_meta["tableName"] = form_meta["id"]
        elif form_meta["id"] != form_meta["tableName"]:
            # If they don't match, use id as canonical
            form_meta["tableName"] = form_meta["id"]

        # Apply field-level defaults
        normalized["fields"] = [
            self._apply_field_defaults(field) for field in normalized["fields"]
        ]

        return normalized

    def _apply_field_defaults(self, field: dict[str, Any]) -> dict[str, Any]:
        """Apply defaults specific to field type."""
        normalized_field = self._apply_defaults(field, self.DEFAULT_FIELD_VALUES)

        field_type = normalized_field.get("type")

        # Type-specific defaults
        if field_type == "textArea":
            if "rows" not in normalized_field:
                normalized_field["rows"] = 5
            if "cols" not in normalized_field:
                normalized_field["cols"] = 50

        elif field_type == "selectBox":
            if "size" not in normalized_field:
                normalized_field["size"] = 10

        elif field_type == "datePicker":
            if "dateFormat" not in normalized_field:
                normalized_field["dateFormat"] = "yyyy-MM-dd"

        elif field_type == "fileUpload":
            if "maxSize" not in normalized_field:
                normalized_field["maxSize"] = 10  # 10 MB default
            if "fileTypes" not in normalized_field:
                normalized_field["fileTypes"] = "*"

        return normalized_field

    def _apply_defaults(self, obj: dict, defaults: dict) -> dict:
        """Apply default values for missing keys."""
        result = obj.copy()
        for key, default_value in defaults.items():
            if key not in result:
                result[key] = default_value
        return result
