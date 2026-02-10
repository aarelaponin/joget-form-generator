"""Tests for Concat Field pattern (GovStack plugin)."""

import json
import pytest
from joget_form_generator.patterns.concat_field import ConcatFieldPattern


class TestConcatFieldPattern:
    """Test suite for ConcatFieldPattern."""

    @pytest.fixture
    def pattern(self):
        """Create pattern instance for testing."""
        return ConcatFieldPattern()

    @pytest.fixture
    def basic_field(self):
        """Basic concat field specification."""
        return {
            "id": "personal_information",
            "label": "Personal Information",
            "type": "concatField",
            "sourceFields": [
                {"fieldId": "national_id"},
                {"fieldId": "first_name"},
                {"fieldId": "last_name"},
            ],
            "separator": "_",
        }

    @pytest.fixture
    def context(self):
        """Standard rendering context."""
        return {"form": {"id": "farmerForm", "name": "Farmer Form", "tableName": "farmerForm"}}

    def test_render_correct_classname(self, pattern, basic_field, context):
        """Test that output uses correct GovStack Concat Field className."""
        result = pattern.render(basic_field, context)

        assert result["className"] == "global.govstack.concatfield.element.ConcatFieldElement"
        assert result["properties"]["id"] == "personal_information"

    def test_source_fields(self, pattern, basic_field, context):
        """Test source fields are correctly rendered."""
        result = pattern.render(basic_field, context)

        source_fields = result["properties"]["sourceFields"]
        assert len(source_fields) == 3
        assert source_fields[0]["fieldId"] == "national_id"
        assert source_fields[1]["fieldId"] == "first_name"
        assert source_fields[2]["fieldId"] == "last_name"

    def test_separator(self, pattern, basic_field, context):
        """Test separator property."""
        result = pattern.render(basic_field, context)

        assert result["properties"]["separator"] == "_"

    def test_custom_separator(self, pattern, context):
        """Test custom separator."""
        field = {
            "id": "concat",
            "type": "concatField",
            "sourceFields": [{"fieldId": "a"}, {"fieldId": "b"}],
            "separator": " - ",
        }
        result = pattern.render(field, context)

        assert result["properties"]["separator"] == " - "

    def test_prefix_suffix(self, pattern, context):
        """Test prefix and suffix properties."""
        field = {
            "id": "concat",
            "type": "concatField",
            "sourceFields": [{"fieldId": "code"}],
            "prefix": "ID-",
            "suffix": "-001",
        }
        result = pattern.render(field, context)

        assert result["properties"]["prefix"] == "ID-"
        assert result["properties"]["suffix"] == "-001"

    def test_skip_empty(self, pattern, context):
        """Test skipEmpty property."""
        field = {
            "id": "concat",
            "type": "concatField",
            "sourceFields": [{"fieldId": "a"}, {"fieldId": "b"}],
            "skipEmpty": True,
        }
        result = pattern.render(field, context)

        assert result["properties"]["skipEmpty"] == "true"

    def test_skip_empty_false(self, pattern, context):
        """Test skipEmpty when disabled."""
        field = {
            "id": "concat",
            "type": "concatField",
            "sourceFields": [{"fieldId": "a"}],
            "skipEmpty": False,
        }
        result = pattern.render(field, context)

        assert result["properties"]["skipEmpty"] == ""

    def test_display_type(self, pattern, context):
        """Test displayType property."""
        field = {
            "id": "concat",
            "type": "concatField",
            "sourceFields": [{"fieldId": "a"}],
            "displayType": "hidden",
        }
        result = pattern.render(field, context)

        assert result["properties"]["displayType"] == "hidden"

    def test_display_type_default(self, pattern, basic_field, context):
        """Test default displayType is readonly."""
        result = pattern.render(basic_field, context)

        assert result["properties"]["displayType"] == "readonly"

    def test_update_on(self, pattern, context):
        """Test updateOn property."""
        field = {
            "id": "concat",
            "type": "concatField",
            "sourceFields": [{"fieldId": "a"}],
            "updateOn": "blur",
        }
        result = pattern.render(field, context)

        assert result["properties"]["updateOn"] == "blur"

    def test_source_field_transform(self, pattern, context):
        """Test source field transformations."""
        field = {
            "id": "concat",
            "type": "concatField",
            "sourceFields": [
                {"fieldId": "first_name", "transform": "uppercase"},
                {"fieldId": "last_name", "transform": "uppercase"},
            ],
        }
        result = pattern.render(field, context)

        source_fields = result["properties"]["sourceFields"]
        assert source_fields[0]["transform"] == "uppercase"
        assert source_fields[1]["transform"] == "uppercase"

    def test_required_field(self, pattern, context):
        """Test required field generates 'true' string."""
        field = {
            "id": "concat",
            "type": "concatField",
            "sourceFields": [{"fieldId": "a"}],
            "required": True,
            "requiredMessage": "This field is required",
        }
        result = pattern.render(field, context)

        assert result["properties"]["required"] == "true"
        assert result["properties"]["requiredMessage"] == "This field is required"

    def test_format_pattern(self, pattern, context):
        """Test format pattern property."""
        field = {
            "id": "concat",
            "type": "concatField",
            "sourceFields": [{"fieldId": "a"}],
            "formatPattern": "{0}-{1}-{2}",
        }
        result = pattern.render(field, context)

        assert result["properties"]["formatPattern"] == "{0}-{1}-{2}"

    def test_valid_json_output(self, pattern, basic_field, context):
        """Test that output is valid JSON."""
        result = pattern.render(basic_field, context)

        json_str = json.dumps(result)
        assert json_str is not None

        parsed = json.loads(json_str)
        assert parsed["className"] == "global.govstack.concatfield.element.ConcatFieldElement"
        assert isinstance(parsed["properties"]["sourceFields"], list)

    def test_matches_production_structure(self, pattern, context):
        """Test that output matches production Joget structure."""
        field = {
            "id": "personal_information",
            "label": "Personal Information",
            "type": "concatField",
            "sourceFields": [
                {"fieldId": "national_id", "transform": ""},
                {"fieldId": "first_name", "transform": ""},
                {"fieldId": "last_name", "transform": ""},
                {"fieldId": "date_of_birth", "transform": ""},
            ],
            "displayType": "readonly",
            "separator": "_",
            "skipEmpty": True,
            "updateOn": "change",
        }
        result = pattern.render(field, context)

        # Verify production structure
        assert result["className"] == "global.govstack.concatfield.element.ConcatFieldElement"
        assert result["properties"]["displayType"] == "readonly"
        assert result["properties"]["separator"] == "_"
        assert result["properties"]["skipEmpty"] == "true"
        assert result["properties"]["updateOn"] == "change"
        assert len(result["properties"]["sourceFields"]) == 4
