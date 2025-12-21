"""Unit tests for FileUploadPattern."""

import pytest
from joget_form_generator.patterns.file_upload import FileUploadPattern


@pytest.fixture
def pattern():
    """Fixture providing FileUploadPattern instance."""
    return FileUploadPattern()


def test_basic_file_upload(pattern):
    """Test basic file upload rendering."""
    field = {
        "id": "resume",
        "label": "Resume",
        "type": "fileUpload",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.FileUpload"
    assert result["properties"]["id"] == "resume"
    assert result["properties"]["label"] == "Resume"


def test_file_upload_with_max_size(pattern):
    """Test file upload with max size limit.

    Note: maxSize is passed as-is (in MB), not converted to bytes.
    """
    field = {
        "id": "document",
        "label": "Document",
        "type": "fileUpload",
        "maxSize": 5,  # 5 MB
    }
    context = {}

    result = pattern.render(field, context)

    # maxSize is passed through as string
    assert result["properties"]["maxSize"] == "5"


def test_file_upload_with_file_types(pattern):
    """Test file upload with file type restrictions."""
    field = {
        "id": "photo",
        "label": "Photo",
        "type": "fileUpload",
        "fileTypes": "*.jpg,*.png,*.gif",
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["fileType"] == "*.jpg,*.png,*.gif"


def test_file_upload_default_settings(pattern):
    """Test file upload uses default settings from normalizer."""
    field = {
        "id": "attachment",
        "label": "Attachment",
        "type": "fileUpload",
    }
    context = {}

    result = pattern.render(field, context)

    # Should have maxSize and fileType (defaults: 10, *)
    assert "maxSize" in result["properties"]
    assert "fileType" in result["properties"]


def test_required_file_upload(pattern):
    """Test required file upload with validation.

    Note: Joget uses validator with mandatory, not a required property.
    """
    field = {
        "id": "proofOfId",
        "label": "Proof of ID",
        "type": "fileUpload",
        "required": True,
    }
    context = {}

    result = pattern.render(field, context)

    # FileUpload uses validator with mandatory for required
    validator = result["properties"]["validator"]
    assert validator["className"] == "org.joget.apps.form.lib.DefaultValidator"
    assert validator["properties"]["mandatory"] == "true"


def test_file_upload_pdf_only(pattern):
    """Test file upload restricted to PDF files.

    Note: maxSize is passed as-is (in MB), not converted to bytes.
    """
    field = {
        "id": "pdfDocument",
        "label": "PDF Document",
        "type": "fileUpload",
        "fileTypes": "*.pdf",
        "maxSize": 20,
    }
    context = {}

    result = pattern.render(field, context)

    assert result["properties"]["fileType"] == "*.pdf"
    # maxSize is passed through as string
    assert result["properties"]["maxSize"] == "20"
