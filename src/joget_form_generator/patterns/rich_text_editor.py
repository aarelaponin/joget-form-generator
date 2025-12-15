"""Rich Text Editor pattern for Enterprise Edition."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin


class RichTextEditorPattern(BasePattern, ReadOnlyMixin):
    """Pattern for Joget Enterprise Rich Text Editor.

    WYSIWYG HTML editor for rich text content.
    Available in Enterprise Edition only.
    Supports TinyMCE and Quill editors.
    """

    template_name: ClassVar[str] = "rich_text_editor.j2"

    def _prepare_context(
        self, field: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Prepare context for Rich Text Editor template.

        Args:
            field: Field specification with properties:
                - id: Field ID
                - label: Field label
                - editor: Editor type ("tinymce" or "quill", default "tinymce")
                - readonly: Whether field is readonly (optional)
                - defaultValue: Default HTML content (optional)
                - rows: Height in rows (optional)
                - placeholder: Placeholder text (optional)
            context: Rendering context

        Returns:
            Template context dictionary
        """
        return {
            "id": field["id"],
            "label": field["label"],
            "editor": field.get("editor", "tinymce"),
            "value": field.get("defaultValue", ""),
            "rows": str(field.get("rows", 10)),
            "placeholder": field.get("placeholder", ""),
            **self.get_readonly_props(field),
        }
