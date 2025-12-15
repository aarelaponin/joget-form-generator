"""Unit tests for CheckBoxPattern."""

import pytest
from joget_form_generator.patterns.check_box import CheckBoxPattern


@pytest.fixture
def pattern():
    """Fixture providing CheckBoxPattern instance."""
    return CheckBoxPattern()


def test_basic_check_box(pattern):
    """Test basic checkbox rendering."""
    field = {
        "id": "interests",
        "label": "Interests",
        "type": "checkBox",
        "options": [
            {"value": "sports", "label": "Sports"},
            {"value": "music", "label": "Music"},
        ],
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.CheckBox"
    assert result["properties"]["id"] == "interests"
    assert result["properties"]["label"] == "Interests"


def test_check_box_with_options(pattern):
    """Test checkbox options rendering."""
    field = {
        "id": "hobbies",
        "label": "Hobbies",
        "type": "checkBox",
        "options": [
            {"value": "reading", "label": "Reading"},
            {"value": "gaming", "label": "Gaming"},
            {"value": "cooking", "label": "Cooking"},
        ],
    }
    context = {}

    result = pattern.render(field, context)

    options_binder = result["properties"]["optionsBinder"]
    assert options_binder["className"] == "org.joget.apps.form.lib.FormOptionsBinder"
    assert len(options_binder["properties"]["options"]) == 3
    assert options_binder["properties"]["options"][0]["value"] == "reading"
    assert options_binder["properties"]["options"][1]["label"] == "Gaming"


def test_required_check_box(pattern):
    """Test required checkbox with validation."""
    field = {
        "id": "terms",
        "label": "Terms",
        "type": "checkBox",
        "required": True,
        "options": [
            {"value": "accepted", "label": "I accept the terms"},
        ],
    }
    context = {}

    result = pattern.render(field, context)

    # CheckBox outputs required as string property, not validator
    assert result["properties"]["required"] == "true"
