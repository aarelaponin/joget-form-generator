"""Tests for MCP validation tools."""

import json
import pytest
from joget_form_mcp.tools.validation import ValidationTools


class TestValidationTools:
    """Tests for ValidationTools class."""

    @pytest.fixture
    def tools(self):
        """Create ValidationTools instance."""
        return ValidationTools()

    def test_validate_spec_success(self, tools):
        """Test successful spec validation."""
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
        result = tools.validate_spec(yaml_spec)

        assert result["valid"] is True
        assert result.get("errors") is None or len(result.get("errors", [])) == 0
        assert "form_info" in result
        assert result["form_info"]["form_id"] == "testForm"
        assert result["form_info"]["field_count"] == 1

    def test_validate_spec_invalid_yaml(self, tools):
        """Test validation with invalid YAML."""
        yaml_spec = """
form:
  id: testForm
  - invalid yaml
"""
        result = tools.validate_spec(yaml_spec)

        assert result["valid"] is False
        assert "errors" in result
        assert len(result["errors"]) > 0

    def test_validate_spec_missing_required(self, tools):
        """Test validation with missing required field."""
        yaml_spec = """
form:
  id: testForm
  # Missing name

fields: []
"""
        result = tools.validate_spec(yaml_spec)

        assert result["valid"] is False
        assert "errors" in result

    def test_validate_joget_json_success(self, tools):
        """Test successful Joget JSON validation."""
        joget_json = json.dumps(
            {
                "className": "org.joget.apps.form.model.Form",
                "properties": {
                    "id": "testForm",
                    "name": "Test Form",
                    "tableName": "app_fd_testForm",
                    "loadBinder": {
                        "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                        "properties": {},
                    },
                    "storeBinder": {
                        "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                        "properties": {},
                    },
                },
                "elements": [
                    {
                        "className": "org.joget.apps.form.model.Section",
                        "properties": {"id": "section1", "label": "Section"},
                        "elements": [
                            {
                                "className": "org.joget.apps.form.model.Column",
                                "properties": {"width": "100%"},
                                "elements": [],
                            }
                        ],
                    }
                ],
            }
        )

        result = tools.validate_joget_json(joget_json)

        assert result["valid"] is True
        assert "structure" in result
        assert result["structure"]["form_id"] == "testForm"

    def test_validate_joget_json_invalid_json(self, tools):
        """Test validation with invalid JSON."""
        result = tools.validate_joget_json("not valid json {")

        assert result["valid"] is False
        assert "errors" in result

    def test_validate_joget_json_missing_classname(self, tools):
        """Test validation with missing className."""
        joget_json = json.dumps(
            {"properties": {"id": "testForm", "name": "Test Form", "tableName": "app_fd_testForm"}}
        )

        result = tools.validate_joget_json(joget_json)

        assert result["valid"] is False
        assert any("className" in err for err in result.get("errors", []))

    def test_validate_joget_json_missing_properties(self, tools):
        """Test validation with missing required properties."""
        joget_json = json.dumps(
            {
                "className": "org.joget.apps.form.model.Form",
                "properties": {
                    "id": "testForm"
                    # Missing name and tableName
                },
                "elements": [],
            }
        )

        result = tools.validate_joget_json(joget_json)

        assert result["valid"] is False
        assert len(result.get("errors", [])) > 0
