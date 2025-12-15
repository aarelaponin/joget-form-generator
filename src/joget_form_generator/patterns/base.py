"""Base pattern class for field generation."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar
import json

from jinja2 import Environment, PackageLoader, select_autoescape, TemplateNotFound


class BasePattern(ABC):
    """Base class for all field patterns."""

    # Subclasses must define template filename
    template_name: ClassVar[str]

    def __init__(self):
        """Initialize pattern with Jinja2 environment."""
        self.env = Environment(
            loader=PackageLoader("joget_form_generator", "patterns/templates"),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Add custom filters
        self.env.filters["tojson_pretty"] = self._tojson_pretty
        self.env.filters["to_joget_bool"] = self._to_joget_bool

    def render(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Render field JSON from template.

        Args:
            field: Field specification from canonical format
            context: Additional context (form metadata, etc.)

        Returns:
            Joget field JSON structure

        Raises:
            TemplateNotFound: If template file doesn't exist
            ValueError: If rendered template is invalid JSON
        """
        # Prepare template context
        template_context = self._prepare_context(field, context)

        # Render template
        try:
            template = self.env.get_template(self.template_name)
            rendered = template.render(**template_context)
        except TemplateNotFound:
            raise TemplateNotFound(
                f"Template '{self.template_name}' not found for {self.__class__.__name__}"
            )

        # Parse JSON from rendered template
        try:
            field_json = json.loads(rendered)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Rendered template '{self.template_name}' is invalid JSON: {e}\n"
                f"Rendered content:\n{rendered}"
            )

        # Post-process
        return self._post_process(field_json, field, context)

    @abstractmethod
    def _prepare_context(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Prepare context for template rendering.

        Subclasses override to add field-specific context.

        Args:
            field: Field specification
            context: Global context

        Returns:
            Template context dictionary
        """
        pass

    def _post_process(
        self, field_json: dict[str, Any], field: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Post-process rendered JSON.

        Override to add custom logic after template rendering.
        Default implementation returns field_json unchanged.
        """
        return field_json

    @staticmethod
    def _tojson_pretty(value: Any) -> str:
        """Jinja2 filter for pretty JSON formatting."""
        return json.dumps(value, indent=2, ensure_ascii=False)

    @staticmethod
    def _to_joget_bool(value: bool) -> str:
        """
        Convert Python boolean to Joget boolean string.

        Joget uses "true" for true, "" (empty string) for false.
        """
        return "true" if value else ""
