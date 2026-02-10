"""Concat Field pattern for GovStack Concat Field plugin."""

from typing import Any, ClassVar
from .base import BasePattern


class ConcatFieldPattern(BasePattern):
    """Pattern for GovStack Concat Field Element.

    Concatenates values from multiple source fields with configurable
    separators, prefixes, suffixes, and transformations.

    Plugin: global.govstack.concatfield.element.ConcatFieldElement
    """

    template_name: ClassVar[str] = "concat_field.j2"

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for Concat Field template.

        Args:
            field: Field specification with properties:
                - id: Field ID (stores concatenated value)
                - label: Field label
                - required: Whether field is mandatory
                - requiredMessage: Validation message

                Source Fields:
                - sourceFields: Array of source field definitions
                    Each: {fieldId: str, transform: str}
                    transform options: "", "uppercase", "lowercase", "trim"

                Formatting:
                - separator: Separator between field values (default: "_")
                - prefix: Prefix before concatenated value
                - suffix: Suffix after concatenated value
                - formatPattern: Custom format pattern (optional)
                - skipEmpty: Skip empty source values (default: True)

                Display:
                - displayType: "readonly" | "hidden" | "editable" (default: "readonly")
                - updateOn: "change" | "blur" | "submit" (default: "change")

            context: Rendering context

        Returns:
            Template context dictionary
        """
        # Process source fields into the expected format
        source_fields = []
        for sf in field.get("sourceFields", []):
            source_fields.append(
                {
                    "fieldId": sf.get("fieldId", ""),
                    "transform": sf.get("transform", ""),
                }
            )

        return {
            "id": field["id"],
            "label": field.get("label", ""),
            "required": "true" if field.get("required", False) else "",
            "requiredMessage": field.get("requiredMessage", "This field is required"),
            # Source fields
            "sourceFields": source_fields,
            # Formatting
            "separator": field.get("separator", "_"),
            "prefix": field.get("prefix", ""),
            "suffix": field.get("suffix", ""),
            "formatPattern": field.get("formatPattern", ""),
            "skipEmpty": "true" if field.get("skipEmpty", True) else "",
            # Display
            "displayType": field.get("displayType", "readonly"),
            "updateOn": field.get("updateOn", "change"),
        }
