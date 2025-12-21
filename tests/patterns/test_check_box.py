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
    """Test checkbox options rendering.

    Note: Joget uses options array directly, not optionsBinder for static options.
    """
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

    # Static options are in options array, optionsBinder is empty
    assert len(result["properties"]["options"]) == 3
    assert result["properties"]["options"][0]["value"] == "reading"
    assert result["properties"]["options"][1]["label"] == "Gaming"
    # optionsBinder should be empty for static options
    options_binder = result["properties"]["optionsBinder"]
    assert options_binder["className"] == ""


def test_required_check_box(pattern):
    """Test required checkbox with validation.

    Note: Joget uses validator with mandatory, not a required property.
    """
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

    # CheckBox uses validator with mandatory for required
    validator = result["properties"]["validator"]
    assert validator["className"] == "org.joget.apps.form.lib.DefaultValidator"
    assert validator["properties"]["mandatory"] == "true"
