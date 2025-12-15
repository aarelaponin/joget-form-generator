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
