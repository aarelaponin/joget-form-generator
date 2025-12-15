"""Unit tests for GridPattern."""

import pytest
from joget_form_generator.patterns.grid import GridPattern


@pytest.fixture
def pattern():
    """Fixture providing GridPattern instance."""
    return GridPattern()


def test_basic_grid(pattern):
    """Test basic grid rendering with columns."""
    field = {
        "id": "productGrid",
        "label": "Product List",
        "type": "grid",
        "columns": [
            {"id": "productCode", "label": "Product Code"},
            {"id": "productName", "label": "Product Name"},
            {"id": "quantity", "label": "Quantity"},
        ],
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.Grid"
    assert result["properties"]["id"] == "productGrid"
    assert result["properties"]["label"] == "Product List"
    assert len(result["properties"]["options"]) == 3
    assert result["properties"]["options"][0] == {"value": "productCode", "label": "Product Code"}
    assert result["properties"]["options"][1] == {"value": "productName", "label": "Product Name"}
    assert result["properties"]["options"][2] == {"value": "quantity", "label": "Quantity"}
    assert result["properties"]["readonly"] == ""


def test_grid_readonly(pattern):
    """Test readonly grid."""
    field = {
        "id": "readonlyGrid",
        "label": "Read-Only Grid",
        "type": "grid",
        "columns": [
            {"id": "field1", "label": "Field 1"},
        ],
        "readonly": True,
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["readonly"] == "true"


def test_grid_with_row_validation(pattern):
    """Test grid with min/max row validation."""
    field = {
        "id": "validatedGrid",
        "label": "Validated Grid",
        "type": "grid",
        "columns": [
            {"id": "item", "label": "Item"},
        ],
        "validateMinRow": 2,
        "validateMaxRow": 10,
        "errorMessage": "Please enter between 2 and 10 rows",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["validateMinRow"] == "2"
    assert result["properties"]["validateMaxRow"] == "10"
    assert result["properties"]["errorMessage"] == "Please enter between 2 and 10 rows"


def test_grid_empty_columns(pattern):
    """Test grid with no columns."""
    field = {
        "id": "emptyGrid",
        "label": "Empty Grid",
        "type": "grid",
        "columns": [],
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["options"] == []


def test_grid_single_column(pattern):
    """Test grid with single column."""
    field = {
        "id": "singleColGrid",
        "label": "Single Column Grid",
        "type": "grid",
        "columns": [
            {"id": "notes", "label": "Notes"},
        ],
    }
    context = {}

    result = pattern.render(field, context)

    assert len(result["properties"]["options"]) == 1
    assert result["properties"]["options"][0] == {"value": "notes", "label": "Notes"}


def test_grid_with_many_columns(pattern):
    """Test grid with many columns."""
    field = {
        "id": "wideGrid",
        "label": "Wide Grid",
        "type": "grid",
        "columns": [
            {"id": "col1", "label": "Column 1"},
            {"id": "col2", "label": "Column 2"},
            {"id": "col3", "label": "Column 3"},
            {"id": "col4", "label": "Column 4"},
            {"id": "col5", "label": "Column 5"},
        ],
    }
    context = {}

    result = pattern.render(field, context)

    assert len(result["properties"]["options"]) == 5
    assert result["properties"]["options"][4] == {"value": "col5", "label": "Column 5"}


def test_grid_min_row_only(pattern):
    """Test grid with only minimum row validation."""
    field = {
        "id": "minOnlyGrid",
        "label": "Min Only Grid",
        "type": "grid",
        "columns": [{"id": "data", "label": "Data"}],
        "validateMinRow": 1,
        "errorMessage": "At least one row required",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["validateMinRow"] == "1"
    assert result["properties"]["validateMaxRow"] == ""
    assert result["properties"]["errorMessage"] == "At least one row required"


def test_grid_default_validation_values(pattern):
    """Test grid uses empty strings for unset validation."""
    field = {
        "id": "defaultGrid",
        "label": "Default Grid",
        "type": "grid",
        "columns": [{"id": "field", "label": "Field"}],
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["validateMinRow"] == ""
    assert result["properties"]["validateMaxRow"] == ""
    assert result["properties"]["errorMessage"] == ""
