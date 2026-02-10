"""GIS Polygon Capture pattern for GovStack GIS plugin."""

from typing import Any, ClassVar
from .base import BasePattern


class GisPolygonCapturePattern(BasePattern):
    """Pattern for GovStack GIS Polygon Capture Element.

    Enables GPS-based polygon capture for land parcel boundaries with
    overlap detection and auto-calculated derived fields.

    Plugin: global.govstack.gisui.element.GisPolygonCaptureElement
    """

    template_name: ClassVar[str] = "gis_polygon.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for GIS Polygon Capture template.

        Args:
            field: Field specification with properties:
                - id: Field ID (stores GeoJSON polygon)
                - label: Field label
                - required: Whether field is mandatory

                Map Configuration:
                - defaultLatitude: Map center latitude (default: "0")
                - defaultLongitude: Map center longitude (default: "0")
                - defaultZoom: Initial zoom level (default: "14")
                - mapHeight: Map height in pixels (default: "500")
                - tileProvider: "OSM" | "ESRI" | "Google" (default: "OSM")
                - showSatelliteOption: Show satellite toggle (default: True)

                Capture Settings:
                - captureMode: "GPS" | "DRAW" | "BOTH" (default: "BOTH")
                - defaultMode: "AUTO" | "MANUAL" (default: "AUTO")
                - gpsHighAccuracy: Use high accuracy GPS (default: True)
                - gpsMinAccuracy: Minimum GPS accuracy in meters (default: "10")
                - autoCloseDistance: Distance to auto-close polygon in meters (default: "15")

                Polygon Constraints:
                - minVertices: Minimum vertices (default: "3")
                - maxVertices: Maximum vertices (default: "200")
                - minAreaHectares: Minimum area in hectares (default: "0.01")
                - maxAreaHectares: Maximum area in hectares (default: "1000")
                - allowSelfIntersection: Allow self-intersecting polygons (default: False)

                Styling:
                - strokeColor: Polygon stroke color (default: "#3388ff")
                - strokeWidth: Stroke width in pixels (default: "3")
                - fillColor: Polygon fill color (default: "#3388ff")
                - fillOpacity: Fill opacity 0-1 (default: "0.2")

                Overlap Detection:
                - enableOverlapCheck: Enable overlap checking (default: True)
                - overlapFormId: Form ID containing existing parcels
                - overlapGeometryField: Geometry field in overlap form
                - overlapDisplayFields: Fields to display for overlapping parcels
                - overlapFilterCondition: SQL condition for overlap query

                Derived Fields (auto-populated):
                - areaFieldId: Hidden field to store area in hectares
                - perimeterFieldId: Hidden field to store perimeter in meters
                - centroidFieldId: Hidden field to store centroid coordinates
                - vertexCountFieldId: Hidden field to store vertex count

                Nearby Parcels Display:
                - showNearbyParcels: "DISABLED" | "ENABLED" (default: "DISABLED")
                - nearbyParcelsFormId: Form ID for nearby parcels
                - nearbyParcelsGeometryField: Geometry field for nearby parcels
                - nearbyParcelsDisplayFields: Fields to show for nearby parcels
                - nearbyParcelsFilterCondition: SQL filter condition
                - nearbyParcelsMaxResults: Max nearby parcels to show
                - nearbyParcelsStrokeColor: Stroke color for nearby parcels
                - nearbyParcelsFillColor: Fill color for nearby parcels
                - nearbyParcelsFillOpacity: Fill opacity for nearby parcels

                API Configuration:
                - apiEndpoint: GIS API endpoint (default: "/jw/api/gis/gis")
                - apiId: API ID for authentication
                - apiKey: API key (should use secure value placeholder)

            context: Rendering context

        Returns:
            Template context dictionary
        """
        return {
            "id": field["id"],
            "label": field.get("label", ""),
            "required": "true" if field.get("required", False) else "",
            "requiredMessage": field.get("requiredMessage", "Please capture the parcel boundary"),
            # Map configuration
            "defaultLatitude": field.get("defaultLatitude", "0"),
            "defaultLongitude": field.get("defaultLongitude", "0"),
            "defaultZoom": field.get("defaultZoom", "14"),
            "mapHeight": field.get("mapHeight", "500"),
            "tileProvider": field.get("tileProvider", "OSM"),
            "showSatelliteOption": "true" if field.get("showSatelliteOption", True) else "",
            # Capture settings
            "captureMode": field.get("captureMode", "BOTH"),
            "defaultMode": field.get("defaultMode", "AUTO"),
            "gpsHighAccuracy": "true" if field.get("gpsHighAccuracy", True) else "",
            "gpsMinAccuracy": field.get("gpsMinAccuracy", "10"),
            "autoCloseDistance": field.get("autoCloseDistance", "15"),
            # Polygon constraints
            "minVertices": field.get("minVertices", "3"),
            "maxVertices": field.get("maxVertices", "200"),
            "minAreaHectares": field.get("minAreaHectares", "0.01"),
            "maxAreaHectares": field.get("maxAreaHectares", "1000"),
            "allowSelfIntersection": "true" if field.get("allowSelfIntersection", False) else "",
            # Styling
            "strokeColor": field.get("strokeColor", "#3388ff"),
            "strokeWidth": field.get("strokeWidth", "3"),
            "fillColor": field.get("fillColor", "#3388ff"),
            "fillOpacity": field.get("fillOpacity", "0.2"),
            # Overlap detection
            "enableOverlapCheck": "true" if field.get("enableOverlapCheck", True) else "",
            "overlapFormId": field.get("overlapFormId", ""),
            "overlapGeometryField": field.get("overlapGeometryField", "geometry"),
            "overlapDisplayFields": field.get("overlapDisplayFields", ""),
            "overlapFilterCondition": field.get("overlapFilterCondition", ""),
            # Derived fields
            "areaFieldId": field.get("areaFieldId", ""),
            "perimeterFieldId": field.get("perimeterFieldId", ""),
            "centroidFieldId": field.get("centroidFieldId", ""),
            "vertexCountFieldId": field.get("vertexCountFieldId", ""),
            # Nearby parcels
            "showNearbyParcels": field.get("showNearbyParcels", "DISABLED"),
            "nearbyParcelsFormId": field.get("nearbyParcelsFormId", ""),
            "nearbyParcelsGeometryField": field.get("nearbyParcelsGeometryField", ""),
            "nearbyParcelsDisplayFields": field.get("nearbyParcelsDisplayFields", ""),
            "nearbyParcelsFilterCondition": field.get("nearbyParcelsFilterCondition", ""),
            "nearbyParcelsMaxResults": field.get("nearbyParcelsMaxResults", ""),
            "nearbyParcelsStrokeColor": field.get("nearbyParcelsStrokeColor", ""),
            "nearbyParcelsFillColor": field.get("nearbyParcelsFillColor", ""),
            "nearbyParcelsFillOpacity": field.get("nearbyParcelsFillOpacity", ""),
            # API configuration
            "apiEndpoint": field.get("apiEndpoint", "/jw/api/gis/gis"),
            "apiId": field.get("apiId", ""),
            "apiKey": field.get("apiKey", ""),
        }
