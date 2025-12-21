"""Unit tests for RadioPattern."""

import pytest
from joget_form_generator.patterns.radio import RadioPattern


@pytest.fixture
def pattern():
    """Fixture providing RadioPattern instance."""
    return RadioPattern()


def test_basic_radio(pattern):
    """Test basic radio button rendering."""
    field = {
        "id": "gender",
        "label": "Gender",
        "type": "radio",
        "options": [
            {"value": "male", "label": "Male"},
            {"value": "female", "label": "Female"},
        ],
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.Radio"
    assert result["properties"]["id"] == "gender"
    assert result["properties"]["label"] == "Gender"


def test_radio_with_options(pattern):
    """Test radio button options rendering.

    Note: Joget uses options array directly, not optionsBinder for static options.
    """
    field = {
        "id": "status",
        "label": "Status",
        "type": "radio",
        "options": [
            {"value": "active", "label": "Active"},
            {"value": "inactive", "label": "Inactive"},
            {"value": "pending", "label": "Pending"},
        ],
    }
    context = {}

    result = pattern.render(field, context)

    # Static options are in options array
    assert len(result["properties"]["options"]) == 3
    assert result["properties"]["options"][2]["value"] == "pending"
    # optionsBinder should be empty for static options
    options_binder = result["properties"]["optionsBinder"]
    assert options_binder["className"] == ""


def test_required_radio(pattern):
    """Test required radio button with validation.

    Note: Joget uses validator with mandatory, not a required property.
    """
    field = {
        "id": "priority",
        "label": "Priority",
        "type": "radio",
        "required": True,
        "options": [
            {"value": "high", "label": "High"},
            {"value": "medium", "label": "Medium"},
            {"value": "low", "label": "Low"},
        ],
    }
    context = {}

    result = pattern.render(field, context)

    # Radio uses validator with mandatory for required
    validator = result["properties"]["validator"]
    assert validator["className"] == "org.joget.apps.form.lib.DefaultValidator"
    assert validator["properties"]["mandatory"] == "true"
