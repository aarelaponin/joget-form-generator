"""Section pattern for grouping form fields into sections."""

from typing import Any, ClassVar
from .base import BasePattern


class SectionPattern(BasePattern):
    """
    Pattern for section elements.

    Section is a special marker type that tells the engine to start a new
    section in the form. The engine handles the actual section structure -
    this pattern just returns None since sections are containers, not fields.

    In Joget, sections use className: org.joget.apps.form.model.Section
    """

    template_name: ClassVar[str] = "section.j2"

    # Mark this as a structural element, not a field
    is_structural: ClassVar[bool] = True

    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for Section.

        Args:
            field: Field specification with properties:
                - id: Section ID
                - label: Section label/title
                - type: "section"
            context: Rendering context

        Returns:
            Template context dictionary
        """
        return {
            "id": field["id"],
            "label": field.get("label", ""),
        }
