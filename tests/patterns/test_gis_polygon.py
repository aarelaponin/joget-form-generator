"""Tests for GIS Polygon Capture pattern (GovStack plugin)."""

import json
import pytest
from joget_form_generator.patterns.gis_polygon import GisPolygonCapturePattern


class TestGisPolygonCapturePattern:
    """Test suite for GisPolygonCapturePattern."""

    @pytest.fixture
    def pattern(self):
        """Create pattern instance for testing."""
        return GisPolygonCapturePattern()

    @pytest.fixture
    def basic_field(self):
        """Basic GIS polygon capture field specification."""
        return {
            "id": "geometry",
            "label": "Parcel Boundary",
            "type": "gisPolygonCapture",
            "required": True,
            "defaultLatitude": "-29.6",
            "defaultLongitude": "28.2",
        }

    @pytest.fixture
    def context(self):
        """Standard rendering context."""
        return {"form": {"id": "parcelForm", "name": "Parcel Form", "tableName": "parcelForm"}}

    def test_render_correct_classname(self, pattern, basic_field, context):
        """Test that output uses correct GovStack GIS className."""
        result = pattern.render(basic_field, context)

        assert result["className"] == "global.govstack.gisui.element.GisPolygonCaptureElement"
        assert result["properties"]["id"] == "geometry"

    def test_required_field(self, pattern, basic_field, context):
        """Test required field generates 'true' string."""
        result = pattern.render(basic_field, context)

        assert result["properties"]["required"] == "true"

    def test_map_defaults(self, pattern, basic_field, context):
        """Test map configuration defaults."""
        result = pattern.render(basic_field, context)

        assert result["properties"]["defaultLatitude"] == "-29.6"
        assert result["properties"]["defaultLongitude"] == "28.2"
        assert result["properties"]["defaultZoom"] == "14"  # default
        assert result["properties"]["mapHeight"] == "500"  # default
        assert result["properties"]["tileProvider"] == "OSM"  # default

    def test_capture_mode_defaults(self, pattern, basic_field, context):
        """Test capture mode defaults to BOTH."""
        result = pattern.render(basic_field, context)

        assert result["properties"]["captureMode"] == "BOTH"
        assert result["properties"]["defaultMode"] == "AUTO"

    def test_gps_settings(self, pattern, context):
        """Test GPS accuracy settings."""
        field = {
            "id": "geometry",
            "type": "gisPolygonCapture",
            "gpsHighAccuracy": True,
            "gpsMinAccuracy": "5",
        }
        result = pattern.render(field, context)

        assert result["properties"]["gpsHighAccuracy"] == "true"
        assert result["properties"]["gpsMinAccuracy"] == "5"

    def test_polygon_constraints(self, pattern, context):
        """Test polygon constraint properties."""
        field = {
            "id": "geometry",
            "type": "gisPolygonCapture",
            "minVertices": "4",
            "maxVertices": "100",
            "minAreaHectares": "0.1",
            "maxAreaHectares": "500",
        }
        result = pattern.render(field, context)

        assert result["properties"]["minVertices"] == "4"
        assert result["properties"]["maxVertices"] == "100"
        assert result["properties"]["minAreaHectares"] == "0.1"
        assert result["properties"]["maxAreaHectares"] == "500"

    def test_styling_properties(self, pattern, context):
        """Test polygon styling properties."""
        field = {
            "id": "geometry",
            "type": "gisPolygonCapture",
            "strokeColor": "#ff0000",
            "strokeWidth": "5",
            "fillColor": "#0000ff",
            "fillOpacity": "0.5",
        }
        result = pattern.render(field, context)

        assert result["properties"]["strokeColor"] == "#ff0000"
        assert result["properties"]["strokeWidth"] == "5"
        assert result["properties"]["fillColor"] == "#0000ff"
        assert result["properties"]["fillOpacity"] == "0.5"

    def test_overlap_detection(self, pattern, context):
        """Test overlap detection configuration."""
        field = {
            "id": "geometry",
            "type": "gisPolygonCapture",
            "enableOverlapCheck": True,
            "overlapFormId": "parcelLocation",
            "overlapGeometryField": "parcelGeometry",
            "overlapDisplayFields": "parcelCode",
        }
        result = pattern.render(field, context)

        assert result["properties"]["enableOverlapCheck"] == "true"
        assert result["properties"]["overlapFormId"] == "parcelLocation"
        assert result["properties"]["overlapGeometryField"] == "parcelGeometry"
        assert result["properties"]["overlapDisplayFields"] == "parcelCode"

    def test_derived_fields(self, pattern, context):
        """Test derived field IDs for auto-calculated values."""
        field = {
            "id": "geometry",
            "type": "gisPolygonCapture",
            "areaFieldId": "area_hectares",
            "perimeterFieldId": "perimeter_meters",
            "centroidFieldId": "centroid_lat",
            "vertexCountFieldId": "vertex_count",
        }
        result = pattern.render(field, context)

        assert result["properties"]["areaFieldId"] == "area_hectares"
        assert result["properties"]["perimeterFieldId"] == "perimeter_meters"
        assert result["properties"]["centroidFieldId"] == "centroid_lat"
        assert result["properties"]["vertexCountFieldId"] == "vertex_count"

    def test_api_configuration(self, pattern, context):
        """Test API endpoint configuration."""
        field = {
            "id": "geometry",
            "type": "gisPolygonCapture",
            "apiEndpoint": "/jw/api/gis/gis",
            "apiId": "API-12345",
            "apiKey": "secret-key",
        }
        result = pattern.render(field, context)

        assert result["properties"]["apiEndpoint"] == "/jw/api/gis/gis"
        assert result["properties"]["apiId"] == "API-12345"
        assert result["properties"]["apiKey"] == "secret-key"

    def test_valid_json_output(self, pattern, basic_field, context):
        """Test that output is valid JSON."""
        result = pattern.render(basic_field, context)

        json_str = json.dumps(result)
        assert json_str is not None

        parsed = json.loads(json_str)
        assert "className" in parsed
        assert "properties" in parsed
