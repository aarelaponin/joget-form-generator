"""SelectBox pattern with cascading dropdown support."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin, OptionsMixin, ValidationMixin


class SelectBoxPattern(BasePattern, ReadOnlyMixin, OptionsMixin, ValidationMixin):
    """Pattern for Joget SelectBox with cascading support."""

    template_name: ClassVar[str] = "select_box.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Prepare context for SelectBox template."""
        # For static options, put them in options array with grouping field
        # For dynamic options, put them in optionsBinder
        static_options = field.get("options", [])
        options = self.build_static_options_array(static_options) if static_options else None
        options_binder = self.build_options_binder(field, context)

        # Build validator using ValidationMixin
        validator = self.build_validator(field)

        return {
            "id": field["id"],
            "label": field["label"],
            "multiple": "true" if field.get("multiple", False) else "",
            "value": field.get("defaultValue", ""),
            "options": options,
            "options_binder": options_binder,
            "validator": validator,
            "readonly": "true" if field.get("readonly", False) else "",
        }
