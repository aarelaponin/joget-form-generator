"""Unit tests for SelectBoxPattern."""

import pytest
from joget_form_generator.patterns.select_box import SelectBoxPattern


@pytest.fixture
def pattern():
    """Fixture providing SelectBoxPattern instance."""
    return SelectBoxPattern()


def test_select_box_with_static_options(pattern):
    """Test select box with static options.

    Note: Joget uses options array directly, not optionsBinder for static options.
    """
    field = {
        "id": "status",
        "label": "Status",
        "type": "selectBox",
        "options": [
            {"value": "active", "label": "Active"},
            {"value": "inactive", "label": "Inactive"},
        ],
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.SelectBox"
    # Static options are in options array
    assert len(result["properties"]["options"]) == 2
    assert result["properties"]["options"][0]["value"] == "active"
    # optionsBinder should be empty for static options
    binder = result["properties"]["optionsBinder"]
    assert binder["className"] == ""


def test_select_box_with_nested_lov(pattern):
    """Test select box with nested LOV (formData source)."""
    field = {
        "id": "equipment_category",
        "label": "Equipment Category",
        "type": "selectBox",
        "optionsSource": {
            "type": "formData",
            "formId": "md25equipCategory",
            "valueColumn": "code",
            "labelColumn": "name",
        },
    }
    context = {}

    result = pattern.render(field, context)

    binder = result["properties"]["optionsBinder"]
    assert binder["className"] == "org.joget.apps.form.lib.FormOptionsBinder"
    assert binder["properties"]["formDefId"] == "md25equipCategory"
    assert binder["properties"]["idColumn"] == "code"
    assert binder["properties"]["labelColumn"] == "name"


def test_select_box_multiple(pattern):
    """Test multi-select box."""
    field = {
        "id": "skills",
        "label": "Skills",
        "type": "selectBox",
        "multiple": True,
        "options": [
            {"value": "python", "label": "Python"},
            {"value": "java", "label": "Java"},
        ],
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["multiple"] == "true"
