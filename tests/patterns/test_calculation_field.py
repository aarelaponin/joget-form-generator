"""Tests for Calculation Field pattern (Enterprise Edition)."""

from joget_form_generator.patterns.calculation_field import CalculationFieldPattern


def test_basic_calculation_field():
    """Test basic calculation field rendering.

    Note: storeNumeric defaults to False (empty string in Joget).
    """
    pattern = CalculationFieldPattern()
    field = {
        "id": "totalCost",
        "label": "Total Cost",
        "type": "calculationField",
        "equation": "fieldA + fieldB",
    }

    result = pattern.render(field, {})

    assert result["className"] == "org.joget.plugin.enterprise.CalculationField"
    assert result["properties"]["id"] == "totalCost"
    assert result["properties"]["label"] == "Total Cost"
    assert result["properties"]["equation"] == "fieldA + fieldB"
    assert result["properties"]["storeNumeric"] == ""  # default is false (empty string)
    assert result["properties"]["readonly"] == ""  # not set in field


def test_calculation_field_with_custom_formula():
    """Test calculation field with complex formula."""
    pattern = CalculationFieldPattern()
    field = {
        "id": "discount",
        "label": "Discount Amount",
        "type": "calculationField",
        "equation": "(price * quantity) * 0.15",
        "storeNumeric": True,
        "readonly": True,
    }

    result = pattern.render(field, {})

    assert result["properties"]["equation"] == "(price * quantity) * 0.15"
    assert result["properties"]["storeNumeric"] == "true"


def test_calculation_field_with_default_value():
    """Test calculation field with default/fallback value.

    Note: Calculation fields have empty value by default.
    Required is not typically used with calculation fields.
    """
    pattern = CalculationFieldPattern()
    field = {
        "id": "tax",
        "label": "Tax",
        "type": "calculationField",
        "equation": "total * 0.21",
        "storeNumeric": True,
    }

    result = pattern.render(field, {})

    # Calculation field value is always empty (computed at runtime)
    assert result["properties"]["value"] == ""
    assert result["properties"]["storeNumeric"] == "true"


def test_calculation_field_store_as_string():
    """Test calculation field storing result as string.

    Note: Joget uses empty string for false values.
    """
    pattern = CalculationFieldPattern()
    field = {
        "id": "result",
        "label": "Result",
        "type": "calculationField",
        "equation": "value1 + value2",
        "storeNumeric": False,
    }

    result = pattern.render(field, {})

    # Joget uses empty string for false
    assert result["properties"]["storeNumeric"] == ""
