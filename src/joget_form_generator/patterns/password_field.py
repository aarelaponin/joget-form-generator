"""PasswordField pattern."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin, ValidationMixin


class PasswordFieldPattern(BasePattern, ReadOnlyMixin, ValidationMixin):
    """Pattern for Joget Password Field."""

    template_name: ClassVar[str] = "password_field.j2"

    def _prepare_context(
        self, field: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Prepare context for PasswordField template."""
        return {
            "id": field["id"],
            "label": field["label"],
            "size": field.get("size", "medium"),
            "maxlength": field.get("maxlength", ""),
            "placeholder": field.get("placeholder", ""),
            "validator": self.build_validator(field),
            **self.get_readonly_props(field),
        }
