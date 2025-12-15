"""Tests for MCP generation tools."""

import json
import pytest
from joget_form_mcp.tools.generation import GenerationTools


class TestGenerationTools:
    """Tests for GenerationTools class."""

    @pytest.fixture
    def tools(self):
        """Create GenerationTools instance."""
        return GenerationTools()

    def test_generate_form_success(self, tools):
        """Test successful form generation."""
        yaml_spec = """
form:
  id: testForm
  name: Test Form

fields:
  - id: name
    label: Name
    type: textField
    required: true
"""
        result = tools.generate_form(yaml_spec)

        assert result["success"] is True
        assert result["form_id"] == "testForm"
        assert "joget_json" in result
        assert result["joget_json"]["className"] == "org.joget.apps.form.model.Form"
        assert result["joget_json"]["properties"]["id"] == "testForm"

    def test_generate_form_invalid_yaml(self, tools):
        """Test form generation with invalid YAML."""
        yaml_spec = """
form:
  id: testForm
  - invalid: yaml
    structure
"""
        result = tools.generate_form(yaml_spec)

        assert result["success"] is False
        assert "error" in result
        assert "YAML" in result["error"] or "Invalid" in result["error"]

    def test_generate_form_empty_spec(self, tools):
        """Test form generation with empty spec."""
        result = tools.generate_form("")

        assert result["success"] is False
        assert "error" in result

    def test_generate_form_missing_required_fields(self, tools):
        """Test form generation with missing required fields."""
        yaml_spec = """
form:
  id: testForm
  # Missing name

fields: []
"""
        result = tools.generate_form(yaml_spec)

        # Should fail validation
        assert result["success"] is False
        assert "error" in result

    def test_generate_form_with_select_box(self, tools):
        """Test form generation with select box field."""
        yaml_spec = """
form:
  id: statusForm
  name: Status Form

fields:
  - id: status
    label: Status
    type: selectBox
    required: true
    options:
      - value: active
        label: Active
      - value: inactive
        label: Inactive
"""
        result = tools.generate_form(yaml_spec)

        assert result["success"] is True
        assert result["form_id"] == "statusForm"

        # Check that select box is properly generated
        form_json = result["joget_json"]
        elements = form_json["elements"][0]["elements"][0]["elements"]
        status_field = elements[0]
        assert "SelectBox" in status_field["className"]

    def test_generate_form_with_cascading_dropdown(self, tools):
        """Test form generation with cascading dropdown."""
        yaml_spec = """
form:
  id: equipmentForm
  name: Equipment Form

fields:
  - id: categoryCode
    label: Category
    type: selectBox
    required: true
    optionsSource:
      type: formData
      formId: md25equipCategory
      valueColumn: code
      labelColumn: name
"""
        result = tools.generate_form(yaml_spec)

        assert result["success"] is True
        assert result["form_id"] == "equipmentForm"

    def test_generate_multiple_forms(self, tools):
        """Test generating multiple forms."""
        yaml_spec = """
forms:
  - form:
      id: form1
      name: Form 1
    fields:
      - id: field1
        label: Field 1
        type: textField

  - form:
      id: form2
      name: Form 2
    fields:
      - id: field2
        label: Field 2
        type: textField
"""
        result = tools.generate_multiple_forms(yaml_spec)

        assert result["success"] is True
        assert result["form_count"] == 2
        assert "form1" in result["forms"]
        assert "form2" in result["forms"]

    def test_field_count(self, tools):
        """Test that field count is correctly reported."""
        yaml_spec = """
form:
  id: testForm
  name: Test Form

fields:
  - id: field1
    label: Field 1
    type: textField

  - id: field2
    label: Field 2
    type: textArea

  - id: field3
    label: Field 3
    type: selectBox
    options:
      - value: a
        label: A
"""
        result = tools.generate_form(yaml_spec)

        assert result["success"] is True
        assert result["field_count"] == 3
