"""IDGenerator pattern for auto-generating unique IDs."""

from typing import Any, ClassVar
from .base import BasePattern


class IDGeneratorPattern(BasePattern):
    """Pattern for rendering ID generator fields."""

    template_name: ClassVar[str] = "id_generator.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for IDGenerator template.

        Args:
            field: Field specification with properties:
                - id: Field ID
                - label: Field label
                - type: "idGenerator"
                - prefix: ID prefix (optional)
                - postfix: ID postfix (optional)
                - format: Format pattern (optional)
            context: Rendering context

        Returns:
            Template context dictionary
        """
        return {
            "id": field["id"],
            "label": field["label"],
            "defaultValue": field.get("defaultValue", ""),
            "prefix": field.get("prefix", ""),
            "postfix": field.get("postfix", ""),
            "format": field.get("format", "{prefix}{count:05d}{postfix}"),
        }
