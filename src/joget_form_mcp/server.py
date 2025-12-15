"""
MCP Server for Joget Form Generator.

This server exposes Joget form generation capabilities through the Model Context Protocol,
enabling AI assistants to help users design and validate Joget DX forms.

Tools provided:
- generate_form: Transform YAML specification to Joget JSON
- validate_spec: Validate YAML against JSON Schema
- list_field_types: List supported field types with documentation
- create_form_spec: Generate YAML from natural language description

Resources provided:
- Field type documentation
- Example specifications
- Cascading dropdown patterns
"""

import json
import logging
from typing import Any, Sequence

import yaml
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)
from pydantic import AnyUrl

from .tools.generation import GenerationTools
from .tools.validation import ValidationTools
from .tools.discovery import DiscoveryTools
from .tools.specification import SpecificationTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_server() -> Server:
    """Create and configure the MCP server with all tools."""
    server = Server("joget-form-generator")

    # Initialize tool handlers
    generation_tools = GenerationTools()
    validation_tools = ValidationTools()
    discovery_tools = DiscoveryTools()
    specification_tools = SpecificationTools()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return [
            # Generation tools
            Tool(
                name="generate_form",
                description=(
                    "Generate Joget DX form JSON from a YAML specification. "
                    "Takes a YAML string defining form metadata and fields, "
                    "returns production-ready Joget JSON that can be imported via FormCreator."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "yaml_spec": {
                            "type": "string",
                            "description": "YAML specification for the form"
                        }
                    },
                    "required": ["yaml_spec"]
                }
            ),
            Tool(
                name="generate_multiple_forms",
                description=(
                    "Generate multiple Joget forms from a multi-form YAML specification. "
                    "Useful for creating related forms like parent-child hierarchies."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "yaml_spec": {
                            "type": "string",
                            "description": "YAML specification with multiple form definitions"
                        }
                    },
                    "required": ["yaml_spec"]
                }
            ),

            # Validation tools
            Tool(
                name="validate_spec",
                description=(
                    "Validate a YAML form specification against JSON Schema and Pydantic models. "
                    "Returns detailed validation errors if the spec is invalid."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "yaml_spec": {
                            "type": "string",
                            "description": "YAML specification to validate"
                        }
                    },
                    "required": ["yaml_spec"]
                }
            ),
            Tool(
                name="validate_joget_json",
                description=(
                    "Validate generated Joget JSON structure for correctness. "
                    "Checks that the JSON follows Joget's expected format."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "joget_json": {
                            "type": "string",
                            "description": "Joget form JSON to validate"
                        }
                    },
                    "required": ["joget_json"]
                }
            ),

            # Discovery tools
            Tool(
                name="list_field_types",
                description=(
                    "List all supported Joget field types with descriptions. "
                    "Returns field types grouped by category (standard, advanced, enterprise)."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_field_type_info",
                description=(
                    "Get detailed information about a specific field type including "
                    "all available properties, examples, and usage patterns."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "field_type": {
                            "type": "string",
                            "description": "Field type name (e.g., 'textField', 'selectBox', 'calculationField')"
                        }
                    },
                    "required": ["field_type"]
                }
            ),
            Tool(
                name="get_example_spec",
                description=(
                    "Get an example YAML specification for a specific use case. "
                    "Available examples: simple_form, cascading_dropdown, master_detail, "
                    "mdm_form, calculation_form, multi_page_form."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "example_name": {
                            "type": "string",
                            "description": "Name of the example to retrieve"
                        }
                    },
                    "required": ["example_name"]
                }
            ),

            # Specification tools
            Tool(
                name="create_form_spec",
                description=(
                    "Generate a YAML form specification from a natural language description. "
                    "Analyzes the description to determine appropriate field types, "
                    "validations, and structure."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Natural language description of the form to create"
                        },
                        "form_id": {
                            "type": "string",
                            "description": "ID for the form (optional, will be generated if not provided)"
                        },
                        "form_name": {
                            "type": "string",
                            "description": "Display name for the form (optional)"
                        }
                    },
                    "required": ["description"]
                }
            ),
            Tool(
                name="create_cascading_dropdown_spec",
                description=(
                    "Generate YAML specification for cascading dropdown pattern. "
                    "Creates parent-child form relationship with dynamic filtering."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "parent_form_id": {
                            "type": "string",
                            "description": "ID of the parent form (e.g., 'md25equipCategory')"
                        },
                        "child_form_id": {
                            "type": "string",
                            "description": "ID of the child form (e.g., 'md25equipment')"
                        },
                        "parent_label_field": {
                            "type": "string",
                            "description": "Field in parent form to display as label"
                        },
                        "parent_value_field": {
                            "type": "string",
                            "description": "Field in parent form to use as value"
                        },
                        "child_fk_field": {
                            "type": "string",
                            "description": "Foreign key field in child form"
                        }
                    },
                    "required": ["parent_form_id", "child_form_id"]
                }
            ),
            Tool(
                name="add_field_to_spec",
                description=(
                    "Add a new field to an existing YAML specification. "
                    "Automatically determines field type and properties based on description."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "yaml_spec": {
                            "type": "string",
                            "description": "Existing YAML specification"
                        },
                        "field_description": {
                            "type": "string",
                            "description": "Description of the field to add"
                        },
                        "position": {
                            "type": "integer",
                            "description": "Position to insert field (0-based, default: end)"
                        }
                    },
                    "required": ["yaml_spec", "field_description"]
                }
            ),

        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
        """Handle tool calls."""
        try:
            # Generation tools
            if name == "generate_form":
                result = generation_tools.generate_form(arguments["yaml_spec"])
            elif name == "generate_multiple_forms":
                result = generation_tools.generate_multiple_forms(arguments["yaml_spec"])

            # Validation tools
            elif name == "validate_spec":
                result = validation_tools.validate_spec(arguments["yaml_spec"])
            elif name == "validate_joget_json":
                result = validation_tools.validate_joget_json(arguments["joget_json"])

            # Discovery tools
            elif name == "list_field_types":
                result = discovery_tools.list_field_types()
            elif name == "get_field_type_info":
                result = discovery_tools.get_field_type_info(arguments["field_type"])
            elif name == "get_example_spec":
                result = discovery_tools.get_example_spec(arguments["example_name"])

            # Specification tools
            elif name == "create_form_spec":
                result = specification_tools.create_form_spec(
                    arguments["description"],
                    arguments.get("form_id"),
                    arguments.get("form_name")
                )
            elif name == "create_cascading_dropdown_spec":
                result = specification_tools.create_cascading_dropdown_spec(
                    arguments["parent_form_id"],
                    arguments["child_form_id"],
                    arguments.get("parent_label_field", "name"),
                    arguments.get("parent_value_field", "code"),
                    arguments.get("child_fk_field", "categoryCode")
                )
            elif name == "add_field_to_spec":
                result = specification_tools.add_field_to_spec(
                    arguments["yaml_spec"],
                    arguments["field_description"],
                    arguments.get("position")
                )

            else:
                result = {"error": f"Unknown tool: {name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            logger.exception(f"Error in tool {name}")
            error_result = {
                "error": str(e),
                "tool": name,
                "arguments": arguments
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List available resources (documentation, examples)."""
        return [
            Resource(
                uri=AnyUrl("joget://docs/field-types"),
                name="Field Types Documentation",
                description="Complete documentation for all supported Joget field types",
                mimeType="text/markdown"
            ),
            Resource(
                uri=AnyUrl("joget://docs/cascading-dropdowns"),
                name="Cascading Dropdowns Guide",
                description="How to create cascading dropdown patterns (nested LOV)",
                mimeType="text/markdown"
            ),
            Resource(
                uri=AnyUrl("joget://examples/simple-form"),
                name="Simple Form Example",
                description="Basic form with text fields and select box",
                mimeType="text/yaml"
            ),
            Resource(
                uri=AnyUrl("joget://examples/mdm-form"),
                name="MDM Form Example",
                description="Master Data Management form with cascading dropdowns",
                mimeType="text/yaml"
            ),
            Resource(
                uri=AnyUrl("joget://examples/enterprise-showcase"),
                name="Enterprise Features Showcase",
                description="Form demonstrating calculation fields, rich text, form grid",
                mimeType="text/yaml"
            ),
        ]

    @server.read_resource()
    async def read_resource(uri: AnyUrl) -> str:
        """Read a resource by URI."""
        uri_str = str(uri)

        if uri_str == "joget://docs/field-types":
            return discovery_tools.get_field_types_documentation()
        elif uri_str == "joget://docs/cascading-dropdowns":
            return discovery_tools.get_cascading_dropdown_documentation()
        elif uri_str.startswith("joget://examples/"):
            example_name = uri_str.replace("joget://examples/", "")
            result = discovery_tools.get_example_spec(example_name)
            return result.get("yaml_spec", f"Example not found: {example_name}")
        else:
            return f"Resource not found: {uri}"

    return server


async def main():
    """Run the MCP server."""
    import mcp.server.stdio

    server = create_server()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="joget-form-generator",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
