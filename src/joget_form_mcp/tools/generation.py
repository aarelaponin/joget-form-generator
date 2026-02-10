"""
Generation tools for MCP server.

Provides tools to generate Joget form JSON from YAML specifications.
"""

import logging
from typing import Any

import yaml

from joget_form_generator.transformers.engine import TransformEngine

logger = logging.getLogger(__name__)


class GenerationTools:
    """Tools for generating Joget forms from YAML specifications."""

    def __init__(self):
        """Initialize generation tools with transform engine."""
        self.engine = TransformEngine()

    def generate_form(self, yaml_spec: str) -> dict[str, Any]:
        """
        Generate Joget form JSON from YAML specification.

        Args:
            yaml_spec: YAML string defining the form specification

        Returns:
            Dictionary with:
                - success: bool
                - form_id: str (if successful)
                - joget_json: dict (if successful)
                - error: str (if failed)
        """
        try:
            # Parse YAML
            spec = yaml.safe_load(yaml_spec)

            if not spec:
                return {"success": False, "error": "Empty or invalid YAML specification"}

            # Generate form
            forms = self.engine.generate(spec)

            # Get the first (and usually only) form
            form_id = list(forms.keys())[0]
            form_json = forms[form_id]

            return {
                "success": True,
                "form_id": form_id,
                "joget_json": form_json,
                "field_count": self._count_fields(form_json),
                "message": f"Successfully generated form '{form_id}'",
            }

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return {"success": False, "error": f"Invalid YAML syntax: {e}"}
        except ValueError as e:
            # Validation errors from the engine
            logger.error(f"Validation error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.exception("Unexpected error during generation")
            return {"success": False, "error": f"Generation failed: {e}"}

    def generate_multiple_forms(self, yaml_spec: str) -> dict[str, Any]:
        """
        Generate multiple Joget forms from a multi-form YAML specification.

        The YAML can contain multiple form definitions in a 'forms' array.

        Args:
            yaml_spec: YAML string with multiple form definitions

        Returns:
            Dictionary with:
                - success: bool
                - forms: dict[form_id, joget_json] (if successful)
                - errors: list[str] (any errors encountered)
        """
        try:
            spec = yaml.safe_load(yaml_spec)

            if not spec:
                return {"success": False, "error": "Empty or invalid YAML specification"}

            # Check if this is a multi-form spec
            if "forms" in spec:
                forms_spec = spec["forms"]
            else:
                # Single form, wrap it
                forms_spec = [spec]

            results = {}
            errors = []

            for form_spec in forms_spec:
                try:
                    forms = self.engine.generate(form_spec)
                    results.update(forms)
                except Exception as e:
                    form_id = form_spec.get("form", {}).get("id", "unknown")
                    errors.append(f"Form '{form_id}': {e}")

            return {
                "success": len(results) > 0,
                "forms": results,
                "form_count": len(results),
                "errors": errors if errors else None,
                "message": f"Generated {len(results)} form(s)"
                + (f" with {len(errors)} error(s)" if errors else ""),
            }

        except yaml.YAMLError as e:
            return {"success": False, "error": f"Invalid YAML syntax: {e}"}
        except Exception as e:
            logger.exception("Unexpected error during multi-form generation")
            return {"success": False, "error": f"Generation failed: {e}"}

    def _count_fields(self, form_json: dict[str, Any]) -> int:
        """Count the number of fields in a form JSON."""
        count = 0

        def count_elements(elements: list) -> int:
            nonlocal count
            for element in elements:
                class_name = element.get("className", "")
                # Skip sections and columns, count actual fields
                if "Section" not in class_name and "Column" not in class_name:
                    count += 1
                if "elements" in element:
                    count_elements(element["elements"])
            return count

        if "elements" in form_json:
            count_elements(form_json["elements"])

        return count

    def generate_form_package(self, yaml_spec: str) -> dict[str, Any]:
        """
        Generate a complete form package from a YAML specification.

        This tool creates multiple interconnected forms including:
        - A main wizard form (MultiPagedForm)
        - Page subforms referenced by the wizard
        - Auto-injection of parent_id hidden fields for relationship linking

        Expected YAML structure:
        ```yaml
        package:
          id: farmerRegistration
          name: Farmer Registration Package
          description: Multi-tab farmer registration wizard

        mainForm:
          id: farmerRegistrationForm
          name: Farmer Registration Form
          tableName: farms_registry
          wizard:
            id: farmerWizard
            displayMode: tab  # or wizard
            partiallyStore: true
            pages:
              - formId: farmerBasicInfo
                label: General
                validate: true
                parentSubFormId: basic_data
              - formId: farmerResidency
                label: Residency
                validate: true
                parentSubFormId: location_data

        subForms:
          - form:
              id: farmerBasicInfo
              name: 01.01 - Basic Information
              tableName: farmerBasicInfo
            fields:
              - id: national_id
                label: National ID
                type: textField
                required: true

          - form:
              id: farmerResidency
              name: 01.02 - Residency
              tableName: farmerResidency
            fields:
              - id: district
                label: District
                type: selectBox
                optionsSource:
                  type: formData
                  formId: md03district
        ```

        Args:
            yaml_spec: YAML string defining the form package

        Returns:
            Dictionary with:
                - success: bool
                - package_id: str
                - forms: dict[form_id, joget_json]
                - errors: list[str] (if any)
        """
        try:
            spec = yaml.safe_load(yaml_spec)

            if not spec:
                return {"success": False, "error": "Empty or invalid YAML specification"}

            package_info = spec.get("package", {})
            package_id = package_info.get("id", "formPackage")

            results = {}
            errors = []

            # Generate main wizard form if specified
            main_form_spec = spec.get("mainForm")
            if main_form_spec:
                try:
                    main_form_json = self._generate_wizard_form(main_form_spec)
                    form_id = main_form_spec.get("id", "mainForm")
                    results[form_id] = main_form_json
                except Exception as e:
                    errors.append(f"Main form generation failed: {e}")

            # Generate subforms
            sub_forms = spec.get("subForms", [])
            for sub_form_spec in sub_forms:
                try:
                    # Ensure parent_id hidden field is present
                    sub_form_spec = self._ensure_parent_id_field(sub_form_spec)

                    # Generate the form
                    forms = self.engine.generate(sub_form_spec)
                    results.update(forms)
                except Exception as e:
                    form_id = sub_form_spec.get("form", {}).get("id", "unknown")
                    errors.append(f"Subform '{form_id}': {e}")

            return {
                "success": len(results) > 0,
                "package_id": package_id,
                "package_name": package_info.get("name", package_id),
                "forms": results,
                "form_count": len(results),
                "errors": errors if errors else None,
                "message": f"Generated {len(results)} form(s) for package '{package_id}'"
                + (f" with {len(errors)} error(s)" if errors else ""),
            }

        except yaml.YAMLError as e:
            return {"success": False, "error": f"Invalid YAML syntax: {e}"}
        except Exception as e:
            logger.exception("Unexpected error during package generation")
            return {"success": False, "error": f"Package generation failed: {e}"}

    def _generate_wizard_form(self, main_form_spec: dict[str, Any]) -> dict[str, Any]:
        """Generate the main wizard form with MultiPagedForm element."""
        wizard_spec = main_form_spec.get("wizard", {})
        pages = wizard_spec.get("pages", [])

        # Build the YAML spec for the main form
        form_spec = {
            "form": {
                "id": main_form_spec.get("id"),
                "name": main_form_spec.get("name"),
                "tableName": main_form_spec.get("tableName", main_form_spec.get("id")),
                "description": main_form_spec.get("description", ""),
            },
            "fields": [
                {
                    "id": wizard_spec.get("id", "wizard"),
                    "label": "",
                    "type": "multiPagedForm",
                    "displayMode": wizard_spec.get("displayMode", "tab"),
                    "partiallyStore": wizard_spec.get("partiallyStore", False),
                    "storeMainFormOnPartiallyStore": wizard_spec.get(
                        "storeMainFormOnPartiallyStore", True
                    ),
                    "onlyAllowSubmitOnLastPage": wizard_spec.get(
                        "onlyAllowSubmitOnLastPage", False
                    ),
                    "prevButtonLabel": wizard_spec.get("prevButtonLabel", "Previous"),
                    "nextButtonLabel": wizard_spec.get("nextButtonLabel", "Next"),
                    "pages": pages,
                }
            ],
        }

        # Add any hidden fields for status tracking
        hidden_fields = main_form_spec.get("hiddenFields", [])
        for hf in hidden_fields:
            form_spec["fields"].insert(
                0,
                {
                    "id": hf.get("id"),
                    "label": hf.get("label", ""),
                    "type": "hiddenField",
                    "defaultValue": hf.get("defaultValue", ""),
                },
            )

        # Generate using the engine
        forms = self.engine.generate(form_spec)
        return list(forms.values())[0]

    def _ensure_parent_id_field(self, sub_form_spec: dict[str, Any]) -> dict[str, Any]:
        """Ensure the subform has a parent_id hidden field for linking."""
        fields = sub_form_spec.get("fields", [])

        # Check if parent_id already exists
        has_parent_id = any(f.get("id") == "parent_id" for f in fields)

        if not has_parent_id:
            # Add parent_id as the first field
            parent_id_field = {
                "id": "parent_id",
                "label": "",
                "type": "hiddenField",
            }
            sub_form_spec["fields"] = [parent_id_field] + fields

        return sub_form_spec
