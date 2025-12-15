"""Tests for Form Grid pattern (Enterprise Edition)."""

from joget_form_generator.patterns.form_grid import FormGridPattern


def test_basic_form_grid():
    """Test basic form grid rendering."""
    pattern = FormGridPattern()
    field = {
        "id": "lineItems",
        "label": "Line Items",
        "type": "formGrid",
        "columns": [
            {"id": "product", "label": "Product", "type": "textField"},
            {"id": "quantity", "label": "Quantity", "type": "textField"},
        ],
    }

    result = pattern.render(field, {})

    assert result["className"] == "org.joget.plugin.enterprise.FormGrid"
    assert result["properties"]["id"] == "lineItems"
    assert result["properties"]["label"] == "Line Items"
    assert len(result["properties"]["columns"]) == 2
    assert result["properties"]["columns"][0]["id"] == "product"
    assert result["properties"]["columns"][0]["type"] == "textField"
    assert result["properties"]["columns"][0]["editable"] == "true"


def test_form_grid_with_form_reference():
    """Test form grid with formId reference."""
    pattern = FormGridPattern()
    field = {
        "id": "orders",
        "label": "Orders",
        "type": "formGrid",
        "formId": "orderLineItems",
        "columns": [
            {"id": "item", "label": "Item", "type": "textField"},
            {"id": "price", "label": "Price", "type": "textField"},
        ],
    }

    result = pattern.render(field, {})

    assert result["properties"]["formDefId"] == "orderLineItems"


def test_form_grid_with_select_column():
    """Test form grid with selectBox column including options."""
    pattern = FormGridPattern()
    field = {
        "id": "tasks",
        "label": "Tasks",
        "type": "formGrid",
        "columns": [
            {
                "id": "status",
                "label": "Status",
                "type": "selectBox",
                "options": [
                    {"value": "todo", "label": "To Do"},
                    {"value": "done", "label": "Done"},
                ],
            },
        ],
    }

    result = pattern.render(field, {})

    assert result["properties"]["columns"][0]["type"] == "selectBox"
    assert len(result["properties"]["columns"][0]["options"]) == 2
    assert result["properties"]["columns"][0]["options"][0]["value"] == "todo"


def test_form_grid_with_row_validation():
    """Test form grid with min/max row validation."""
    pattern = FormGridPattern()
    field = {
        "id": "items",
        "label": "Items",
        "type": "formGrid",
        "columns": [{"id": "name", "label": "Name", "type": "textField"}],
        "validateMinRow": 1,
        "validateMaxRow": 10,
    }

    result = pattern.render(field, {})

    assert result["properties"]["validateMinRow"] == "1"
    assert result["properties"]["validateMaxRow"] == "10"


def test_form_grid_readonly():
    """Test readonly form grid."""
    pattern = FormGridPattern()
    field = {
        "id": "readonly_grid",
        "label": "Read-only Grid",
        "type": "formGrid",
        "columns": [{"id": "col1", "label": "Column 1", "type": "textField"}],
        "readonly": True,
    }

    result = pattern.render(field, {})

    assert result["properties"]["readonly"] == "true"


def test_form_grid_with_disabled_buttons():
    """Test form grid with add/delete buttons disabled."""
    pattern = FormGridPattern()
    field = {
        "id": "fixed_grid",
        "label": "Fixed Grid",
        "type": "formGrid",
        "columns": [{"id": "col1", "label": "Column 1", "type": "textField"}],
        "allowAddRow": False,
        "allowDeleteRow": False,
    }

    result = pattern.render(field, {})

    assert result["properties"]["allowAddRow"] == "false"
    assert result["properties"]["allowDeleteRow"] == "false"


def test_form_grid_with_non_editable_column():
    """Test form grid with non-editable column."""
    pattern = FormGridPattern()
    field = {
        "id": "grid",
        "label": "Grid",
        "type": "formGrid",
        "columns": [
            {"id": "id", "label": "ID", "type": "textField", "editable": False},
            {"id": "name", "label": "Name", "type": "textField", "editable": True},
        ],
    }

    result = pattern.render(field, {})

    assert result["properties"]["columns"][0]["editable"] == "false"
    assert result["properties"]["columns"][1]["editable"] == "true"
