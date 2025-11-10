"""CheckBox pattern."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin, OptionsMixin


class CheckBoxPattern(BasePattern, ReadOnlyMixin, OptionsMixin):
    """Pattern for Joget Check Box."""

    template_name: ClassVar[str] = "check_box.j2"

    def _prepare_context(
        self, field: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Prepare context for CheckBox template."""
        return {
            "id": field["id"],
            "label": field["label"],
            "options_binder": self.build_options_binder(field, context),
            **self.get_readonly_props(field),
        }
