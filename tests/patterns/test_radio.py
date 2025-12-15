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
    """Test radio button options rendering."""
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

    options_binder = result["properties"]["optionsBinder"]
    assert options_binder["className"] == "org.joget.apps.form.lib.FormOptionsBinder"
    assert len(options_binder["properties"]["options"]) == 3
    assert options_binder["properties"]["options"][2]["value"] == "pending"


def test_required_radio(pattern):
    """Test required radio button with validation."""
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

    # Radio outputs required as string property, not validator
    assert result["properties"]["required"] == "true"
