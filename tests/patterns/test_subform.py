"""Unit tests for SubformPattern."""

import pytest
from joget_form_generator.patterns.subform import SubformPattern


@pytest.fixture
def pattern():
    """Fixture providing SubformPattern instance."""
    return SubformPattern()


def test_basic_subform(pattern):
    """Test basic subform rendering."""
    field = {
        "id": "intendedCrops",
        "label": "Intended Crops for This Season",
        "type": "subform",
        "formId": "intendedCropsGrid",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.SubForm"
    assert result["properties"]["id"] == "intendedCrops"
    assert result["properties"]["label"] == "Intended Crops for This Season"
    assert result["properties"]["formDefId"] == "intendedCropsGrid"
    assert result["properties"]["readonly"] == ""
    assert result["properties"]["readonlyLabel"] == ""


def test_subform_with_custom_button_labels(pattern):
    """Test subform with custom button labels."""
    field = {
        "id": "equipmentRequests",
        "label": "Equipment Requests",
        "type": "subform",
        "formId": "equipmentRequestsGrid",
        "addButtonLabel": "Add Equipment",
        "deleteButtonLabel": "Remove",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["addButtonLabel"] == "Add Equipment"
    assert result["properties"]["deleteButtonLabel"] == "Remove"


def test_subform_readonly(pattern):
    """Test readonly subform."""
    field = {
        "id": "readonlyData",
        "label": "Read-Only Data",
        "type": "subform",
        "formId": "dataGrid",
        "readonly": True,
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["readonly"] == "true"


def test_subform_with_hidden_buttons(pattern):
    """Test subform with hidden add/delete buttons."""
    field = {
        "id": "fixedData",
        "label": "Fixed Data",
        "type": "subform",
        "formId": "fixedDataGrid",
        "noAddButton": True,
        "noDeleteButton": True,
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["noAddButton"] == "true"
    assert result["properties"]["noDeleteButton"] == "true"


def test_required_subform(pattern):
    """Test required subform with validator."""
    field = {
        "id": "inputRequests",
        "label": "Input Requests",
        "type": "subform",
        "formId": "inputRequestsGrid",
        "required": True,
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["validator"]["className"] == "org.joget.apps.form.lib.DefaultValidator"
    assert result["properties"]["validator"]["properties"]["mandatory"] == "true"
    assert "Input Requests is required" in result["properties"]["validator"]["properties"]["message"]


def test_subform_with_workflow_variable(pattern):
    """Test subform with workflow variable binding."""
    field = {
        "id": "approvalData",
        "label": "Approval Data",
        "type": "subform",
        "formId": "approvalGrid",
        "workflowVariable": "wf_approval_data",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["workflowVariable"] == "wf_approval_data"


def test_subform_default_button_labels(pattern):
    """Test subform uses default button labels."""
    field = {
        "id": "defaultButtons",
        "label": "Default Buttons",
        "type": "subform",
        "formId": "defaultGrid",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["addButtonLabel"] == "Add"
    assert result["properties"]["deleteButtonLabel"] == "Delete"


def test_subform_readonly_label(pattern):
    """Test subform with readonly label."""
    field = {
        "id": "readonlyLabelData",
        "label": "Readonly Label Data",
        "type": "subform",
        "formId": "dataGrid",
        "readonlyLabel": True,
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["readonlyLabel"] == "true"
