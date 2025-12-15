"""Subform pattern for embedding forms (master-detail relationships)."""

from typing import Any, ClassVar
from .base import BasePattern


class SubformPattern(BasePattern):
    """Pattern for rendering subform fields (master-detail relationship)."""

    template_name: ClassVar[str] = "subform.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for Subform template.

        Args:
            field: Field specification with properties:
                - id: Field ID
                - label: Field label
                - type: "subform"
                - formId: Referenced form definition ID (required)
                - readonly: Whether subform is read-only (optional)
                - addButtonLabel: Label for add button (optional)
                - deleteButtonLabel: Label for delete button (optional)
                - noAddButton: Hide add button (optional)
                - noDeleteButton: Hide delete button (optional)
                - required: Whether field is required (optional)
            context: Rendering context

        Returns:
            Template context dictionary
        """
        # Build validator if required
        validator = {}
        if field.get("required", False):
            validator = {
                "className": "org.joget.apps.form.lib.DefaultValidator",
                "properties": {
                    "mandatory": "true",
                    "message": f"{field['label']} is required",
                },
            }

        return {
            "id": field["id"],
            "label": field["label"],
            "formDefId": field["formId"],
            "readonly": "true" if field.get("readonly", False) else "",
            "readonlyLabel": "true" if field.get("readonlyLabel", False) else "",
            "addButtonLabel": field.get("addButtonLabel", "Add"),
            "deleteButtonLabel": field.get("deleteButtonLabel", "Delete"),
            "noAddButton": "true" if field.get("noAddButton", False) else "",
            "noDeleteButton": "true" if field.get("noDeleteButton", False) else "",
            "validator": validator,
            "workflowVariable": field.get("workflowVariable", ""),
        }
