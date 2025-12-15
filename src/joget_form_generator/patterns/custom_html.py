"""CustomHTML pattern for custom HTML elements."""

from typing import Any, ClassVar
from .base import BasePattern


class CustomHTMLPattern(BasePattern):
    """Pattern for rendering custom HTML elements."""

    template_name: ClassVar[str] = "custom_html.j2"

    def _prepare_context(
        self, field: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Prepare context for CustomHTML template.

        Args:
            field: Field specification with properties:
                - id: Field ID
                - label: Field label (optional for display-only content)
                - type: "customHTML"
                - html: HTML content to display
            context: Rendering context

        Returns:
            Template context dictionary
        """
        return {
            "id": field["id"],
            "label": field.get("label", ""),
            "html": field.get("html", ""),
        }
