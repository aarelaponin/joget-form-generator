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
                - columns: Array of column definitions
                    Each column: {id: str, label: str, type: str, options: [], editable: bool}
                - readonly: Whether grid is readonly (optional)
                - validateMinRow: Minimum number of rows (optional)
                - validateMaxRow: Maximum number of rows (optional)
                - allowAddRow: Allow adding new rows (optional, default true)
                - allowDeleteRow: Allow deleting rows (optional, default true)
            context: Rendering context

        Returns:
            Template context dictionary
        """
        # Build column definitions for Form Grid
        columns = field.get("columns", [])
        column_defs = []
        for col in columns:
            col_def = {
                "id": col["id"],
                "label": col["label"],
                "type": col.get("type", "textField"),
                "editable": "true" if col.get("editable", True) else "false",
            }
            # Add options for selectBox columns
            if "options" in col:
                col_def["options"] = col["options"]
            column_defs.append(col_def)

        return {
            "id": field["id"],
            "label": field["label"],
            "formId": field.get("formId", ""),
            "columns": column_defs,
            "readonly": "true" if field.get("readonly", False) else "",
            "validateMinRow": (
                str(field.get("validateMinRow", "")) if field.get("validateMinRow") else ""
            ),
            "validateMaxRow": (
                str(field.get("validateMaxRow", "")) if field.get("validateMaxRow") else ""
            ),
            "allowAddRow": "true" if field.get("allowAddRow", True) else "false",
            "allowDeleteRow": "true" if field.get("allowDeleteRow", True) else "false",
        }
