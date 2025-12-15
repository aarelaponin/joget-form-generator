"""Grid pattern for simple tabular data entry."""

from typing import Any, ClassVar
from .base import BasePattern


class GridPattern(BasePattern):
    """Pattern for rendering grid fields (simple table)."""

    template_name: ClassVar[str] = "grid.j2"

    def _prepare_context(
        self, field: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Prepare context for Grid template.

        Args:
            field: Field specification with properties:
                - id: Field ID
                - label: Field label
                - type: "grid"
                - columns: Array of column definitions
                    Each column: {id: str, label: str}
                - readonly: Whether grid is read-only (optional)
                - validateMinRow: Minimum number of rows (optional)
                - validateMaxRow: Maximum number of rows (optional)
                - errorMessage: Error message for row validation (optional)
            context: Rendering context

        Returns:
            Template context dictionary
        """
        # Convert columns to options format (Joget uses "options" for grid columns)
        columns = field.get("columns", [])
        options = [
            {"value": col["id"], "label": col["label"]}
            for col in columns
        ]

        # Build validator if min/max row validation needed
        validator = {}
        validate_min_row = field.get("validateMinRow", "")
        validate_max_row = field.get("validateMaxRow", "")
        error_message = field.get("errorMessage", "")

        return {
            "id": field["id"],
            "label": field["label"],
            "options": options,
            "readonly": "true" if field.get("readonly", False) else "",
            "validator": validator,
            "validateMinRow": str(validate_min_row) if validate_min_row else "",
            "validateMaxRow": str(validate_max_row) if validate_max_row else "",
            "errorMessage": error_message,
        }
