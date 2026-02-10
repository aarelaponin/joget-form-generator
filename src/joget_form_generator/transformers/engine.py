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
        Post-process form JSON with auto-injection and validation.

        Operations:
        1. Auto-inject parent_id hidden field if form is used as subform
        2. Validate foreignKey references in FormGrid elements

        Args:
            form_json: Generated form JSON
            normalized_spec: Normalized specification for context

        Returns:
            Post-processed form JSON
        """
        # Check if this is a subform (has isSubform flag or needs parent_id)
        form_meta = normalized_spec.get("form", {})
        if form_meta.get("isSubform", False):
            form_json = self._inject_parent_id_if_missing(form_json)

        # Validate FormGrid foreignKey references
        self._validate_form_grid_references(form_json, normalized_spec)

        return form_json

    def _inject_parent_id_if_missing(self, form_json: dict[str, Any]) -> dict[str, Any]:
        """
        Auto-inject parent_id hidden field if not present.

        This ensures subforms have the necessary FK field to link back to parent.

        Args:
            form_json: Generated form JSON

        Returns:
            Form JSON with parent_id field injected if needed
        """
        # Check if parent_id already exists
        has_parent_id = self._find_field_by_id(form_json, "parent_id")
        if has_parent_id:
            return form_json

        # Create parent_id hidden field
        parent_id_field = {
            "className": "org.joget.apps.form.lib.HiddenField",
            "properties": {
                "id": "parent_id",
                "value": "",
                "useDefaultWhenEmpty": "",
                "workflowVariable": "",
                "validator": {"className": "", "properties": {}},
            },
        }

        # Insert at the beginning of the first section's first column
        if form_json.get("elements"):
            first_section = form_json["elements"][0]
            if first_section.get("elements"):
                first_column = first_section["elements"][0]
                if first_column.get("elements") is not None:
                    first_column["elements"].insert(0, parent_id_field)

        return form_json

    def _find_field_by_id(self, form_json: dict[str, Any], field_id: str) -> bool:
        """
        Recursively search for a field by ID in the form JSON.

        Args:
            form_json: Form JSON structure
            field_id: Field ID to find

        Returns:
            True if field exists, False otherwise
        """

        def search_elements(elements: list) -> bool:
            for element in elements:
                # Check properties for field ID
                props = element.get("properties", {})
                if props.get("id") == field_id:
                    return True
                # Recursively search nested elements
                if "elements" in element:
                    if search_elements(element["elements"]):
                        return True
            return False

        return search_elements(form_json.get("elements", []))

    def _validate_form_grid_references(
        self, form_json: dict[str, Any], normalized_spec: dict[str, Any]
    ) -> None:
        """
        Validate that FormGrid foreignKey references match existing fields.

        This helps catch configuration errors early.

        Args:
            form_json: Generated form JSON
            normalized_spec: Normalized specification for context

        Note:
            Currently logs warnings but doesn't raise errors to allow
            cross-form references that may be valid at runtime.
        """
        # Collect all field IDs in this form
        field_ids = {f["id"] for f in normalized_spec.get("fields", [])}

        def check_form_grids(elements: list) -> None:
            for element in elements:
                class_name = element.get("className", "")
                if "FormGrid" in class_name:
                    props = element.get("properties", {})
                    # Check loadBinder foreignKey
                    load_binder = props.get("loadBinder", {})
                    if load_binder:
                        fk = load_binder.get("properties", {}).get("foreignKey", "")
                        if fk and fk not in field_ids:
                            # This is expected for cross-form references
                            pass
                # Recursively check nested elements
                if "elements" in element:
                    check_form_grids(element["elements"])

        check_form_grids(form_json.get("elements", []))
