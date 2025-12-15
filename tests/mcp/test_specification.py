"""Tests for MCP specification tools."""

import pytest
import yaml
from joget_form_mcp.tools.specification import SpecificationTools


class TestSpecificationTools:
    """Tests for SpecificationTools class."""

    @pytest.fixture
    def tools(self):
        """Create SpecificationTools instance."""
        return SpecificationTools()

    def test_create_form_spec_basic(self, tools):
        """Test creating basic form spec from description."""
        result = tools.create_form_spec(
            "Create a contact form with name, email, and message fields"
        )

        assert result["success"] is True
        assert "yaml_spec" in result
        assert result["field_count"] >= 3

        # Parse and verify YAML
        spec = yaml.safe_load(result["yaml_spec"])
        assert "form" in spec
        assert "fields" in spec
        field_ids = [f["id"] for f in spec["fields"]]
        assert "name" in field_ids or "fullName" in field_ids
        assert "email" in field_ids
        assert "message" in field_ids

    def test_create_form_spec_with_id_and_name(self, tools):
        """Test creating form spec with custom ID and name."""
        result = tools.create_form_spec(
            "A form with name and email",
            form_id="customForm",
            form_name="My Custom Form"
        )

        assert result["success"] is True
        spec = yaml.safe_load(result["yaml_spec"])
        assert spec["form"]["id"] == "customForm"
        assert spec["form"]["name"] == "My Custom Form"

    def test_create_form_spec_infers_field_types(self, tools):
        """Test that field types are correctly inferred."""
        result = tools.create_form_spec(
            "Form with email address, phone number, and birth date"
        )

        assert result["success"] is True
        spec = yaml.safe_load(result["yaml_spec"])

        # Find fields and check types
        fields_by_id = {f["id"]: f for f in spec["fields"]}

        if "email" in fields_by_id:
            assert fields_by_id["email"]["type"] == "textField"
            assert "validator" in fields_by_id["email"]

        if "phone" in fields_by_id:
            assert fields_by_id["phone"]["type"] == "textField"

        # Birth date should be datePicker
        date_fields = [f for f in spec["fields"] if "date" in f["id"].lower()]
        if date_fields:
            assert date_fields[0]["type"] == "datePicker"

    def test_create_form_spec_empty_description(self, tools):
        """Test creating form spec with empty description."""
        result = tools.create_form_spec("")

        assert result["success"] is False
        assert "error" in result

    def test_create_cascading_dropdown_spec(self, tools):
        """Test creating cascading dropdown pattern."""
        result = tools.create_cascading_dropdown_spec(
            parent_form_id="md25equipCategory",
            child_form_id="md25equipment"
        )

        assert result["success"] is True
        assert "parent_spec" in result
        assert "child_spec" in result

        # Verify parent form
        parent = yaml.safe_load(result["parent_spec"])
        assert parent["form"]["id"] == "md25equipCategory"
        assert any(f["id"] == "code" for f in parent["fields"])
        assert any(f["id"] == "name" for f in parent["fields"])

        # Verify child form
        child = yaml.safe_load(result["child_spec"])
        assert child["form"]["id"] == "md25equipment"

        # Check cascading dropdown field
        category_field = next(
            (f for f in child["fields"] if f.get("optionsSource")),
            None
        )
        assert category_field is not None
        assert category_field["type"] == "selectBox"
        assert category_field["optionsSource"]["type"] == "formData"
        assert category_field["optionsSource"]["formId"] == "md25equipCategory"

    def test_create_cascading_dropdown_spec_custom_fields(self, tools):
        """Test cascading dropdown with custom field names."""
        result = tools.create_cascading_dropdown_spec(
            parent_form_id="categories",
            child_form_id="items",
            parent_label_field="title",
            parent_value_field="id",
            child_fk_field="parentCategoryId"
        )

        assert result["success"] is True

        parent = yaml.safe_load(result["parent_spec"])
        assert any(f["id"] == "id" for f in parent["fields"])
        assert any(f["id"] == "title" for f in parent["fields"])

        child = yaml.safe_load(result["child_spec"])
        fk_field = next(f for f in child["fields"] if f["id"] == "parentCategoryId")
        assert fk_field["optionsSource"]["valueColumn"] == "id"
        assert fk_field["optionsSource"]["labelColumn"] == "title"

    def test_add_field_to_spec(self, tools):
        """Test adding a field to existing spec."""
        original_yaml = """
form:
  id: testForm
  name: Test Form

fields:
  - id: name
    label: Name
    type: textField
"""
        result = tools.add_field_to_spec(
            original_yaml,
            "email"  # Simple field name
        )

        assert result["success"] is True
        assert "yaml_spec" in result
        assert result["field_count"] == 2

        spec = yaml.safe_load(result["yaml_spec"])
        assert len(spec["fields"]) == 2
        # Check that a field with 'email' in the id was added
        assert any("email" in f["id"].lower() for f in spec["fields"])

    def test_add_field_to_spec_at_position(self, tools):
        """Test adding a field at specific position."""
        original_yaml = """
form:
  id: testForm
  name: Test Form

fields:
  - id: field1
    label: Field 1
    type: textField

  - id: field3
    label: Field 3
    type: textField
"""
        result = tools.add_field_to_spec(
            original_yaml,
            "description notes",
            position=1  # Insert between field1 and field3
        )

        assert result["success"] is True
        spec = yaml.safe_load(result["yaml_spec"])
        assert len(spec["fields"]) == 3
        # The new field should be at position 1
        assert "description" in spec["fields"][1]["id"].lower()

    def test_add_field_to_spec_invalid_yaml(self, tools):
        """Test adding field to invalid YAML."""
        result = tools.add_field_to_spec(
            "not: valid: yaml: [",
            "some field"
        )

        assert result["success"] is False
        assert "error" in result

    def test_id_to_label_conversion(self, tools):
        """Test conversion of camelCase ID to label."""
        assert tools._id_to_label("firstName") == "First Name"
        assert tools._id_to_label("dateOfBirth") == "Date Of Birth"
        assert tools._id_to_label("email") == "Email"
        assert tools._id_to_label("userID") == "User Id"

    def test_id_to_name_conversion(self, tools):
        """Test conversion of form ID to name."""
        assert "MD.25" in tools._id_to_name("md25equipCategory")
        assert "Equip Category" in tools._id_to_name("md25equipCategory")
        assert "Contact Form" == tools._id_to_name("contactForm")
