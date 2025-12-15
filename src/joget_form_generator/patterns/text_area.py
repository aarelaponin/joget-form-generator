"""TextArea pattern."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin, ValidationMixin


class TextAreaPattern(BasePattern, ReadOnlyMixin, ValidationMixin):
    """Pattern for Joget Text Area."""

    template_name: ClassVar[str] = "text_area.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Prepare context for TextArea template."""
        return {
            "id": field["id"],
            "label": field["label"],
            "value": field.get("defaultValue", ""),
            "rows": field.get("rows", 5),
            "cols": field.get("cols", 50),
            "placeholder": field.get("placeholder", ""),
            "validator": self.build_validator(field),
            **self.get_readonly_props(field),
        }
