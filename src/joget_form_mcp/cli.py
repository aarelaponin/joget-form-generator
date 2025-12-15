"""
CLI entry point for Joget Form Generator MCP Server.

Usage:
    joget-form-mcp                 # Run MCP server (stdio transport)
    joget-form-mcp --version       # Show version
    joget-form-mcp --help          # Show help
"""

import asyncio
import sys

import typer

from . import __version__

app = typer.Typer(
    name="joget-form-mcp",
    help="MCP Server for Joget Form Generator - AI-assisted form development",
    add_completion=False,
)


@app.command()
def serve(
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
):
    """
    Start the Joget Form Generator MCP server.

    The server communicates via stdio and provides tools for:
    - Generating Joget forms from YAML specifications
    - Validating specifications and Joget JSON
    - Deploying forms to Joget instances
    - Discovering field types and examples
    """
    if version:
        typer.echo(f"joget-form-mcp version {__version__}")
        raise typer.Exit()

    # Configure logging
    import logging

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,  # Log to stderr, stdout is for MCP protocol
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Starting Joget Form Generator MCP Server v{__version__}")

    # Run the server
    from .server import main as server_main

    asyncio.run(server_main())


@app.command("tools")
def list_tools():
    """List all available MCP tools."""
    from .tools import (
        GenerationTools,
        ValidationTools,
        DiscoveryTools,
        SpecificationTools,
    )

    tools = [
        (
            "Generation",
            [
                ("generate_form", "Generate Joget JSON from YAML specification"),
                ("generate_multiple_forms", "Generate multiple forms from multi-form spec"),
            ],
        ),
        (
            "Validation",
            [
                ("validate_spec", "Validate YAML against JSON Schema"),
                ("validate_joget_json", "Validate Joget JSON structure"),
            ],
        ),
        (
            "Discovery",
            [
                ("list_field_types", "List supported field types"),
                ("get_field_type_info", "Get detailed field type documentation"),
                ("get_example_spec", "Get example YAML specifications"),
            ],
        ),
        (
            "Specification",
            [
                ("create_form_spec", "Generate YAML from natural language"),
                ("create_cascading_dropdown_spec", "Generate cascading dropdown pattern"),
                ("add_field_to_spec", "Add field to existing specification"),
            ],
        ),
    ]

    typer.echo("\n🔧 Joget Form Generator MCP Tools\n")
    typer.echo("=" * 60)

    for category, tool_list in tools:
        typer.echo(f"\n📁 {category}")
        typer.echo("-" * 40)
        for name, description in tool_list:
            typer.echo(f"  • {name}")
            typer.echo(f"    {description}")

    typer.echo("\n" + "=" * 60)
    typer.echo("\nUse 'joget-form-mcp serve' to start the MCP server")


@app.command("examples")
def list_examples():
    """List available example specifications."""
    from .tools.discovery import EXAMPLES

    typer.echo("\n📄 Available Example Specifications\n")
    typer.echo("=" * 60)

    for name, content in EXAMPLES.items():
        # Extract first line as description
        first_line = content.strip().split("\n")[0]
        if first_line.startswith("#"):
            description = first_line[1:].strip()
        else:
            description = name

        typer.echo(f"\n  • {name}")
        typer.echo(f"    {description}")

    typer.echo("\n" + "=" * 60)
    typer.echo("\nUse 'joget-form-mcp example <name>' to view an example")


@app.command("example")
def show_example(
    name: str = typer.Argument(..., help="Example name to display"),
):
    """Display an example specification."""
    from .tools.discovery import DiscoveryTools

    discovery = DiscoveryTools()
    result = discovery.get_example_spec(name)

    if "error" in result:
        typer.echo(f"❌ {result['error']}", err=True)
        typer.echo(f"\nAvailable examples: {', '.join(result.get('available_examples', []))}")
        raise typer.Exit(1)

    typer.echo(result["yaml_spec"])


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
