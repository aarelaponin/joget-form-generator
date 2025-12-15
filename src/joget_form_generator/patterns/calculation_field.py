"""Calculation Field pattern for Enterprise Edition."""

from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin


class CalculationFieldPattern(BasePattern, ReadOnlyMixin):
    """Pattern for Joget Enterprise Calculation Field.

    Performs arithmetic computations on form field values.
    Available in Professional and Enterprise editions only.
    """

    template_name: ClassVar[str] = "calculation_field.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for Calculation Field template.

        Args:
            field: Field specification with properties:
                - id: Field ID
                - label: Field label
                - equation: Calculation equation/formula
                - storeNumeric: Whether to store as numeric (optional, default true)
                - readonly: Whether field is readonly (typically true)
                - defaultValue: Default value if calculation fails (optional)
            context: Rendering context

        Returns:
            Template context dictionary
        """
        return {
            "id": field["id"],
            "label": field["label"],
            "equation": field.get("equation", ""),
            "storeNumeric": "true" if field.get("storeNumeric", True) else "false",
            "defaultValue": field.get("defaultValue", ""),
            **self.get_readonly_props(field),
        }
