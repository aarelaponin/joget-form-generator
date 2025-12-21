"""Form Grid pattern for Enterprise Edition."""

from typing import Any, ClassVar
from .base import BasePattern


class FormGridPattern(BasePattern):
    """Pattern for Joget Enterprise Form Grid.

    Advanced grid that extends default grid functionality.
    Supports complex field types within cells.
    Available in Professional and Enterprise editions only.
    """

    template_name: ClassVar[str] = "form_grid.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for Form Grid template.

        Args:
            field: Field specification with properties:
                - id: Field ID
                - label: Field label
                - formId: Referenced form ID for grid rows
                - foreignKey: Foreign key field in child form (optional, defaults to parent form id + "_id")
                - columns: Array of column definitions (optional)
                    Each column: {value: str, label: str, formatType: str, format: str, width: str}
                - readonly: Whether grid is readonly (optional)
                - validateMinRow: Minimum number of rows (optional)
                - validateMaxRow: Maximum number of rows (optional)
                - allowAddRow: Allow adding new rows (optional, default true)
                - allowDeleteRow: Allow deleting rows (optional, default true)
            context: Rendering context

        Returns:
            Template context dictionary
        """
        # Build column definitions for Form Grid - Joget uses "options" array
        # with value, label, formatType, format, width structure
        columns = field.get("columns", [])
        column_defs = []
        for col in columns:
            col_def = {
                "value": col.get("value", col.get("id", "")),
                "label": col.get("label", ""),
                "formatType": col.get("formatType", "text"),
                "format": col.get("format", ""),
                "width": col.get("width", ""),
            }
            column_defs.append(col_def)

        # Get form metadata for foreign key default
        form_id = context.get("form_id", "")
        default_fk = f"{form_id}_id" if form_id else ""

        return {
            "id": field["id"],
            "label": field["label"],
            "formId": field.get("formId", ""),
            "foreignKey": field.get("foreignKey", default_fk),
            "columns": column_defs,
            "readonly": "true" if field.get("readonly", False) else "",
            "validateMinRow": (
                str(field.get("validateMinRow", "")) if field.get("validateMinRow") else ""
            ),
            "validateMaxRow": (
                str(field.get("validateMaxRow", "")) if field.get("validateMaxRow") else ""
            ),
            "allowAddRow": field.get("allowAddRow", True),
            "allowDeleteRow": field.get("allowDeleteRow", True),
            "errorMessage": field.get("errorMessage", ""),
        }
