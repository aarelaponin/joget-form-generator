"""Tests for Smart Search pattern (GovStack plugin)."""

import json
import pytest
from joget_form_generator.patterns.smart_search import SmartSearchPattern


class TestSmartSearchPattern:
    """Test suite for SmartSearchPattern."""

    @pytest.fixture
    def pattern(self):
        """Create pattern instance for testing."""
        return SmartSearchPattern()

    @pytest.fixture
    def basic_field(self):
        """Basic smart search field specification."""
        return {
            "id": "farmer_id",
            "label": "Select Farmer",
            "type": "smartSearch",
            "required": False,
            "displayMode": "popup",
            "storeValue": "nationalId",
        }

    @pytest.fixture
    def context(self):
        """Standard rendering context."""
        return {"form": {"id": "parcelForm", "name": "Parcel Form", "tableName": "parcelForm"}}

    def test_render_correct_classname(self, pattern, basic_field, context):
        """Test that output uses correct GovStack Smart Search className."""
        result = pattern.render(basic_field, context)

        assert result["className"] == "global.govstack.smartsearch.element.SmartSearchElement"
        assert result["properties"]["id"] == "farmer_id"

    def test_display_mode(self, pattern, basic_field, context):
        """Test display mode property."""
        result = pattern.render(basic_field, context)

        assert result["properties"]["displayMode"] == "popup"
        assert result["properties"]["storeValue"] == "nationalId"

    def test_display_columns(self, pattern, context):
        """Test display columns configuration."""
        field = {
            "id": "farmer_id",
            "type": "smartSearch",
            "displayColumns": "nationalId,firstName,lastName,district,village",
        }
        result = pattern.render(field, context)

        assert (
            result["properties"]["displayColumns"]
            == "nationalId,firstName,lastName,district,village"
        )

    def test_search_patterns(self, pattern, context):
        """Test national ID and phone pattern configuration (JSON-safe patterns)."""
        # Note: Patterns must be JSON-safe (backslashes pre-escaped)
        field = {
            "id": "farmer_id",
            "type": "smartSearch",
            "nationalIdPattern": "^[0-9]{13,}$",
            "nationalIdMinLength": "13",
            "phonePattern": "^[+]266[0-9]{8}$",
            "phoneMinLength": "10",
        }
        result = pattern.render(field, context)

        assert result["properties"]["nationalIdPattern"] == "^[0-9]{13,}$"
        assert result["properties"]["nationalIdMinLength"] == "13"
        assert result["properties"]["phonePattern"] == "^[+]266[0-9]{8}$"
        assert result["properties"]["phoneMinLength"] == "10"

    def test_auto_select_behavior(self, pattern, context):
        """Test auto-select configuration."""
        field = {
            "id": "farmer_id",
            "type": "smartSearch",
            "autoSelectSingleResult": True,
            "autoSelectMinScore": "90",
            "showAutoSelectNotification": True,
        }
        result = pattern.render(field, context)

        assert result["properties"]["autoSelectSingleResult"] == "true"
        assert result["properties"]["autoSelectMinScore"] == "90"
        assert result["properties"]["showAutoSelectNotification"] == "true"

    def test_recent_farmers(self, pattern, context):
        """Test recent farmers display configuration."""
        field = {
            "id": "farmer_id",
            "type": "smartSearch",
            "showRecentFarmers": True,
            "maxRecentFarmers": "10",
        }
        result = pattern.render(field, context)

        assert result["properties"]["showRecentFarmers"] == "true"
        assert result["properties"]["maxRecentFarmers"] == "10"

    def test_location_filtering(self, pattern, context):
        """Test location-based filtering."""
        field = {
            "id": "farmer_id",
            "type": "smartSearch",
            "filterDistrict": "district",
            "filterVillage": "village",
        }
        result = pattern.render(field, context)

        assert result["properties"]["filterDistrict"] == "district"
        assert result["properties"]["filterVillage"] == "village"

    def test_api_configuration(self, pattern, context):
        """Test API endpoint configuration."""
        field = {
            "id": "farmer_id",
            "type": "smartSearch",
            "apiEndpoint": "/jw/api/fss",
            "apiId": "API-12345",
            "apiKey": "secret-key",
        }
        result = pattern.render(field, context)

        assert result["properties"]["apiEndpoint"] == "/jw/api/fss"
        assert result["properties"]["apiId"] == "API-12345"
        assert result["properties"]["apiKey"] == "secret-key"

    def test_defaults(self, pattern, context):
        """Test default values are applied."""
        field = {
            "id": "farmer_id",
            "type": "smartSearch",
        }
        result = pattern.render(field, context)

        assert result["properties"]["displayMode"] == "popup"  # default
        assert result["properties"]["autoSelectSingleResult"] == "true"  # default
        assert result["properties"]["autoSelectMinScore"] == "95"  # default
        assert result["properties"]["showRecentFarmers"] == "true"  # default
        assert result["properties"]["maxRecentFarmers"] == "5"  # default

    def test_valid_json_output(self, pattern, basic_field, context):
        """Test that output is valid JSON."""
        result = pattern.render(basic_field, context)

        json_str = json.dumps(result)
        assert json_str is not None

        parsed = json.loads(json_str)
        assert parsed["className"] == "global.govstack.smartsearch.element.SmartSearchElement"
