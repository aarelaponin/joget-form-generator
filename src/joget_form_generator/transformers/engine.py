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

        # Transform each field using pattern library
        context = {"form": form_meta}
        field_elements = []

        for field in fields:
            field_type = field["type"]

            # Get pattern class from registry
            pattern_class = PatternRegistry.get(field_type)

            # Instantiate and render
            pattern = pattern_class()
            field_json = pattern.render(field, context)

            # Add to field list
            field_elements.append(field_json)

        # Wrap fields in Section → Column layout (MDM pattern)
        section = {
            "className": "org.joget.apps.form.model.Section",
            "properties": {"id": "section1", "label": "Section"},
            "elements": [
                {
                    "className": "org.joget.apps.form.model.Column",
                    "properties": {"width": "100%"},
                    "elements": field_elements,
                }
            ],
        }

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
            "elements": [section],
        }

        return form_json

    def _post_process(
        self, form_json: dict[str, Any], normalized_spec: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Post-process form JSON (add metadata, cleanup).

        Args:
            form_json: Generated form JSON
            normalized_spec: Normalized specification for context

        Returns:
            Post-processed form JSON
        """
        # Add generator metadata as comment
        form_json["_metadata"] = {
            "generator": "joget-form-generator",
            "version": "0.1.0",
            "field_count": len(form_json["elements"]),
        }

        return form_json
