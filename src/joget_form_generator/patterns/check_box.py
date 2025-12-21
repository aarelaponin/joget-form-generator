"""CheckBox pattern."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin, OptionsMixin, ValidationMixin


class CheckBoxPattern(BasePattern, ReadOnlyMixin, OptionsMixin, ValidationMixin):
    """Pattern for Joget Check Box."""

    template_name: ClassVar[str] = "check_box.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Prepare context for CheckBox template."""
        # For static options, put them in options array
        # For dynamic options, put them in optionsBinder
        static_options = field.get("options", [])
        options = self.build_static_options_array(static_options) if static_options else None
        options_binder = self.build_options_binder(field, context)

        return {
            "id": field["id"],
            "label": field["label"],
            "options": options,
            "options_binder": options_binder,
            "value": field.get("defaultValue", ""),
            "validator": self.build_validator(field),
            **self.get_readonly_props(field),
        }
