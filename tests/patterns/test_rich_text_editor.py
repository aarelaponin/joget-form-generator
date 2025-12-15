"""Tests for Rich Text Editor pattern (Enterprise Edition)."""

from joget_form_generator.patterns.rich_text_editor import RichTextEditorPattern


def test_basic_rich_text_editor():
    """Test basic rich text editor rendering."""
    pattern = RichTextEditorPattern()
    field = {
        "id": "description",
        "label": "Description",
        "type": "richTextEditor",
    }

    result = pattern.render(field, {})
    

    assert result["className"] == "org.joget.plugin.enterprise.RichTextEditor"
    assert result["properties"]["id"] == "description"
    assert result["properties"]["label"] == "Description"
    assert result["properties"]["editor"] == "tinymce"  # default
    assert result["properties"]["rows"] == "10"  # default
    assert result["properties"]["readonly"] == ""


def test_rich_text_editor_with_quill():
    """Test rich text editor with Quill editor."""
    pattern = RichTextEditorPattern()
    field = {
        "id": "content",
        "label": "Content",
        "type": "richTextEditor",
        "editor": "quill",
    }

    result = pattern.render(field, {})
    

    assert result["properties"]["editor"] == "quill"


def test_rich_text_editor_with_default_value():
    """Test rich text editor with default HTML content."""
    pattern = RichTextEditorPattern()
    field = {
        "id": "template",
        "label": "Email Template",
        "type": "richTextEditor",
        "defaultValue": "<p>Hello <strong>World</strong>!</p>",
    }

    result = pattern.render(field, {})
    

    assert result["properties"]["value"] == "<p>Hello <strong>World</strong>!</p>"


def test_rich_text_editor_with_custom_height():
    """Test rich text editor with custom height."""
    pattern = RichTextEditorPattern()
    field = {
        "id": "article",
        "label": "Article",
        "type": "richTextEditor",
        "rows": 20,
    }

    result = pattern.render(field, {})
    

    assert result["properties"]["rows"] == "20"


def test_rich_text_editor_with_placeholder():
    """Test rich text editor with placeholder text."""
    pattern = RichTextEditorPattern()
    field = {
        "id": "notes",
        "label": "Notes",
        "type": "richTextEditor",
        "placeholder": "Enter your notes here...",
        "required": True,
    }

    result = pattern.render(field, {})
    

    assert result["properties"]["placeholder"] == "Enter your notes here..."
    assert result["properties"]["required"] == "true"


def test_rich_text_editor_readonly():
    """Test readonly rich text editor."""
    pattern = RichTextEditorPattern()
    field = {
        "id": "readonly_content",
        "label": "Read-only Content",
        "type": "richTextEditor",
        "readonly": True,
    }

    result = pattern.render(field, {})
    

    assert result["properties"]["readonly"] == "true"
