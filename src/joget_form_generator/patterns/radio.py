"""Radio button pattern."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin, OptionsMixin


class RadioPattern(BasePattern, ReadOnlyMixin, OptionsMixin):
    """Pattern for Joget Radio Button."""

    template_name: ClassVar[str] = "radio.j2"

    def _prepare_context(
        self, field: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Prepare context for Radio template."""
        return {
            "id": field["id"],
            "label": field["label"],
            "options_binder": self.build_options_binder(field, context),
            **self.get_readonly_props(field),
        }
