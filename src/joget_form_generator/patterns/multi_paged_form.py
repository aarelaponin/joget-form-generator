"""Multi Paged Form pattern for Enterprise Edition."""

from typing import Any, ClassVar
from .base import BasePattern


class MultiPagedFormPattern(BasePattern):
    """Pattern for Joget Enterprise Multi Paged Form.

    Incorporates multiple forms in one single form with pagination/tabs.
    Available in Professional and Enterprise editions only.

    This pattern generates the production-correct MultiPagedForm structure
    with flat pageN_* properties inside the numberOfPage object.
    """

    template_name: ClassVar[str] = "multi_paged_form.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for Multi Paged Form template.

        Args:
            field: Field specification with properties:
                - id: Field ID
                - label: Field label (optional)
                - pages: Array of page definitions
                    Each page: {
                        formId: str,           # Required: referenced form ID
                        label: str,            # Page tab label
                        validate: bool,        # Validate on page change (default: True)
                        parentSubFormId: str,  # ID used in parent form to reference this subform
                        subFormParentId: str,  # FK field in subform pointing to parent (default: parent_id)
                        readonly: bool,        # Whether page is readonly
                        readonlyLabel: str     # Label when readonly
                    }
                - displayMode: "tab" | "wizard" (default: "tab")
                - partiallyStore: Allow partial saves (default: False)
                - storeMainFormOnPartiallyStore: Store main form on partial save (default: True)
                - onlyAllowSubmitOnLastPage: Only show submit on last page (default: False)
                - prevButtonLabel: Previous button text (default: "Previous")
                - nextButtonLabel: Next button text (default: "Next")
                - ajaxMode: Use AJAX mode (default: False)
                - css: Custom CSS (optional)
            context: Rendering context

        Returns:
            Template context dictionary
        """
        pages = field.get("pages", [])
        num_pages = len(pages)

        # Build flat pageN_* properties
        page_properties = {}
        for idx, page in enumerate(pages, start=1):
            prefix = f"page{idx}_"
            page_properties[f"{prefix}formDefId"] = page.get("formId", "")
            page_properties[f"{prefix}label"] = page.get("label", f"Page {idx}")
            page_properties[f"{prefix}validate"] = "true" if page.get("validate", True) else ""
            page_properties[f"{prefix}parentSubFormId"] = page.get("parentSubFormId", f"tab_{idx}")
            page_properties[f"{prefix}subFormParentId"] = page.get("subFormParentId", "parent_id")
            page_properties[f"{prefix}readonly"] = "true" if page.get("readonly", False) else ""
            page_properties[f"{prefix}readonlyLabel"] = page.get("readonlyLabel", "")

        return {
            "id": field["id"],
            "label": field.get("label", ""),
            "num_pages": str(num_pages),
            "page_properties": page_properties,
            "displayMode": field.get("displayMode", "tab"),
            "partiallyStore": "true" if field.get("partiallyStore", False) else "",
            "storeMainFormOnPartiallyStore": (
                "true" if field.get("storeMainFormOnPartiallyStore", True) else ""
            ),
            "onlyAllowSubmitOnLastPage": (
                "true" if field.get("onlyAllowSubmitOnLastPage", False) else ""
            ),
            "prevButtonLabel": field.get("prevButtonLabel", "Previous"),
            "nextButtonLabel": field.get("nextButtonLabel", "Next"),
            "ajaxMode": "true" if field.get("ajaxMode", False) else "",
            "css": field.get("css", ""),
        }
