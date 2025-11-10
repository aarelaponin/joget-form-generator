"""CLI entry point for joget-form-generator."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="joget-form-gen",
    help="Generate Joget DX forms from YAML specifications",
    add_completion=False,
)
console = Console()


@app.command()
def generate(
    spec_file: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to YAML specification file",
    ),
    output_dir: Path = typer.Option(
        Path("./generated_forms"),
        "--output",
        "-o",
        help="Output directory for generated forms",
    ),
    validate_only: bool = typer.Option(
        False, "--validate-only", help="Only validate spec, don't generate forms"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed progress and debug info"
    ),
):
    """
    Generate Joget form JSON from YAML specification.

    Example:
        joget-form-gen generate myform.yaml -o output/
    """

    console.print(
        Panel.fit("[bold blue]Joget Form Generator[/bold blue]", subtitle="v0.1.0")
    )
    console.print(f"📄 Specification: [cyan]{spec_file}[/cyan]")

    # Import here to avoid slow startup
    import yaml
    import json

    # Phase 1: Load YAML
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Loading specification...", total=None)

        try:
            with open(spec_file) as f:
                spec = yaml.safe_load(f)
        except yaml.YAMLError as e:
            console.print(f"[bold red]❌ YAML parsing failed:[/bold red]")
            console.print(f"  {e}")
            raise typer.Exit(code=1)

        progress.update(task, completed=True)

    # Phase 2: Validate
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Validating against schema...", total=None)

        from ..validators import DualValidator

        validator = DualValidator()
        result, form_spec = validator.validate(spec)

        progress.update(task, completed=True)

    # Show validation results
    if not result.valid:
        console.print("[bold red]❌ Validation failed:[/bold red]")
        for error in result.errors:
            console.print(f"  • {error}", style="red")
        raise typer.Exit(code=1)

    if result.warnings:
        console.print("[yellow]⚠️  Warnings:[/yellow]")
        for warning in result.warnings:
            console.print(f"  • {warning}", style="yellow")

    console.print("[green]✓ Validation passed[/green]")

    if validate_only:
        console.print(
            "\n[bold green]✓ Validation complete (no forms generated)[/bold green]"
        )
        return

    # Phase 3: Generate forms
    output_dir.mkdir(parents=True, exist_ok=True)

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Generating forms...", total=None)

        try:
            # Import transform engine
            from ..transformers.engine import TransformEngine

            engine = TransformEngine()
            forms = engine.generate(spec)
        except Exception as e:
            console.print(f"[bold red]❌ Generation failed:[/bold red]")
            console.print(f"  {e}")
            if verbose:
                import traceback

                console.print("\n[yellow]Stack trace:[/yellow]")
                console.print(traceback.format_exc())
            raise typer.Exit(code=1)

        # Write output files
        generated_files = []
        for form_id, form_json in forms.items():
            output_file = output_dir / f"{form_id}.json"

            with open(output_file, "w") as f:
                json.dump(form_json, f, indent=2, ensure_ascii=False)

            generated_files.append(output_file)

            if verbose:
                console.print(f"  Generated: [cyan]{output_file}[/cyan]")

        progress.update(task, completed=True)

    # Summary table
    table = Table(title="Generation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Forms Generated", str(len(forms)))
    table.add_row("Output Directory", str(output_dir))
    table.add_row(
        "Total Fields", str(sum(len(f.get("elements", [])) for f in forms.values()))
    )

    console.print()
    console.print(table)

    console.print(f"\n[bold green]✓ Generation complete![/bold green]")


@app.command()
def validate(
    spec_file: Path = typer.Argument(
        ..., exists=True, dir_okay=False, readable=True, help="Path to YAML specification file"
    )
):
    """
    Validate specification without generating forms.

    Example:
        joget-form-gen validate myform.yaml
    """
    # Delegate to generate with validate_only=True
    generate(spec_file=spec_file, validate_only=True)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit", is_eager=True
    ),
):
    """Joget Form Generator CLI."""
    if version:
        from .. import __version__

        console.print(f"joget-form-generator version {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print("[yellow]No command specified. Use --help for usage.[/yellow]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
