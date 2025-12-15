"""Multi Paged Form pattern for Enterprise Edition."""

from typing import Any, ClassVar
from .base import BasePattern


class MultiPagedFormPattern(BasePattern):
    """Pattern for Joget Enterprise Multi Paged Form.

    Incorporates multiple forms in one single form with pagination.
    Available in Professional and Enterprise editions only.
    """

    template_name: ClassVar[str] = "multi_paged_form.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for Multi Paged Form template.

        Args:
            field: Field specification with properties:
                - id: Field ID
                - label: Field label (optional, for page title)
                - pages: Array of page definitions
                    Each page: {formId: str, label: str, description: str}
                - showNavigation: Show page navigation (optional, default true)
                - showProgressBar: Show progress bar (optional, default true)
                - readonly: Whether all pages are readonly (optional)
            context: Rendering context

        Returns:
            Template context dictionary
        """
        # Build page definitions
        pages = field.get("pages", [])
        page_defs = []
        for page in pages:
            page_def = {
                "formDefId": page["formId"],
                "label": page.get("label", ""),
                "description": page.get("description", ""),
            }
            page_defs.append(page_def)

        return {
            "id": field["id"],
            "label": field.get("label", ""),
            "pages": page_defs,
            "showNavigation": "true" if field.get("showNavigation", True) else "false",
            "showProgressBar": "true" if field.get("showProgressBar", True) else "false",
            "readonly": "true" if field.get("readonly", False) else "",
        }
