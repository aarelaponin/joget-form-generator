"""Smart Search pattern for GovStack Smart Search plugin."""

from typing import Any, ClassVar
from .base import BasePattern


class SmartSearchPattern(BasePattern):
    """Pattern for GovStack Smart Search Element.

    Provides fuzzy search functionality for finding records (e.g., farmers)
    by multiple criteria like national ID, phone number, name, etc.

    Plugin: global.govstack.smartsearch.element.SmartSearchElement
    """

    template_name: ClassVar[str] = "smart_search.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for Smart Search template.

        Args:
            field: Field specification with properties:
                - id: Field ID (stores selected record's ID)
                - label: Field label
                - required: Whether field is mandatory

                Display Configuration:
                - displayMode: "popup" | "inline" (default: "popup")
                - displayColumns: Columns to show in results (comma-separated)
                - storeValue: Field to store as value (default: national ID or code)

                Search Configuration:
                - nationalIdPattern: Regex for national ID validation
                - nationalIdMinLength: Min length for national ID search
                - phonePattern: Regex for phone number validation
                - phoneMinLength: Min length for phone search

                Auto-Select Behavior:
                - autoSelectSingleResult: Auto-select if only one result (default: True)
                - autoSelectMinScore: Minimum match score for auto-select (default: "95")
                - showAutoSelectNotification: Show notification on auto-select

                Recent Records:
                - showRecentFarmers: Show recent searches (default: True)
                - maxRecentFarmers: Max recent items to show (default: "5")

                Location Filtering:
                - filterDistrict: District field ID for filtering
                - filterVillage: Village field ID for filtering

                API Configuration:
                - apiEndpoint: Search API endpoint
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
            # Display configuration
            "displayMode": field.get("displayMode", "popup"),
            "displayColumns": field.get("displayColumns", ""),
            "storeValue": field.get("storeValue", ""),
            # Search configuration
            "nationalIdPattern": field.get("nationalIdPattern", ""),
            "nationalIdMinLength": field.get("nationalIdMinLength", ""),
            "phonePattern": field.get("phonePattern", ""),
            "phoneMinLength": field.get("phoneMinLength", ""),
            # Auto-select behavior
            "autoSelectSingleResult": ("true" if field.get("autoSelectSingleResult", True) else ""),
            "autoSelectMinScore": field.get("autoSelectMinScore", "95"),
            "showAutoSelectNotification": (
                "true" if field.get("showAutoSelectNotification", False) else ""
            ),
            # Recent records
            "showRecentFarmers": "true" if field.get("showRecentFarmers", True) else "",
            "maxRecentFarmers": field.get("maxRecentFarmers", "5"),
            # Location filtering
            "filterDistrict": field.get("filterDistrict", ""),
            "filterVillage": field.get("filterVillage", ""),
            # API configuration
            "apiEndpoint": field.get("apiEndpoint", ""),
            "apiId": field.get("apiId", ""),
            "apiKey": field.get("apiKey", ""),
        }
