"""Unit tests for SelectBoxPattern."""

import pytest
from joget_form_generator.patterns.select_box import SelectBoxPattern


@pytest.fixture
def pattern():
    """Fixture providing SelectBoxPattern instance."""
    return SelectBoxPattern()


def test_select_box_with_static_options(pattern):
    """Test select box with static options."""
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
    binder = result["properties"]["optionsBinder"]
    assert binder["className"] == "org.joget.apps.form.lib.FormOptionsBinder"
    assert len(binder["properties"]["options"]) == 2
    assert binder["properties"]["options"][0]["value"] == "active"


def test_select_box_with_cascading_dropdown(pattern):
    """Test select box with cascading dropdown (formData source)."""
    field = {
        "id": "equipment",
        "label": "Equipment",
        "type": "selectBox",
        "optionsSource": {
            "type": "formData",
            "formId": "md25equipment",
            "parentField": "equipmentCategory",
            "filterField": "equipment_category",
        },
    }
    context = {}

    result = pattern.render(field, context)

    binder = result["properties"]["optionsBinder"]
    assert binder["className"] == "org.joget.apps.form.model.FormLoadBinder"
    assert binder["properties"]["formDefId"] == "md25equipment"
    assert binder["properties"]["parentFieldId"] == "equipmentCategory"
    assert binder["properties"]["filterField"] == "equipment_category"


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
