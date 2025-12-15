"""Unit tests for HiddenFieldPattern."""

import pytest
from joget_form_generator.patterns.hidden_field import HiddenFieldPattern


@pytest.fixture
def pattern():
    """Fixture providing HiddenFieldPattern instance."""
    return HiddenFieldPattern()


def test_basic_hidden_field(pattern):
    """Test basic hidden field rendering."""
    field = {
        "id": "recordId",
        "label": "Record ID",
        "type": "hiddenField",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.HiddenField"
    assert result["properties"]["id"] == "recordId"
    # HiddenField doesn't output label property in Joget JSON


def test_hidden_field_with_default_value(pattern):
    """Test hidden field with default value."""
    field = {
        "id": "formVersion",
        "label": "Form Version",
        "type": "hiddenField",
        "defaultValue": "v2.0",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["value"] == "v2.0"


def test_hidden_field_empty_value(pattern):
    """Test hidden field with no default value."""
    field = {
        "id": "tempField",
        "label": "Temporary Field",
        "type": "hiddenField",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["value"] == ""
