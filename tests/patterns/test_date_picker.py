"""Unit tests for DatePickerPattern."""

import pytest
from joget_form_generator.patterns.date_picker import DatePickerPattern


@pytest.fixture
def pattern():
    """Fixture providing DatePickerPattern instance."""
    return DatePickerPattern()


def test_basic_date_picker(pattern):
    """Test basic date picker rendering."""
    field = {
        "id": "birthDate",
        "label": "Date of Birth",
        "type": "datePicker",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.DatePicker"
    assert result["properties"]["id"] == "birthDate"
    assert result["properties"]["label"] == "Date of Birth"


def test_date_picker_with_format(pattern):
    """Test date picker with custom date format."""
    field = {
        "id": "eventDate",
        "label": "Event Date",
        "type": "datePicker",
        "dateFormat": "dd/MM/yyyy",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["format"] == "dd/MM/yyyy"


def test_date_picker_default_format(pattern):
    """Test date picker uses default format from normalizer."""
    field = {
        "id": "appointmentDate",
        "label": "Appointment Date",
        "type": "datePicker",
    }
    context = {}

    result = pattern.render(field, context)

    # Should have format property (default: yyyy-MM-dd)
    assert "format" in result["properties"]


def test_required_date_picker(pattern):
    """Test required date picker with validation."""
    field = {
        "id": "registrationDate",
        "label": "Registration Date",
        "type": "datePicker",
        "required": True,
    }
    context = {}

    result = pattern.render(field, context)

    assert "validator" in result["properties"]
    validator = result["properties"]["validator"]
    assert validator["properties"]["mandatory"] == "true"


def test_date_picker_with_default_value(pattern):
    """Test date picker with default value."""
    field = {
        "id": "startDate",
        "label": "Start Date",
        "type": "datePicker",
        "defaultValue": "2025-01-01",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["value"] == "2025-01-01"
