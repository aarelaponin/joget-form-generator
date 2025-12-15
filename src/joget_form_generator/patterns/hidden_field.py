"""HiddenField pattern - simplest field type."""

from typing import Any, ClassVar
from .base import BasePattern


class HiddenFieldPattern(BasePattern):
    """Pattern for Joget Hidden Field."""

    template_name: ClassVar[str] = "hidden_field.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Prepare context for HiddenField template."""
        return {"id": field["id"], "value": field.get("defaultValue", "")}
