# Joget Form Generator

**Schema-driven form generation for Joget DX Enterprise Edition**

Transform human-readable YAML specifications into production-ready Joget DX form JSON definitions.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-191%20passing-brightgreen.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-62%25-yellow.svg)](#testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Features

- **JSON Schema 2020-12 Validation** - IDE autocomplete (VS Code, PyCharm) and fail-fast error detection
- **Pattern Library** - 17 field types (9 standard + 4 advanced + 4 Enterprise), extensible architecture
- **CLI with Progress Reporting** - User-friendly command-line interface with detailed error messages
- **MCP Server** - AI-assisted form design via Model Context Protocol (Claude Desktop, LM Studio)
- **Type Safety** - Full type hints with Pydantic models for Python integration
- **No Manual JSON Editing** - Write clean YAML, generate perfect Joget JSON
- **Cascading Dropdowns** - Built-in support for nested LOV (List of Values) patterns

---

## Supported Field Types

**Phase 1 (Core Fields):**
- Hidden Field | Text Field | Password Field | Text Area
- Select Box (with cascading) | Check Box | Radio | Date Picker | File Upload

**Phase 2 (Advanced Fields):**
- Custom HTML | ID Generator | Subform (master-detail) | Grid (tabular data)

**Phase 3 (Enterprise Fields):**
- Calculation Field | Rich Text Editor | Form Grid | Multi Paged Form

---

## Installation

### From Source (Development)

```bash
# Clone repository
git clone https://github.com/aarelaponin/joget-form-generator.git
cd joget-form-generator

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
joget-form-gen --version
joget-form-mcp --version
```

---

## Quick Start

### 1. Create a YAML Specification

`customer_form.yaml`:
```yaml
form:
  id: customerInfo
  name: Customer Information
  description: Basic customer details form

fields:
  - id: firstName
    label: First Name
    type: textField
    required: true
    placeholder: Enter first name

  - id: email
    label: Email Address
    type: textField
    required: true
    validation:
      pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      message: Please enter a valid email address

  - id: dateOfBirth
    label: Date of Birth
    type: datePicker
    dateFormat: yyyy-MM-dd

  - id: status
    label: Status
    type: selectBox
    required: true
    options:
      - value: active
        label: Active
      - value: inactive
        label: Inactive
```

### 2. Generate the Form

```bash
joget-form-gen generate customer_form.yaml -o output/
```

Output:
```
Validation successful
Generating: customerInfo
Generated: output/customerInfo.json

Summary:
  Forms: 1
  Fields: 4
  Time: 0.12s
```

### 3. Deploy to Joget

Upload `output/customerInfo.json` via Joget Form Builder UI or FormCreator API.

---

## MCP Server (AI-Assisted Development)

The project includes an MCP server for AI-assisted form development with Claude Desktop or other MCP clients.

### Start the MCP Server

```bash
joget-form-mcp serve
```

### Configure Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "joget-form-generator": {
      "command": "joget-form-mcp",
      "args": ["serve"]
    }
  }
}
```

### Available MCP Tools (12 total)

| Category | Tools |
|----------|-------|
| **Generation** | `generate_form`, `generate_multiple_forms` |
| **Validation** | `validate_spec`, `validate_joget_json` |
| **Discovery** | `list_field_types`, `get_field_type_info`, `get_example_spec` |
| **Specification** | `create_form_spec`, `create_cascading_dropdown_spec`, `add_field_to_spec` |

See [MCP Server README](src/joget_form_mcp/README.md) for detailed documentation.

---

## Documentation

| Document | Description |
|----------|-------------|
| **[YAML Specification Reference](docs/YAML_SPECIFICATION.md)** | Complete reference for YAML input format, all 17 field types, options sources |
| **[User Guide](docs/USER_GUIDE.md)** | Getting started, workflows, troubleshooting |
| **[Enterprise Fields Guide](ENTERPRISE_FIELDS.md)** | Calculation Field, Rich Text Editor, Form Grid, Multi-Paged Form |
| **[API Reference](docs/API_REFERENCE.md)** | Programmatic usage for Python integration |
| **[Pattern Development Guide](docs/PATTERN_DEVELOPMENT_GUIDE.md)** | Extend with custom field types |
| **[MCP Server](src/joget_form_mcp/README.md)** | AI-assisted form development |
| **[Examples](examples/)** | Working examples (MDM forms, etc.) |
| **[Specs](specs/)** | Your form specifications go here |

---

## CLI Usage

```bash
# Validate specification without generating
joget-form-gen validate my_form.yaml

# Generate forms to current directory
joget-form-gen generate my_form.yaml

# Generate to specific directory
joget-form-gen generate my_form.yaml -o generated_forms/

# Validate only (skip generation)
joget-form-gen generate my_form.yaml --validate-only

# Verbose output with debug info
joget-form-gen generate my_form.yaml --verbose

# Show version
joget-form-gen --version
```

---

## Programmatic Usage (Python API)

```python
from joget_form_generator.transformers.engine import TransformEngine
import yaml
import json

# Load specification
with open("customer_form.yaml") as f:
    spec = yaml.safe_load(f)

# Generate forms
engine = TransformEngine()
forms = engine.generate(spec)

# Save to file
for form_id, form_json in forms.items():
    with open(f"{form_id}.json", "w") as f:
        json.dump(form_json, f, indent=2)
```

See [API Reference](docs/API_REFERENCE.md) for full documentation.

---

## Examples

### Simple Master Data Form

```yaml
form:
  id: md01maritalStatus
  name: MD.01 - Marital Status

fields:
  - id: code
    label: Code
    type: textField
    required: true

  - id: name
    label: Name
    type: textField
    required: true
```

### Form with Cascading Dropdown (Nested LOV)

```yaml
fields:
  - id: equipment_category
    label: Equipment Category
    type: selectBox
    required: true
    optionsSource:
      type: formData
      formId: md25equipCategory  # References parent form
      valueColumn: code
      labelColumn: name
```

### Enterprise Fields Example (Calculation Field)

```yaml
fields:
  - id: quantity
    label: Quantity
    type: textField
    required: true
    defaultValue: "1"

  - id: unitPrice
    label: Unit Price ($)
    type: textField
    required: true
    defaultValue: "100.00"

  - id: total
    label: Total Cost
    type: calculationField
    equation: quantity * unitPrice
    storeNumeric: true
    readonly: true
```

More examples in [examples/](examples/) directory.

---

## Development

### Setup

```bash
# Clone and install
git clone https://github.com/aarelaponin/joget-form-generator.git
cd joget-form-generator
python3.10 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/patterns/test_select_box.py

# Run MCP tests only
pytest tests/mcp/ -v
```

### Project Structure

```
joget-form-generator/
├── src/
│   ├── joget_form_generator/      # Core form generation
│   │   ├── cli/                   # Typer-based CLI
│   │   ├── models/                # Pydantic models
│   │   ├── patterns/              # Pattern library (17 field types)
│   │   │   └── templates/         # Jinja2 templates
│   │   ├── schema/                # JSON Schema validation
│   │   ├── transformers/          # Transform engine
│   │   └── validators.py          # Dual validation
│   │
│   └── joget_form_mcp/            # MCP server for AI assistants
│       ├── server.py              # Main MCP server
│       ├── cli.py                 # MCP CLI
│       └── tools/                 # 12 MCP tools
│
├── tests/                         # Test suite
│   ├── integration/               # End-to-end tests
│   ├── mcp/                       # MCP server tests
│   ├── patterns/                  # Pattern unit tests
│   ├── schema/                    # Schema validation tests
│   └── transformers/              # Normalizer tests
│
├── examples/                      # Working examples
│   ├── mdm/                       # MDM form examples
│   └── sample_form.yaml
│
└── docs/                          # Documentation
```

---

## Testing

**Current Status:** 191 tests (188 passing)

```bash
$ pytest --cov=src

============================= test session starts ==============================
collected 191 items

tests/integration/test_mdm_forms.py ......
tests/mcp/test_discovery.py ...........
tests/mcp/test_generation.py ........
tests/mcp/test_specification.py ..........
tests/mcp/test_validation.py .......
tests/patterns/test_calculation_field.py ....
tests/patterns/test_check_box.py ...
tests/patterns/test_custom_html.py ....
tests/patterns/test_date_picker.py .....
tests/patterns/test_file_upload.py ......
tests/patterns/test_form_grid.py .......
tests/patterns/test_grid.py ........
tests/patterns/test_hidden_field.py ...
tests/patterns/test_id_generator.py ......
tests/patterns/test_mixins.py ............
tests/patterns/test_multi_paged_form.py ......
tests/patterns/test_password_field.py ....
tests/patterns/test_radio.py ...
tests/patterns/test_rich_text_editor.py ......
tests/patterns/test_select_box.py ...
tests/patterns/test_subform.py ........
tests/patterns/test_text_area.py .....
tests/patterns/test_text_field.py .............
tests/schema/test_validator.py ................
tests/transformers/test_normalizer.py ...............

======================== 191 passed in 0.72s ================================
```

---

## Roadmap

### Completed
- [x] JSON Schema 2020-12 validation
- [x] Pattern library with 17 field types (standard, advanced, enterprise)
- [x] Typer-based CLI with Rich output
- [x] Cascading dropdown support (formData source)
- [x] MCP server for AI-assisted development
- [x] Comprehensive documentation

### Planned
- [ ] Additional Enterprise field types (Advanced Grid, Spreadsheet, Signature)
- [ ] Section and Column layout patterns
- [ ] Process integration (workflow variables)
- [ ] Import existing Joget forms to YAML (reverse transformation)
- [ ] Web UI for form generation

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

See [PATTERN_DEVELOPMENT_GUIDE.md](docs/PATTERN_DEVELOPMENT_GUIDE.md) for extending with custom field types.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built for Joget DX Enterprise Edition
- Uses JSON Schema 2020-12 for validation
- Template rendering via Jinja2
- CLI powered by Typer
- MCP server using Model Context Protocol SDK

---

**Version:** 0.1.0
**Maintained by:** Aare Laponin
