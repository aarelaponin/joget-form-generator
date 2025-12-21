"""DatePicker pattern."""

from typing import Any, ClassVar
from .base import BasePattern


class DatePickerPattern(BasePattern):
    """Pattern for Joget Date Picker."""

    template_name: ClassVar[str] = "date_picker.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Prepare context for DatePicker template."""
        # Build validator if required
        validator = None
        if field.get("required", False):
            validator = {
                "className": "org.joget.apps.form.lib.DefaultValidator",
                "properties": {
                    "mandatory": "true",
                    "type": "",
                    "message": "",
                },
            }

        return {
            "id": field["id"],
            "label": field["label"],
            "value": field.get("defaultValue", ""),
            "dataFormat": field.get("dateFormat", "yyyy-MM-dd"),
            "readonly": "true" if field.get("readonly", False) else "",
            "validator": validator,
        }
