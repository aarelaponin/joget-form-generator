"""Tests for Multi Paged Form pattern (Enterprise Edition).

Tests the production-correct MultiPagedForm structure with flat pageN_* properties
inside the numberOfPage object.
"""

import json
import pytest
from joget_form_generator.patterns.multi_paged_form import MultiPagedFormPattern


class TestMultiPagedFormPattern:
    """Test suite for MultiPagedFormPattern."""

    @pytest.fixture
    def pattern(self):
        """Create pattern instance for testing."""
        return MultiPagedFormPattern()

    @pytest.fixture
    def basic_field(self):
        """Basic multiPagedForm field specification."""
        return {
            "id": "registrationWizard",
            "label": "",
            "type": "multiPagedForm",
            "pages": [
                {
                    "formId": "basicInfo",
                    "label": "General",
                    "validate": True,
                    "parentSubFormId": "basic_data",
                },
                {
                    "formId": "contactInfo",
                    "label": "Contact",
                    "validate": True,
                    "parentSubFormId": "contact_data",
                },
            ],
        }

    @pytest.fixture
    def context(self):
        """Standard rendering context."""
        return {"form": {"id": "mainForm", "name": "Main Form", "tableName": "mainForm"}}

    def test_render_correct_classname(self, pattern, basic_field, context):
        """Test that output uses correct MultiPagedForm className."""
        result = pattern.render(basic_field, context)

        assert result["className"] == "org.joget.plugin.enterprise.MultiPagedForm"
        assert result["properties"]["id"] == "registrationWizard"

    def test_number_of_pages_structure(self, pattern, basic_field, context):
        """Test that numberOfPage has correct structure with className as page count."""
        result = pattern.render(basic_field, context)

        number_of_page = result["properties"]["numberOfPage"]
        assert number_of_page["className"] == "2"  # Page count as string
        assert "properties" in number_of_page
        assert isinstance(number_of_page["properties"], dict)

    def test_page_properties_flat_structure(self, pattern, basic_field, context):
        """Test that pageN_* properties are generated as flat structure."""
        result = pattern.render(basic_field, context)

        page_props = result["properties"]["numberOfPage"]["properties"]

        # Page 1 properties
        assert page_props["page1_formDefId"] == "basicInfo"
        assert page_props["page1_label"] == "General"
        assert page_props["page1_validate"] == "true"
        assert page_props["page1_parentSubFormId"] == "basic_data"
        assert page_props["page1_subFormParentId"] == "parent_id"  # default
        assert page_props["page1_readonly"] == ""  # false = empty string
        assert page_props["page1_readonlyLabel"] == ""

        # Page 2 properties
        assert page_props["page2_formDefId"] == "contactInfo"
        assert page_props["page2_label"] == "Contact"
        assert page_props["page2_validate"] == "true"
        assert page_props["page2_parentSubFormId"] == "contact_data"

    def test_display_mode_default_tab(self, pattern, basic_field, context):
        """Test default display mode is 'tab'."""
        result = pattern.render(basic_field, context)

        assert result["properties"]["displayMode"] == "tab"

    def test_display_mode_wizard(self, pattern, basic_field, context):
        """Test wizard display mode."""
        basic_field["displayMode"] = "wizard"
        result = pattern.render(basic_field, context)

        assert result["properties"]["displayMode"] == "wizard"

    def test_navigation_labels_custom(self, pattern, basic_field, context):
        """Test custom navigation button labels."""
        basic_field["prevButtonLabel"] = "Back"
        basic_field["nextButtonLabel"] = "Continue"
        result = pattern.render(basic_field, context)

        # Note: Joget uses 'prevButtonlabel' with lowercase 'l'
        assert result["properties"]["prevButtonlabel"] == "Back"
        assert result["properties"]["nextButtonlabel"] == "Continue"

    def test_navigation_labels_default(self, pattern, basic_field, context):
        """Test default navigation button labels."""
        result = pattern.render(basic_field, context)

        assert result["properties"]["prevButtonlabel"] == "Previous"
        assert result["properties"]["nextButtonlabel"] == "Next"

    def test_partially_store_enabled(self, pattern, basic_field, context):
        """Test partiallyStore option when enabled."""
        basic_field["partiallyStore"] = True
        result = pattern.render(basic_field, context)

        assert result["properties"]["partiallyStore"] == "true"
        assert result["properties"]["storeMainFormOnPartiallyStore"] == "true"

    def test_partially_store_disabled(self, pattern, basic_field, context):
        """Test partiallyStore is empty string when disabled."""
        basic_field["partiallyStore"] = False
        result = pattern.render(basic_field, context)

        assert result["properties"]["partiallyStore"] == ""

    def test_only_submit_on_last_page(self, pattern, basic_field, context):
        """Test onlyAllowSubmitOnLastPage option."""
        basic_field["onlyAllowSubmitOnLastPage"] = True
        result = pattern.render(basic_field, context)

        assert result["properties"]["onlyAllowSubmitOnLastPage"] == "true"

    def test_readonly_page(self, pattern, context):
        """Test readonly page configuration."""
        field = {
            "id": "wizard",
            "type": "multiPagedForm",
            "pages": [
                {
                    "formId": "readonlyForm",
                    "label": "View Only",
                    "readonly": True,
                    "readonlyLabel": "View Mode",
                },
            ],
        }
        result = pattern.render(field, context)

        page_props = result["properties"]["numberOfPage"]["properties"]
        assert page_props["page1_readonly"] == "true"
        assert page_props["page1_readonlyLabel"] == "View Mode"

    def test_custom_subform_parent_id(self, pattern, context):
        """Test custom subFormParentId field."""
        field = {
            "id": "wizard",
            "type": "multiPagedForm",
            "pages": [
                {
                    "formId": "subform1",
                    "label": "Page 1",
                    "subFormParentId": "custom_parent_id",
                },
            ],
        }
        result = pattern.render(field, context)

        page_props = result["properties"]["numberOfPage"]["properties"]
        assert page_props["page1_subFormParentId"] == "custom_parent_id"

    def test_eight_page_wizard(self, pattern, context):
        """Test 8-page wizard (production-scale) structure."""
        field = {
            "id": "farmerWizard",
            "type": "multiPagedForm",
            "displayMode": "tab",
            "pages": [
                {"formId": f"page{i}Form", "label": f"Page {i}", "validate": True}
                for i in range(1, 9)
            ],
        }
        result = pattern.render(field, context)

        # Check page count
        assert result["properties"]["numberOfPage"]["className"] == "8"

        # Verify all 8 pages have properties
        page_props = result["properties"]["numberOfPage"]["properties"]
        for i in range(1, 9):
            assert f"page{i}_formDefId" in page_props
            assert page_props[f"page{i}_formDefId"] == f"page{i}Form"
            assert page_props[f"page{i}_label"] == f"Page {i}"
            assert page_props[f"page{i}_validate"] == "true"

    def test_ajax_mode_enabled(self, pattern, basic_field, context):
        """Test ajaxMode when enabled."""
        basic_field["ajaxMode"] = True
        result = pattern.render(basic_field, context)

        assert result["properties"]["ajaxMode"] == "true"

    def test_ajax_mode_disabled(self, pattern, basic_field, context):
        """Test ajaxMode is empty string when disabled."""
        result = pattern.render(basic_field, context)

        assert result["properties"]["ajaxMode"] == ""

    def test_css_property(self, pattern, basic_field, context):
        """Test custom CSS property."""
        basic_field["css"] = ".wizard-step { padding: 20px; }"
        result = pattern.render(basic_field, context)

        assert result["properties"]["css"] == ".wizard-step { padding: 20px; }"

    def test_valid_json_output(self, pattern, basic_field, context):
        """Test that output is valid JSON that can be serialized."""
        result = pattern.render(basic_field, context)

        # Should be serializable to JSON
        json_str = json.dumps(result)
        assert json_str is not None

        # Should be parseable back
        parsed = json.loads(json_str)
        assert parsed["className"] == "org.joget.plugin.enterprise.MultiPagedForm"

    def test_matches_production_structure(self, pattern, context):
        """Test that output matches production Joget structure."""
        field = {
            "id": "spProgramWizard",
            "type": "multiPagedForm",
            "displayMode": "tab",
            "partiallyStore": True,
            "onlyAllowSubmitOnLastPage": True,
            "pages": [
                {
                    "formId": "spProgramIdentity",
                    "label": "Identity",
                    "validate": True,
                    "parentSubFormId": "tab_identity",
                },
                {
                    "formId": "spProgramTimeline",
                    "label": "Timeline & Budget",
                    "validate": True,
                    "parentSubFormId": "tab_timeline",
                },
            ],
        }
        result = pattern.render(field, context)

        # Verify production structure
        assert result["className"] == "org.joget.plugin.enterprise.MultiPagedForm"
        assert result["properties"]["displayMode"] == "tab"
        assert result["properties"]["partiallyStore"] == "true"
        assert result["properties"]["onlyAllowSubmitOnLastPage"] == "true"

        number_of_page = result["properties"]["numberOfPage"]
        assert number_of_page["className"] == "2"
        assert number_of_page["properties"]["page1_formDefId"] == "spProgramIdentity"
        assert number_of_page["properties"]["page1_parentSubFormId"] == "tab_identity"
