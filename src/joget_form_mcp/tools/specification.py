"""
Specification tools for MCP server.

Provides tools to create and modify YAML form specifications.
"""

import logging
import re
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)


# Field type inference patterns
FIELD_INFERENCE_PATTERNS = {
    # Email patterns
    r"email|e-mail": ("textField", {"validator": {"type": "email"}}),
    # Date patterns
    r"date|birth|dob|deadline|due": ("datePicker", {"dateFormat": "yyyy-MM-dd"}),
    # Phone patterns
    r"phone|mobile|tel|fax": ("textField", {"validator": {"type": "numeric"}}),
    # Status/category patterns
    r"status|category|type|level|priority": ("selectBox", {}),
    # Yes/No patterns
    r"is_|has_|can_|allow|enable|active": ("checkBox", {}),
    # Description/notes patterns
    r"description|notes|comments|remarks|message|content": ("textArea", {"rows": 5}),
    # Password patterns
    r"password|pin|secret": ("passwordField", {}),
    # ID/code patterns
    r"id$|_id$|code$|number$|no$": ("textField", {}),
    # File patterns
    r"file|document|attachment|upload|image|photo": ("fileUpload", {}),
    # Amount/price patterns
    r"amount|price|cost|total|subtotal|tax|fee": ("textField", {"validator": {"type": "numeric"}}),
    # Quantity patterns
    r"quantity|qty|count|number": ("textField", {"validator": {"type": "numeric"}}),
}


class SpecificationTools:
    """Tools for creating and modifying form specifications."""

    def create_form_spec(
        self, description: str, form_id: Optional[str] = None, form_name: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Generate a YAML form specification from natural language description.

        Args:
            description: Natural language description of the form
            form_id: Optional form ID (generated if not provided)
            form_name: Optional form name (generated if not provided)

        Returns:
            Dictionary with YAML spec and metadata
        """
        # Extract field hints from description
        fields = self._extract_fields_from_description(description)

        if not fields:
            return {
                "success": False,
                "error": "Could not identify any fields from the description. "
                "Please include field names like 'name', 'email', 'status', etc.",
            }

        # Generate form ID and name if not provided
        if not form_id:
            form_id = self._generate_form_id(description)
        if not form_name:
            form_name = self._generate_form_name(description)

        # Build specification
        spec = {
            "form": {
                "id": form_id,
                "name": form_name,
                "description": description[:200] if len(description) > 200 else description,
            },
            "fields": fields,
        }

        yaml_spec = yaml.dump(spec, default_flow_style=False, sort_keys=False, allow_unicode=True)

        return {
            "success": True,
            "yaml_spec": yaml_spec,
            "form_id": form_id,
            "form_name": form_name,
            "field_count": len(fields),
            "fields_detected": [f["id"] for f in fields],
            "message": f"Generated specification with {len(fields)} fields",
        }

    def create_cascading_dropdown_spec(
        self,
        parent_form_id: str,
        child_form_id: str,
        parent_label_field: str = "name",
        parent_value_field: str = "code",
        child_fk_field: str = "categoryCode",
    ) -> dict[str, Any]:
        """
        Generate YAML specification for cascading dropdown pattern.

        Args:
            parent_form_id: ID of parent form
            child_form_id: ID of child form
            parent_label_field: Field to display in dropdown
            parent_value_field: Field to store as value
            child_fk_field: Foreign key field in child

        Returns:
            Dictionary with parent and child YAML specs
        """
        # Generate parent form spec
        parent_spec = {
            "form": {
                "id": parent_form_id,
                "name": self._id_to_name(parent_form_id),
                "description": f"Parent lookup table for {child_form_id}",
            },
            "fields": [
                {
                    "id": parent_value_field,
                    "label": parent_value_field.title(),
                    "type": "textField",
                    "required": True,
                },
                {
                    "id": parent_label_field,
                    "label": parent_label_field.title(),
                    "type": "textField",
                    "required": True,
                },
            ],
        }

        # Generate child form spec
        child_spec = {
            "form": {
                "id": child_form_id,
                "name": self._id_to_name(child_form_id),
                "description": f"Child form with cascading dropdown from {parent_form_id}",
            },
            "fields": [
                {"id": "code", "label": "Code", "type": "textField", "required": True},
                {"id": "name", "label": "Name", "type": "textField", "required": True},
                {
                    "id": child_fk_field,
                    "label": self._id_to_name(parent_form_id),
                    "type": "selectBox",
                    "required": True,
                    "optionsSource": {
                        "type": "formData",
                        "formId": parent_form_id,
                        "valueColumn": parent_value_field,
                        "labelColumn": parent_label_field,
                    },
                },
            ],
        }

        parent_yaml = yaml.dump(parent_spec, default_flow_style=False, sort_keys=False)
        child_yaml = yaml.dump(child_spec, default_flow_style=False, sort_keys=False)

        return {
            "success": True,
            "parent_spec": parent_yaml,
            "child_spec": child_yaml,
            "parent_form_id": parent_form_id,
            "child_form_id": child_form_id,
            "relationship": f"{parent_form_id}.{parent_value_field} → {child_form_id}.{child_fk_field}",
            "message": "Generated cascading dropdown pattern with parent and child forms",
        }

    def add_field_to_spec(
        self, yaml_spec: str, field_description: str, position: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Add a new field to an existing YAML specification.

        Args:
            yaml_spec: Existing YAML specification
            field_description: Description of field to add
            position: Position to insert (default: end)

        Returns:
            Dictionary with updated YAML spec
        """
        try:
            spec = yaml.safe_load(yaml_spec)
        except yaml.YAMLError as e:
            return {"success": False, "error": f"Invalid YAML: {e}"}

        if "fields" not in spec:
            spec["fields"] = []

        # Extract field info from description
        field = self._infer_field_from_description(field_description)

        if not field:
            return {
                "success": False,
                "error": f"Could not infer field from description: '{field_description}'",
            }

        # Insert at position
        if position is not None and 0 <= position < len(spec["fields"]):
            spec["fields"].insert(position, field)
        else:
            spec["fields"].append(field)

        updated_yaml = yaml.dump(
            spec, default_flow_style=False, sort_keys=False, allow_unicode=True
        )

        return {
            "success": True,
            "yaml_spec": updated_yaml,
            "added_field": field,
            "field_count": len(spec["fields"]),
            "message": f"Added field '{field['id']}' ({field['type']})",
        }

    def _extract_fields_from_description(self, description: str) -> list[dict]:
        """Extract field definitions from natural language description."""
        fields = []

        # Common field patterns to look for
        field_patterns = [
            # "field_name field" or "the field_name"
            r"\b(name|email|phone|address|city|state|country|zip|date|status|"
            r"description|notes|comments|title|first\s*name|last\s*name|"
            r"password|username|id|code|amount|price|quantity|type|category|"
            r"message|content|file|document|birth\s*date|due\s*date)\b",
        ]

        description_lower = description.lower()

        # Find mentioned fields
        found_fields = set()
        for pattern in field_patterns:
            matches = re.findall(pattern, description_lower)
            found_fields.update(matches)

        # Also look for explicit field mentions
        explicit_patterns = [
            r"fields?:\s*([^.]+)",
            r"include(?:s|ing)?:?\s*([^.]+)",
            r"with\s+([^.]+?)\s+fields?",
        ]

        for pattern in explicit_patterns:
            match = re.search(pattern, description_lower)
            if match:
                # Split on common delimiters
                parts = re.split(r"[,\s]+(?:and\s+)?", match.group(1))
                for part in parts:
                    clean = part.strip()
                    if clean and len(clean) > 2:
                        found_fields.add(clean)

        # Convert found fields to specifications
        for field_name in found_fields:
            field = self._infer_field_from_description(field_name)
            if field:
                fields.append(field)

        # Sort by a reasonable order
        priority_fields = ["id", "code", "name", "firstName", "lastName", "email", "phone"]
        fields.sort(
            key=lambda f: (
                priority_fields.index(f["id"]) if f["id"] in priority_fields else 100,
                f["id"],
            )
        )

        return fields

    def _infer_field_from_description(self, description: str) -> Optional[dict]:
        """Infer field configuration from description."""
        description_lower = description.lower().strip()

        # Clean up the description to get field ID
        field_id = re.sub(r"[^a-z0-9]+", "_", description_lower).strip("_")

        # Handle common multi-word fields
        field_id = field_id.replace("first_name", "firstName")
        field_id = field_id.replace("last_name", "lastName")
        field_id = field_id.replace("birth_date", "birthDate")
        field_id = field_id.replace("due_date", "dueDate")

        # Convert to camelCase
        parts = field_id.split("_")
        field_id = parts[0] + "".join(p.capitalize() for p in parts[1:])

        if not field_id:
            return None

        # Infer field type
        field_type = "textField"
        extra_props = {}

        for pattern, (inferred_type, props) in FIELD_INFERENCE_PATTERNS.items():
            if re.search(pattern, description_lower):
                field_type = inferred_type
                extra_props = props.copy()
                break

        # Build field definition
        field = {
            "id": field_id,
            "label": self._id_to_label(field_id),
            "type": field_type,
        }

        # Add common properties
        if "required" in description_lower or "mandatory" in description_lower:
            field["required"] = True

        # Add inferred properties
        field.update(extra_props)

        return field

    def _generate_form_id(self, description: str) -> str:
        """Generate a form ID from description."""
        # Extract key words
        words = re.findall(r"\b[a-z]+\b", description.lower())

        # Filter common words
        stop_words = {"a", "an", "the", "for", "with", "and", "or", "to", "of", "in", "on", "form"}
        key_words = [w for w in words if w not in stop_words][:3]

        if key_words:
            return "".join(w.capitalize() for w in key_words) + "Form"
        return "generatedForm"

    def _generate_form_name(self, description: str) -> str:
        """Generate a form name from description."""
        # Take first sentence or phrase
        match = re.match(r"^(.+?)[.!?]", description)
        if match:
            name = match.group(1)
        else:
            name = description[:50]

        # Clean up
        name = name.strip()
        if len(name) > 50:
            name = name[:47] + "..."

        return name.title()

    def _id_to_label(self, field_id: str) -> str:
        """Convert camelCase ID to human-readable label."""
        # Insert space before capitals
        label = re.sub(r"([a-z])([A-Z])", r"\1 \2", field_id)
        # Insert space before numbers
        label = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", label)
        return label.title()

    def _id_to_name(self, form_id: str) -> str:
        """Convert form ID to human-readable name."""
        # Handle MDM patterns like "md25equipCategory"
        match = re.match(r"md(\d+)(.+)", form_id, re.IGNORECASE)
        if match:
            num = match.group(1)
            rest = match.group(2)
            name = re.sub(r"([a-z])([A-Z])", r"\1 \2", rest)
            return f"MD.{num} - {name.title()}"

        # General conversion
        name = re.sub(r"([a-z])([A-Z])", r"\1 \2", form_id)
        name = name.replace("_", " ").replace("-", " ")
        return name.title()
