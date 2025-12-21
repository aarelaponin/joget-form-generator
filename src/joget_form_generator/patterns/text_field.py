"""TextField pattern."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin, ValidationMixin


class TextFieldPattern(BasePattern, ReadOnlyMixin, ValidationMixin):
    """Pattern for Joget TextField."""

    template_name: ClassVar[str] = "text_field.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Prepare context for TextField template."""
        return {
            "id": field["id"],
            "label": field["label"],
            "value": field.get("defaultValue", ""),
            "style": "",
            "maxlength": field.get("maxlength", ""),
            "placeholder": field.get("placeholder", ""),
            "validator": self.build_validator(field),
            **self.get_readonly_props(field),
        }
