"""SelectBox pattern with cascading dropdown support."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin, OptionsMixin


class SelectBoxPattern(BasePattern, ReadOnlyMixin, OptionsMixin):
    """Pattern for Joget SelectBox with cascading support."""

    template_name: ClassVar[str] = "select_box.j2"

    def _prepare_context(
        self, field: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Prepare context for SelectBox template."""
        return {
            "id": field["id"],
            "label": field["label"],
            "multiple": "true" if field.get("multiple", False) else "",
            "size": field.get("size", 10),
            "options_binder": self.build_options_binder(field, context),
            **self.get_readonly_props(field),
        }
