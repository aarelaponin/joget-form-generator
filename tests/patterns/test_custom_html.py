"""Unit tests for CustomHTMLPattern."""

import pytest
from joget_form_generator.patterns.custom_html import CustomHTMLPattern


@pytest.fixture
def pattern():
    """Fixture providing CustomHTMLPattern instance."""
    return CustomHTMLPattern()


def test_basic_custom_html(pattern):
    """Test basic custom HTML rendering."""
    field = {
        "id": "banner",
        "label": "Banner",
        "type": "customHTML",
        "html": "<div class='banner'>Welcome to our form!</div>",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.CustomHTML"
    assert result["properties"]["id"] == "banner"
    assert result["properties"]["label"] == "Banner"
    assert "<div class='banner'>Welcome to our form!</div>" in result["properties"]["value"]


def test_custom_html_with_complex_content(pattern):
    """Test custom HTML with complex HTML content."""
    html_content = """
    <div class='info-box'>
        <h3>Important Information</h3>
        <p>Please read carefully before proceeding.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
    </div>
    """
    field = {
        "id": "infoBox",
        "label": "Information Box",
        "type": "customHTML",
        "html": html_content,
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.CustomHTML"
    assert "Important Information" in result["properties"]["value"]
    assert "Item 1" in result["properties"]["value"]


def test_custom_html_empty_content(pattern):
    """Test custom HTML with empty content."""
    field = {
        "id": "spacer",
        "label": "Spacer",
        "type": "customHTML",
        "html": "",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.CustomHTML"
    assert result["properties"]["value"] == ""


def test_custom_html_with_script(pattern):
    """Test custom HTML with JavaScript."""
    field = {
        "id": "calculator",
        "label": "Calculator",
        "type": "customHTML",
        "html": "<script>function calculate() { return 2 + 2; }</script>",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.CustomHTML"
    assert "function calculate" in result["properties"]["value"]
