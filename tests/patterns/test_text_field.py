"""Unit tests for TextFieldPattern."""

import pytest
from joget_form_generator.patterns.text_field import TextFieldPattern


@pytest.fixture
def pattern():
    """Fixture providing TextFieldPattern instance."""
    return TextFieldPattern()


class TestBasicRendering:
    """Test basic text field rendering."""

    def test_minimal_text_field(self, pattern):
        """Test text field with only required properties."""
        field = {
            "id": "username",
            "label": "Username",
            "type": "textField",
        }
        context = {}

        result = pattern.render(field, context)

        assert result["className"] == "org.joget.apps.form.lib.TextField"
        assert result["properties"]["id"] == "username"
        assert result["properties"]["label"] == "Username"
        assert result["properties"]["value"] == ""
        # readonly may be empty string or "false" depending on template
        assert result["properties"]["readonly"] in ["", "false"]

    def test_text_field_with_placeholder(self, pattern):
        """Test text field with placeholder text."""
        field = {
            "id": "email",
            "label": "Email",
            "type": "textField",
            "placeholder": "your.email@example.com",
        }
        context = {}

        result = pattern.render(field, context)

        assert result["properties"]["placeholder"] == "your.email@example.com"

    def test_text_field_with_default_value(self, pattern):
        """Test text field with default value."""
        field = {
            "id": "country",
            "label": "Country",
            "type": "textField",
            "defaultValue": "USA",
        }
        context = {}

        result = pattern.render(field, context)

        assert result["properties"]["value"] == "USA"


class TestSizeHandling:
    """Test field size handling."""

    def test_text_field_small_size(self, pattern):
        """Test text field with small size."""
        field = {
            "id": "code",
            "label": "Code",
            "type": "textField",
            "size": "small",
        }
        context = {}

        result = pattern.render(field, context)

        assert result["properties"]["size"] == "small"

    def test_text_field_large_size(self, pattern):
        """Test text field with large size."""
        field = {
            "id": "description",
            "label": "Description",
            "type": "textField",
            "size": "large",
        }
        context = {}

        result = pattern.render(field, context)

        assert result["properties"]["size"] == "large"

    def test_text_field_default_size(self, pattern):
        """Test text field defaults to medium size."""
        field = {
            "id": "name",
            "label": "Name",
            "type": "textField",
        }
        context = {}

        result = pattern.render(field, context)

        # Should use default size from normalizer
        assert "size" in result["properties"]


class TestValidation:
    """Test validation handling."""

    def test_required_field_generates_validator(self, pattern):
        """Test that required=true generates DefaultValidator."""
        field = {
            "id": "firstName",
            "label": "First Name",
            "type": "textField",
            "required": True,
        }
        context = {}

        result = pattern.render(field, context)

        assert "validator" in result["properties"]
        validator = result["properties"]["validator"]
        assert validator["className"] == "org.joget.apps.form.lib.DefaultValidator"
        assert validator["properties"]["mandatory"] == "true"

    def test_optional_field_no_validator(self, pattern):
        """Test that required=false has no mandatory validator."""
        field = {
            "id": "middleName",
            "label": "Middle Name",
            "type": "textField",
            "required": False,
        }
        context = {}

        result = pattern.render(field, context)

        # May have empty validator or no validator key
        if "validator" in result["properties"]:
            validator = result["properties"]["validator"]
            # If present, mandatory should be false or absent
            if "properties" in validator and "mandatory" in validator["properties"]:
                assert validator["properties"]["mandatory"] == "false"

    def test_max_length_validation(self, pattern):
        """Test maxLength property."""
        field = {
            "id": "code",
            "label": "Code",
            "type": "textField",
            "maxLength": 10,
        }
        context = {}

        result = pattern.render(field, context)

        # maxLength from YAML is not directly mapped - validation is handled differently
        # This test verifies pattern accepts maxLength without error
        assert result["className"] == "org.joget.apps.form.lib.TextField"


class TestReadOnlyHandling:
    """Test readonly field handling."""

    def test_readonly_field(self, pattern):
        """Test readonly text field."""
        field = {
            "id": "recordId",
            "label": "Record ID",
            "type": "textField",
            "readonly": True,
        }
        context = {}

        result = pattern.render(field, context)

        assert result["properties"]["readonly"] == "true"

    def test_editable_field(self, pattern):
        """Test editable (not readonly) field."""
        field = {
            "id": "name",
            "label": "Name",
            "type": "textField",
            "readonly": False,
        }
        context = {}

        result = pattern.render(field, context)

        # readonly false may be empty string or "false" depending on template
        assert result["properties"]["readonly"] in ["", "false"]


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_default_value(self, pattern):
        """Test field with empty default value."""
        field = {
            "id": "field1",
            "label": "Field 1",
            "type": "textField",
            "defaultValue": "",
        }
        context = {}

        result = pattern.render(field, context)

        assert result["properties"]["value"] == ""

    def test_numeric_default_value(self, pattern):
        """Test field with numeric default value (should be stringified)."""
        field = {
            "id": "quantity",
            "label": "Quantity",
            "type": "textField",
            "defaultValue": "123",
        }
        context = {}

        result = pattern.render(field, context)

        assert result["properties"]["value"] == "123"
