"""DatePicker pattern."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin, ValidationMixin


class DatePickerPattern(BasePattern, ReadOnlyMixin, ValidationMixin):
    """Pattern for Joget Date Picker."""

    template_name: ClassVar[str] = "date_picker.j2"

    def _prepare_context(
        self, field: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Prepare context for DatePicker template."""
        return {
            "id": field["id"],
            "label": field["label"],
            "value": field.get("defaultValue", ""),
            "format": field.get("dateFormat", "yyyy-MM-dd"),
            "validator": self.build_validator(field),
            **self.get_readonly_props(field),
        }
