# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Joget Form Generator is a schema-driven tool for generating Joget DX Enterprise Edition forms from YAML specifications. It transforms declarative YAML definitions into Joget JSON form definitions through a 7-phase pipeline. The project also includes an MCP (Model Context Protocol) server for AI-assisted form development.

## Development Commands

### Setup
```bash
# Create virtual environment and install dependencies
python3.10 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run with coverage report
pytest --cov=src

# Run specific test file
pytest tests/patterns/test_select_box.py

# Run tests marked as integration
pytest -m integration

# Run MCP server tests only
pytest tests/mcp/ -v
```

### Code Quality
```bash
# Format code with Black
black src/ tests/

# Run linting
flake8 src/ tests/

# Type checking
mypy src/
```

### CLI Commands
```bash
# Validate a form specification
joget-form-gen validate examples/sample_form.yaml

# Generate forms from specification
joget-form-gen generate examples/sample_form.yaml -o output/

# Generate with validation only (no output)
joget-form-gen generate examples/sample_form.yaml --validate-only
```

### MCP Server Commands
```bash
# Start the MCP server
joget-form-mcp serve

# List available tools
joget-form-mcp tools

# Show examples
joget-form-mcp examples
```

### Regenerate Pydantic Models
When modifying the JSON schema, regenerate the Pydantic models:
```bash
python scripts/generate_models.py
```

## Architecture

### 7-Phase Transformation Pipeline

The core architecture follows a pipeline pattern implemented in `transformers/engine.py`:

1. **Load**: Parse YAML specification (handled by CLI)
2. **Validate**: Dual validation using JSON Schema (`schema/validator.py`) + Pydantic (`validators.py`)
3. **Normalize**: Apply defaults and standardize structure (`transformers/normalizer.py`)
4. **Pattern Match**: Look up field type in PatternRegistry (`patterns/registry.py`)
5. **Transform**: Render Joget JSON using Jinja2 templates (`patterns/base.py`)
6. **Post-Process**: Add metadata and finalize structure (`transformers/engine.py`)
7. **Output**: Write JSON files (handled by CLI)

### Pattern Library System

The pattern library (`src/joget_form_generator/patterns/`) uses a registry-based architecture:

- **BasePattern** (`base.py`): Abstract base class for all field patterns
  - Manages Jinja2 environment with custom filters
  - Defines template rendering workflow: `_prepare_context()` → render → `_post_process()`
  - Custom filters: `tojson_pretty`, `to_joget_bool` (converts Python bool to Joget's "true"/"" format)

- **PatternRegistry** (`registry.py`): Central registry mapping field types to pattern classes
  - Registration happens in `patterns/__init__.py`
  - Supports 17 data field types + 1 structural element:
    - **Standard (9)**: hiddenField, textField, passwordField, textArea, selectBox, checkBox, radio, datePicker, fileUpload
    - **Advanced (4)**: customHTML, idGenerator, subform, grid
    - **Enterprise (4)**: calculationField, richTextEditor, formGrid, multiPagedForm
    - **Structural (1)**: section (for grouping fields into sections)

- **Pattern Classes**: Each field type has:
  - A Python class (e.g., `TextFieldPattern` in `text_field.py`)
  - A Jinja2 template (e.g., `text_field.j2` in `patterns/templates/`)

### MCP Server

The MCP server (`src/joget_form_mcp/`) enables AI assistants to interact with the form generator:

- **server.py**: Main MCP server with 12 tools
- **tools/**: Tool implementations
  - `generation.py`: Form generation tools
  - `validation.py`: Spec validation tools
  - `discovery.py`: Field type discovery and documentation
  - `specification.py`: YAML spec creation from natural language

### Adding New Field Types

To add a new Joget field type:

1. Update JSON schema in `src/joget_form_generator/schema/form_spec_schema.json`
2. Regenerate Pydantic models: `python scripts/generate_models.py`
3. Create pattern class in `src/joget_form_generator/patterns/new_field.py`:
   - Inherit from `BasePattern`
   - Set `template_name` class variable
   - Implement `_prepare_context()` method
4. Create Jinja2 template in `src/joget_form_generator/patterns/templates/new_field.j2`
5. Register in `src/joget_form_generator/patterns/__init__.py`:
   ```python
   PatternRegistry.register("newField", NewFieldPattern)
   ```
6. Add tests in `tests/patterns/test_new_field.py`

### Validation System

Dual validation approach in `validators.py`:

1. **JSON Schema Validation** (`schema/validator.py`):
   - Structural validation using jsonschema library
   - Enforces required fields, data types, patterns (e.g., ID format)
   - Provides contextual error messages with suggestions
   - Checks for warnings (duplicate IDs, form ID/tableName mismatch)

2. **Pydantic Validation** (generated models in `models/spec.py`):
   - Semantic validation with type hints
   - Auto-generated from JSON schema using datamodel-code-generator
   - Provides IDE autocomplete support

### Key Files

- `cli/main.py`: Typer-based CLI with Rich output formatting
- `transformers/engine.py`: TransformEngine orchestrates the pipeline
- `transformers/normalizer.py`: Applies defaults before transformation
- `patterns/base.py`: Template rendering infrastructure
- `patterns/mixins.py`: Shared behavior for pattern classes (e.g., validators, options)
- `schema/form_spec_schema.json`: JSON Schema defining valid specifications

## Configuration

### pytest (pyproject.toml)
- Coverage reports: terminal + HTML (in `htmlcov/`)
- Integration tests marked with `@pytest.mark.integration`

### Black (pyproject.toml)
- Line length: 100 characters
- Target: Python 3.10+

### mypy (pyproject.toml)
- Strict type checking enabled
- `disallow_untyped_defs = true`

## YAML Specification Format

Form specifications follow this structure:

```yaml
form:
  id: formId              # Must match tableName, max 20 chars
  name: Display Name
  tableName: formId       # Database table name (should match id)
  description: Optional description

fields:
  - id: fieldId           # Database column name
    label: Field Label
    type: textField       # One of registered pattern types
    required: true/false
    # Type-specific properties...
```

See `examples/sample_form.yaml` for a complete example.

## Sample Forms Reference

The `sample-forms/` directory contains tested, working Joget JSON exports that serve as syntax and pattern references:

```
sample-forms/
├── 01_nested_lovs/           # Cascading dropdown pattern (with comprehensive guide)
├── 02_master_details/        # Master-detail relationships
├── 03_tabs/                  # Tab-based layouts
├── 04_farmer-application-form/  # Complex 7-page wizard (excellent syntax reference)
└── 05_ajax-subform/          # AJAX Subform lookup pattern
```

### Key Reference Examples

- **04_farmer-application-form**: Production-quality multi-tab wizard demonstrating:
  - `MultiPagedForm` with 7 pages
  - `FormGrid` with `MultirowFormBinder`
  - Various validators (`DefaultValidator`, `DuplicateValueValidator`)
  - `FormOptionsBinder` for MDM lookups

- **01_nested_lovs**: Complete cascading dropdown implementation with `JOGET_NESTED_LOV_GUIDE.md`

- **05_ajax-subform**: AJAX Subform pattern (see `docs/AJAX_SUBFORM_PATTERN.md` for critical undocumented behaviors)

## Package Structure

```
src/
├── joget_form_generator/      # Core form generation library
│   ├── cli/                   # Typer CLI interface
│   ├── models/                # Pydantic models (auto-generated)
│   ├── patterns/              # Pattern library (17 field types)
│   │   └── templates/         # Jinja2 templates for each field type
│   ├── schema/                # JSON Schema definitions
│   ├── transformers/          # Pipeline components (engine, normalizer)
│   ├── utils/                 # Utility functions
│   └── validators.py          # DualValidator orchestration
│
└── joget_form_mcp/            # MCP server for AI assistants
    ├── server.py              # Main MCP server
    ├── cli.py                 # MCP CLI entry point
    └── tools/                 # Tool implementations
        ├── generation.py      # Form generation
        ├── validation.py      # Spec validation
        ├── discovery.py       # Field type docs
        └── specification.py   # YAML creation
```

## Joget-Specific Conventions

- Joget uses `"true"` (string) for true and `""` (empty string) for false - use the `to_joget_bool` filter
- Form ID and tableName must be identical for proper database table creation
- Field IDs become database column names - validate for uniqueness
- All forms have className: `org.joget.apps.form.model.Form`
- Elements array contains field definitions as nested JSON

### Composite Patterns (Enterprise)

These patterns combine multiple elements for advanced functionality:

1. **AJAX Subform Pattern**: SelectBox + AjaxSubForm for dynamic record lookup
   - CRITICAL: SelectBox `idColumn` MUST be empty (use primary key)
   - AjaxSubForm `ajax` MUST be `"true"`
   - AjaxSubForm `parentSubFormId` must match SelectBox ID
   - See `docs/AJAX_SUBFORM_PATTERN.md` for complete documentation

2. **Cascading Dropdown Pattern**: Parent SelectBox → Child SelectBox with filtering
   - Child needs `groupingColumn` (field in source form referencing parent)
   - Child needs `controlField` (parent field ID in current form)
   - Child needs `useAjax: "true"` for dynamic filtering
   - **CRITICAL**: Category field in child MDM MUST be a SelectBox (not TextField)
   - See `docs/NESTED_LOV_REFACTORING_PATTERN.md` for refactoring long flat LOVs
   - See `sample-forms/01_nested_lovs/JOGET_NESTED_LOV_GUIDE.md` for implementation guide

3. **Multi-Page Wizard**: MultiPagedForm element with multiple sub-forms
   - See `sample-forms/04_farmer-application-form/` for 7-page example

### Validator Classes

Joget DX has limited built-in validator classes. **Do NOT use non-existent classes**:

| Correct Class | Usage |
|---------------|-------|
| `org.joget.apps.form.lib.DefaultValidator` | Standard validator for mandatory, regex, email, alphanumeric, etc. |

**Classes that DO NOT exist** (never generate these):
- ~~`org.joget.apps.form.lib.RegexValidator`~~ - Use `DefaultValidator` with `type: "regex"`
- ~~`org.joget.apps.form.lib.MultiValidator`~~ - Combine validations in single `DefaultValidator`
- ~~`org.joget.apps.form.lib.TextFieldLengthValidator`~~ - Use `DefaultValidator` with regex pattern

Example of correct validator structure:
```json
{
  "className": "org.joget.apps.form.lib.DefaultValidator",
  "properties": {
    "mandatory": "true",
    "type": "regex",
    "regex": "^[A-Z0-9_]+$",
    "message": "Invalid format"
  }
}
```

## Form Generation Rules

### Do NOT Add System-Managed Fields

These rules apply to **ALL forms** (MDM, transactional, etc.). Joget automatically manages these fields - **never add them to any form**:

- `id` - Joget auto-generates the primary key (do NOT add as hidden field either)
- `createdBy` - Audit trail field (auto-managed)
- `createdDate` / `dateCreated` - Audit trail field (auto-managed)
- `modifiedBy` - Audit trail field (auto-managed)
- `modifiedDate` / `dateModified` - Audit trail field (auto-managed)

## MDM Form Rules

When creating Master Data Management (MDM) forms, follow these additional rules:

### 1. Form Naming Convention
- Form ID: `mdXX<EntityName>` (e.g., `md38InputCategory`)
- Form Name: `MD.XX - <Display Name>` (e.g., `MD.38 - Input Category`)
- The XX index should be consistent between ID and name

### 2. Required Fields for Every MDM Form
Every MDM form **must** have these fields as the first two fields:
- `code` - Unique business identifier (required, textField)
- `name` - Display name (required, textField)

### 3. Standard MDM Form Structure
```yaml
form:
  id: mdXXEntityName
  name: MD.XX - Entity Name
  tableName: mdXXEntityName
  description: Description of the master data

fields:
  - id: code
    label: Code
    type: textField
    required: true
    maxlength: 30

  - id: name
    label: Name
    type: textField
    required: true
    maxlength: 100

  # ... additional entity-specific fields ...

  - id: isActive
    label: Active
    type: radio
    required: true
    defaultValue: "Y"
    options:
      - value: "Y"
        label: "Yes"
      - value: "N"
        label: "No"
```

### 4. Common Optional Fields
- `description` - textArea for additional details
- `sortOrder` - textField for display ordering (default: "0")
- `isActive` - radio Y/N for soft delete pattern (recommended for all MDM)
