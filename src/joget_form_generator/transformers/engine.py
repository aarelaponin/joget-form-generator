"""Transform engine: orchestrates the 7-phase pipeline."""

from typing import Any

from ..validators import DualValidator
from .normalizer import Normalizer
from ..patterns import PatternRegistry


class TransformEngine:
    """Orchestrates the complete transformation pipeline."""

    def __init__(self):
        """Initialize transform engine with validator and normalizer."""
        self.validator = DualValidator()
        self.normalizer = Normalizer()

    def generate(self, spec: dict[str, Any]) -> dict[str, dict]:
        """
        Generate Joget form JSON from specification.

        Pipeline:
        1. Load (handled by caller)
        2. Validate (JSON Schema + Pydantic)
        3. Normalize (apply defaults)
        4. Pattern Match (registry lookup)
        5. Transform (render with patterns)
        6. Post-Process (add metadata)
        7. Output (handled by caller)

        Args:
            spec: Raw specification dictionary

        Returns:
            Dictionary mapping form ID to form JSON

        Raises:
            ValueError: If validation fails
        """
        # Phase 2: Validate
        result, form_spec = self.validator.validate(spec)
        if not result.valid:
            error_msg = "\n  ".join(result.errors)
            raise ValueError(f"Validation failed:\n  {error_msg}")

        # Phase 3: Normalize
        normalized = self.normalizer.normalize(spec)

        # Phase 5: Transform
        form_json = self._transform(normalized)

        # Phase 6: Post-Process
        form_json = self._post_process(form_json, normalized)

        # Return dict with form ID as key
        form_id = normalized["form"]["id"]
        return {form_id: form_json}

    def _transform(self, normalized_spec: dict[str, Any]) -> dict[str, Any]:
        """
        Transform normalized spec into Joget form JSON.

        Args:
            normalized_spec: Normalized specification

        Returns:
            Joget form JSON structure with Section → Column → Fields layout
        """
        form_meta = normalized_spec["form"]
        fields = normalized_spec["fields"]

        # Transform each field using pattern library, grouping by sections
        context = {"form": form_meta}
        sections = []
        current_section_fields: list[dict[str, Any]] = []
        current_section_id = "section1"
        current_section_label = "Section"

        for field in fields:
            field_type = field["type"]

            # Handle section type - starts a new section
            if field_type == "section":
                # Save current section if it has fields
                if current_section_fields:
                    sections.append(
                        self._build_section(
                            current_section_id, current_section_label, current_section_fields
                        )
                    )
                    current_section_fields = []

                # Start new section
                current_section_id = field["id"]
                current_section_label = field.get("label", "")
                continue

            # Get pattern class from registry
            pattern_class = PatternRegistry.get(field_type)

            # Instantiate and render
            pattern = pattern_class()
            field_json = pattern.render(field, context)

            # Add to current section's field list
            current_section_fields.append(field_json)

        # Don't forget the last section
        if current_section_fields:
            sections.append(
                self._build_section(
                    current_section_id, current_section_label, current_section_fields
                )
            )

        # If no sections were created (no section markers), create default section
        if not sections:
            sections.append(self._build_section("section1", "Section", []))

        # Build form structure with WorkflowFormBinder (MDM pattern)
        form_json = {
            "className": "org.joget.apps.form.model.Form",
            "properties": {
                "id": form_meta["id"],
                "name": form_meta["name"],
                "tableName": form_meta["tableName"],
                "description": form_meta.get("description", ""),
                "loadBinder": {
                    "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                    "properties": {},
                },
                "storeBinder": {
                    "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                    "properties": {},
                },
                "noPermissionMessage": "",
                "postProcessorRunOn": "create",
                "permission": {"className": "", "properties": {}},
                "postProcessor": {"className": "", "properties": {}},
            },
            "elements": sections,
        }

        return form_json

    def _build_section(
        self, section_id: str, section_label: str, field_elements: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Build a Joget Section element with Column and fields.

        Args:
            section_id: Section ID
            section_label: Section label/title
            field_elements: List of field JSON elements

        Returns:
            Section JSON structure
        """
        return {
            "className": "org.joget.apps.form.model.Section",
            "properties": {"id": section_id, "label": section_label},
            "elements": [
                {
                    "className": "org.joget.apps.form.model.Column",
                    "properties": {"width": "100%"},
                    "elements": field_elements,
                }
            ],
        }

    def _post_process(
        self, form_json: dict[str, Any], normalized_spec: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Post-process form JSON (cleanup).

        Args:
            form_json: Generated form JSON
            normalized_spec: Normalized specification for context

        Returns:
            Post-processed form JSON
        """
        # No metadata - Joget doesn't accept extra fields
        return form_json
