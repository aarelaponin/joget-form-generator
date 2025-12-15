"""Tests for MCP discovery tools."""

import pytest
from joget_form_mcp.tools.discovery import DiscoveryTools


class TestDiscoveryTools:
    """Tests for DiscoveryTools class."""

    @pytest.fixture
    def tools(self):
        """Create DiscoveryTools instance."""
        return DiscoveryTools()

    def test_list_field_types(self, tools):
        """Test listing all field types."""
        result = tools.list_field_types()

        assert "total_types" in result
        assert result["total_types"] > 0
        assert "categories" in result
        assert "standard" in result["categories"]
        assert "advanced" in result["categories"]
        assert "enterprise" in result["categories"]
        assert "registered_types" in result

        # Check that common types are present
        assert any(t["type"] == "textField" for t in result["categories"]["standard"])
        assert any(t["type"] == "selectBox" for t in result["categories"]["standard"])

    def test_get_field_type_info_text_field(self, tools):
        """Test getting info for textField."""
        result = tools.get_field_type_info("textField")

        assert result["type"] == "textField"
        assert "description" in result
        assert "use_cases" in result
        assert "properties" in result
        assert "example" in result
        assert result["registered"] is True

    def test_get_field_type_info_select_box(self, tools):
        """Test getting info for selectBox."""
        result = tools.get_field_type_info("selectBox")

        assert result["type"] == "selectBox"
        assert "options_sources" in result  # Select box has options sources
        assert "formData" in result["options_sources"]

    def test_get_field_type_info_calculation_field(self, tools):
        """Test getting info for calculationField (enterprise)."""
        result = tools.get_field_type_info("calculationField")

        assert result["type"] == "calculationField"
        assert result["category"] == "enterprise"
        assert "equation" in str(result.get("example", {}))

    def test_get_field_type_info_unknown(self, tools):
        """Test getting info for unknown field type."""
        result = tools.get_field_type_info("unknownFieldType")

        assert "error" in result
        assert "available_types" in result

    def test_get_example_spec_simple_form(self, tools):
        """Test getting simple form example."""
        result = tools.get_example_spec("simple-form")

        assert "yaml_spec" in result
        assert "form:" in result["yaml_spec"]
        assert "fields:" in result["yaml_spec"]

    def test_get_example_spec_cascading_dropdown(self, tools):
        """Test getting cascading dropdown example."""
        result = tools.get_example_spec("cascading-dropdown")

        assert "yaml_spec" in result
        assert "optionsSource" in result["yaml_spec"]
        assert "formData" in result["yaml_spec"]

    def test_get_example_spec_normalized_name(self, tools):
        """Test that example names are normalized."""
        # Both should work
        result1 = tools.get_example_spec("simple-form")
        result2 = tools.get_example_spec("simple_form")

        assert "yaml_spec" in result1
        assert "yaml_spec" in result2

    def test_get_example_spec_unknown(self, tools):
        """Test getting unknown example."""
        result = tools.get_example_spec("unknown-example")

        assert "error" in result
        assert "available_examples" in result

    def test_get_field_types_documentation(self, tools):
        """Test getting full field types documentation."""
        doc = tools.get_field_types_documentation()

        assert "# Joget Form Generator" in doc
        assert "## Standard Fields" in doc
        assert "## Advanced Fields" in doc
        assert "## Enterprise Fields" in doc
        assert "textField" in doc
        assert "selectBox" in doc

    def test_get_cascading_dropdown_documentation(self, tools):
        """Test getting cascading dropdown documentation."""
        doc = tools.get_cascading_dropdown_documentation()

        assert "# Cascading Dropdowns" in doc
        assert "formData" in doc
        assert "optionsSource" in doc
        assert "Parent Form" in doc
        assert "Child Form" in doc
