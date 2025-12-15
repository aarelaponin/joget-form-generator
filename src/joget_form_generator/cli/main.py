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

    console.print(Panel.fit("[bold blue]Joget Form Generator[/bold blue]", subtitle="v0.1.0"))
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
        console.print("\n[bold green]✓ Validation complete (no forms generated)[/bold green]")
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
    table.add_row("Total Fields", str(sum(len(f.get("elements", [])) for f in forms.values())))

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


@app.command(name="generate-from-excel")
def generate_from_excel(
    excel_file: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to Excel file (.xlsx) or CSV file (.csv)",
    ),
    output_dir: Path = typer.Option(
        Path("./generated_forms"),
        "--output",
        "-o",
        help="Output directory for generated forms",
    ),
    sheet_name: Optional[str] = typer.Option(
        None,
        "--sheet",
        "-s",
        help="Sheet name to read from Excel (default: first sheet)",
    ),
    form_id: Optional[str] = typer.Option(
        None,
        "--form-id",
        help="Override form ID from spreadsheet",
    ),
    form_name: Optional[str] = typer.Option(
        None,
        "--form-name",
        help="Override form name from spreadsheet",
    ),
    save_yaml: bool = typer.Option(
        False,
        "--save-yaml",
        help="Also save intermediate YAML specification",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed progress and debug info"
    ),
):
    """
    Generate Joget form from Excel/CSV spreadsheet.

    Expected spreadsheet format:

    \b
    | Form ID | Form Name | Field ID | Field Label | Field Type | Required | Options |
    |---------|-----------|----------|-------------|------------|----------|---------|
    | myForm  | My Form   | field1   | Field 1     | textField  | Yes      |         |

    Example:
        joget-form-gen generate-from-excel customers.xlsx -o output/
        joget-form-gen generate-from-excel data.csv --sheet "Form Definition"
    """
    import json
    import yaml

    console.print(
        Panel.fit(
            "[bold blue]Joget Form Generator[/bold blue]\n[dim]Excel/CSV Import[/dim]",
            subtitle="v0.1.0",
        )
    )
    console.print(f"📊 Spreadsheet: [cyan]{excel_file}[/cyan]")

    # Phase 1: Load from Excel/CSV
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Loading spreadsheet...", total=None)

        try:
            from ..loaders.spreadsheet import SpreadsheetLoader

            # Detect file type
            if excel_file.suffix.lower() == ".csv":
                spec = SpreadsheetLoader.from_csv(
                    str(excel_file), form_id=form_id, form_name=form_name
                )
            else:
                spec = SpreadsheetLoader.from_excel(
                    str(excel_file),
                    sheet_name=sheet_name,
                    form_id=form_id,
                    form_name=form_name,
                )
        except FileNotFoundError as e:
            console.print(f"[bold red]❌ File not found:[/bold red]")
            console.print(f"  {e}")
            raise typer.Exit(code=1)
        except ValueError as e:
            console.print(f"[bold red]❌ Invalid spreadsheet format:[/bold red]")
            console.print(f"  {e}")
            raise typer.Exit(code=1)
        except Exception as e:
            console.print(f"[bold red]❌ Failed to load spreadsheet:[/bold red]")
            console.print(f"  {e}")
            if verbose:
                import traceback

                console.print("\n[yellow]Stack trace:[/yellow]")
                console.print(traceback.format_exc())
            raise typer.Exit(code=1)

        progress.update(task, completed=True)

    console.print(f"[green]✓ Loaded {len(spec['fields'])} fields[/green]")

    # Save intermediate YAML if requested
    if save_yaml:
        yaml_file = output_dir / f"{spec['form']['id']}_spec.yaml"
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(yaml_file, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        console.print(f"[dim]Saved specification: {yaml_file}[/dim]")

    # Phase 2: Validate
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Validating specification...", total=None)

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

    # Phase 3: Generate forms
    output_dir.mkdir(parents=True, exist_ok=True)

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Generating forms...", total=None)

        try:
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
        for form_id_key, form_json in forms.items():
            output_file = output_dir / f"{form_id_key}.json"

            with open(output_file, "w") as f:
                json.dump(form_json, f, indent=2, ensure_ascii=False)

            if verbose:
                console.print(f"  Generated: [cyan]{output_file}[/cyan]")

        progress.update(task, completed=True)

    # Summary table
    table = Table(title="Generation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Forms Generated", str(len(forms)))
    table.add_row("Output Directory", str(output_dir))
    table.add_row("Total Fields", str(len(spec["fields"])))
    table.add_row("Source File", str(excel_file))

    console.print()
    console.print(table)

    console.print(f"\n[bold green]✓ Generation complete![/bold green]")


@app.command(name="generate-from-db")
def generate_from_db(
    connection_string: str = typer.Argument(
        ...,
        help="Database connection string (e.g., mysql://user:pass@localhost/db)",
    ),
    table_name: str = typer.Argument(
        ...,
        help="Table name to analyze",
    ),
    output_dir: Path = typer.Option(
        Path("./generated_forms"),
        "--output",
        "-o",
        help="Output directory for generated forms",
    ),
    form_id: Optional[str] = typer.Option(
        None,
        "--form-id",
        help="Override form ID (default: {tableName}Form)",
    ),
    form_name: Optional[str] = typer.Option(
        None,
        "--form-name",
        help="Override form name (default: humanized table name)",
    ),
    skip_columns: Optional[str] = typer.Option(
        None,
        "--skip",
        help="Comma-separated list of columns to skip",
    ),
    save_yaml: bool = typer.Option(
        False,
        "--save-yaml",
        help="Also save intermediate YAML specification",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed progress and debug info"
    ),
):
    """
    Generate Joget form from database table schema.

    Connects to a database, analyzes a table structure, and generates a form
    definition with appropriate field types based on column data types.

    Connection string examples:

    \b
    - MySQL:      mysql://user:password@localhost:3306/database
    - PostgreSQL: postgresql://user:password@localhost:5432/database
    - SQLite:     sqlite:///path/to/database.db

    Example:
        joget-form-gen generate-from-db "mysql://root@localhost/mydb" customers -o output/
        joget-form-gen generate-from-db "sqlite:///app.db" products --skip "created_at,updated_at"
    """
    import json
    import yaml

    console.print(
        Panel.fit(
            "[bold blue]Joget Form Generator[/bold blue]\n[dim]Database Schema Analysis[/dim]",
            subtitle="v0.1.0",
        )
    )
    console.print(
        f"🗄️  Database: [cyan]{connection_string.split('@')[-1] if '@' in connection_string else connection_string}[/cyan]"
    )
    console.print(f"📊 Table: [cyan]{table_name}[/cyan]")

    # Phase 1: Connect and analyze database
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Analyzing database schema...", total=None)

        try:
            from ..loaders.database import DatabaseSchemaAnalyzer

            analyzer = DatabaseSchemaAnalyzer(connection_string)

            # Parse skip_columns if provided
            skip_list = None
            if skip_columns:
                skip_list = [col.strip() for col in skip_columns.split(",")]

            spec = analyzer.analyze_table(
                table_name,
                form_id=form_id,
                form_name=form_name,
                skip_columns=skip_list,
            )

        except ValueError as e:
            console.print(f"[bold red]❌ Database analysis failed:[/bold red]")
            console.print(f"  {e}")
            raise typer.Exit(code=1)
        except Exception as e:
            console.print(f"[bold red]❌ Failed to analyze database:[/bold red]")
            console.print(f"  {e}")
            if verbose:
                import traceback

                console.print("\n[yellow]Stack trace:[/yellow]")
                console.print(traceback.format_exc())
            raise typer.Exit(code=1)

        progress.update(task, completed=True)

    console.print(f"[green]✓ Generated {len(spec['fields'])} fields from schema[/green]")

    # Save intermediate YAML if requested
    if save_yaml:
        yaml_file = output_dir / f"{spec['form']['id']}_spec.yaml"
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(yaml_file, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        console.print(f"[dim]Saved specification: {yaml_file}[/dim]")

    # Phase 2: Validate
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Validating specification...", total=None)

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

    # Phase 3: Generate forms
    output_dir.mkdir(parents=True, exist_ok=True)

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Generating forms...", total=None)

        try:
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
        for form_id_key, form_json in forms.items():
            output_file = output_dir / f"{form_id_key}.json"

            with open(output_file, "w") as f:
                json.dump(form_json, f, indent=2, ensure_ascii=False)

            if verbose:
                console.print(f"  Generated: [cyan]{output_file}[/cyan]")

        progress.update(task, completed=True)

    # Summary table
    table = Table(title="Generation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Forms Generated", str(len(forms)))
    table.add_row("Output Directory", str(output_dir))
    table.add_row("Total Fields", str(len(spec["fields"])))
    table.add_row("Source Table", table_name)

    console.print()
    console.print(table)

    console.print(f"\n[bold green]✓ Generation complete![/bold green]")


@app.command()
def deploy(
    form_path: Path = typer.Argument(
        ...,
        exists=True,
        help="Path to form JSON file or directory containing forms",
    ),
    base_url: str = typer.Option(
        ...,
        "--url",
        "-u",
        help="Joget base URL (e.g., http://localhost:8080/jw)",
    ),
    app_id: str = typer.Option(
        ...,
        "--app-id",
        "-a",
        help="Joget application ID",
    ),
    username: str = typer.Option(
        ...,
        "--username",
        help="Joget username",
    ),
    password: str = typer.Option(
        ...,
        "--password",
        help="Joget password",
        prompt=True,
        hide_input=True,
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing forms",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress"),
):
    """
    Deploy form(s) to a Joget DX instance.

    Supports deploying a single form file or all forms in a directory.

    Example:
        joget-form-gen deploy myform.json -u http://localhost:8080/jw -a myApp --username admin
        joget-form-gen deploy forms/ -u http://localhost:8080/jw -a myApp --username admin --overwrite
    """
    console.print(
        Panel.fit(
            "[bold blue]Joget Form Generator[/bold blue]\n[dim]Form Deployment[/dim]",
            subtitle="v0.1.0",
        )
    )

    # Phase 1: Connect to Joget
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Connecting to Joget...", total=None)

        try:
            from ..deployment.api_client import JogetAPIClient

            client = JogetAPIClient(
                base_url=base_url, app_id=app_id, username=username, password=password
            )

            # Get version info
            version = client.get_version()
            if version and verbose:
                console.print(f"[dim]Connected to Joget DX {version}[/dim]")

        except Exception as e:
            console.print(f"[bold red]❌ Connection failed:[/bold red]")
            console.print(f"  {e}")
            raise typer.Exit(code=1)

        progress.update(task, completed=True)

    console.print(f"[green]✓ Connected to {base_url}[/green]")

    # Phase 2: Deploy form(s)
    if form_path.is_file():
        # Deploy single file
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Deploying form...", total=None)

            try:
                result = client.deploy_form_from_file(form_path, overwrite_existing=overwrite)
                progress.update(task, completed=True)

                if result.get("success"):
                    console.print(f"[green]✓ Form deployed successfully[/green]")
                    if verbose:
                        console.print(f"  File: [cyan]{form_path}[/cyan]")
                else:
                    console.print(
                        f"[red]❌ Deployment failed: {result.get('message', 'Unknown error')}[/red]"
                    )
                    raise typer.Exit(code=1)

            except Exception as e:
                console.print(f"[bold red]❌ Deployment failed:[/bold red]")
                console.print(f"  {e}")
                if verbose:
                    import traceback

                    console.print("\n[yellow]Stack trace:[/yellow]")
                    console.print(traceback.format_exc())
                raise typer.Exit(code=1)

    elif form_path.is_dir():
        # Deploy directory
        console.print(f"📂 Directory: [cyan]{form_path}[/cyan]")

        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Deploying forms...", total=None)

            try:
                results = client.deploy_forms_from_directory(
                    form_path, overwrite_existing=overwrite
                )
                progress.update(task, completed=True)

            except Exception as e:
                console.print(f"[bold red]❌ Batch deployment failed:[/bold red]")
                console.print(f"  {e}")
                raise typer.Exit(code=1)

        # Summary
        successful = len(results["successful"])
        failed = len(results["failed"])
        total = successful + failed

        # Summary table
        table = Table(title="Deployment Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Forms", str(total))
        table.add_row("Successful", str(successful))
        table.add_row("Failed", str(failed), style="red" if failed > 0 else "green")
        table.add_row("Success Rate", f"{(successful/total*100):.1f}%" if total > 0 else "N/A")

        console.print()
        console.print(table)

        # Show failures if any
        if failed > 0:
            console.print("\n[bold red]Failed Deployments:[/bold red]")
            for failure in results["failed"]:
                console.print(f"  • {Path(failure['file']).name}: {failure['error']}")

        # Show successes in verbose mode
        if verbose and successful > 0:
            console.print("\n[bold green]Successful Deployments:[/bold green]")
            for success in results["successful"]:
                console.print(f"  ✓ {Path(success['file']).name}")

        if failed > 0:
            raise typer.Exit(code=1)

    else:
        console.print(f"[bold red]❌ Invalid path:[/bold red] {form_path}")
        console.print("  Path must be a file or directory")
        raise typer.Exit(code=1)

    console.print(f"\n[bold green]✓ Deployment complete![/bold green]")


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
