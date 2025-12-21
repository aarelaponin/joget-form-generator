"""Calculation Field pattern for Enterprise Edition."""

import re
from typing import Any, ClassVar
from .base import BasePattern
from .mixins import ReadOnlyMixin


class CalculationFieldPattern(BasePattern, ReadOnlyMixin):
    """Pattern for Joget Enterprise Calculation Field.

    Performs arithmetic computations on form field values.
    Available in Professional and Enterprise editions only.
    """

    template_name: ClassVar[str] = "calculation_field.j2"

    def _extract_variables(self, equation: str) -> list[dict[str, str]]:
        """
        Extract field variables from the equation.

        Joget requires a variables array where each referenced field is declared.
        Variables are referenced in the equation as {fieldId}.

        Args:
            equation: The calculation equation (e.g., "{totalBudget} * {reservePct}")

        Returns:
            List of variable definitions with variableName, fieldId, operation
        """
        # Find all {fieldId} references in the equation
        field_refs = re.findall(r"\{(\w+)\}", equation)

        # Remove duplicates while preserving order
        seen = set()
        unique_refs = []
        for ref in field_refs:
            if ref not in seen:
                seen.add(ref)
                unique_refs.append(ref)

        # Build variables array - each variable uses "sum" operation by default
        variables = []
        for field_id in unique_refs:
            variables.append(
                {
                    "variableName": field_id,
                    "fieldId": field_id,
                    "operation": "sum",
                }
            )

        return variables

    def _convert_equation(self, equation: str) -> str:
        """
        Convert equation from YAML format to Joget format.

        YAML uses {fieldId} syntax, Joget uses just fieldId (no braces).

        Args:
            equation: The equation in YAML format

        Returns:
            The equation in Joget format
        """
        # Remove braces from field references
        return re.sub(r"\{(\w+)\}", r"\1", equation)

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for Calculation Field template.

        Args:
            field: Field specification with properties:
                - id: Field ID
                - label: Field label
                - equation: Calculation equation/formula (e.g., "{field1} + {field2}")
                - storeNumeric: Whether to store as numeric (optional, default false)
                - readonly: Whether field is readonly (typically true)
                - numOfDecimal: Number of decimal places (optional, default 2)
                - style: Number style - "us" or "eu" (optional, default "us")
            context: Rendering context

        Returns:
            Template context dictionary
        """
        equation = field.get("equation", "")
        variables = self._extract_variables(equation)
        joget_equation = self._convert_equation(equation)

        return {
            "id": field["id"],
            "label": field["label"],
            "equation": joget_equation,
            "variables": variables,
            "storeNumeric": "true" if field.get("storeNumeric", False) else "",
            "numOfDecimal": str(field.get("numOfDecimal", 2)),
            "style": field.get("style", "us"),
            **self.get_readonly_props(field),
        }
