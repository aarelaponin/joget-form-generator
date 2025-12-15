"""Unit tests for TextAreaPattern."""

import pytest
from joget_form_generator.patterns.text_area import TextAreaPattern


@pytest.fixture
def pattern():
    """Fixture providing TextAreaPattern instance."""
    return TextAreaPattern()


def test_basic_text_area(pattern):
    """Test basic text area rendering."""
    field = {
        "id": "description",
        "label": "Description",
        "type": "textArea",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.TextArea"
    assert result["properties"]["id"] == "description"
    assert result["properties"]["label"] == "Description"


def test_text_area_with_rows_cols(pattern):
    """Test text area with custom rows and columns."""
    field = {
        "id": "comments",
        "label": "Comments",
        "type": "textArea",
        "rows": 10,
        "cols": 80,
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["rows"] == "10"
    assert result["properties"]["cols"] == "80"


def test_text_area_default_dimensions(pattern):
    """Test text area uses default rows/cols from normalizer."""
    field = {
        "id": "notes",
        "label": "Notes",
        "type": "textArea",
    }
    context = {}

    result = pattern.render(field, context)

    # Should have rows and cols (defaults: 5, 50)
    assert "rows" in result["properties"]
    assert "cols" in result["properties"]


def test_required_text_area(pattern):
    """Test required text area with validation."""
    field = {
        "id": "feedback",
        "label": "Feedback",
        "type": "textArea",
        "required": True,
    }
    context = {}

    result = pattern.render(field, context)

    assert "validator" in result["properties"]
    validator = result["properties"]["validator"]
    assert validator["properties"]["mandatory"] == "true"


def test_text_area_with_placeholder(pattern):
    """Test text area with placeholder text."""
    field = {
        "id": "bio",
        "label": "Bio",
        "type": "textArea",
        "placeholder": "Tell us about yourself",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["placeholder"] == "Tell us about yourself"
