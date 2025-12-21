"""IDGenerator pattern for auto-generating unique IDs."""

from typing import Any, ClassVar
from .base import BasePattern


class IDGeneratorPattern(BasePattern):
    """Pattern for rendering ID generator fields."""

    template_name: ClassVar[str] = "id_generator.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for IDGenerator template.

        Joget IdGeneratorField uses:
        - format: Pattern with ? as placeholders (e.g., "AD-??????" generates AD-000001)
        - envVariable: Environment variable name for counter (e.g., "counter")
        - hidden: Whether to hide the field

        Args:
            field: Field specification with properties:
                - id: Field ID
                - label: Field label
                - type: "idGenerator"
                - prefix: ID prefix (e.g., "AD-")
                - format: Format pattern with ? placeholders (optional)
                - hidden: Whether field is hidden (optional)
            context: Rendering context

        Returns:
            Template context dictionary
        """
        # Build format string: prefix + ?????? (6 question marks for counter)
        prefix = field.get("prefix", "")
        format_str = field.get("format", f"{prefix}??????")

        return {
            "id": field["id"],
            "label": field["label"],
            "format": format_str,
            "envVariable": field.get("envVariable", "counter"),
            "hidden": "true" if field.get("hidden", False) else "",
        }
