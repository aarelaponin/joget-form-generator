# Joget Form Generator MCP Server

**Model Context Protocol (MCP) server for AI-assisted Joget DX form development.**

This module provides an MCP interface to the Joget Form Generator, enabling AI assistants (Claude Desktop, LM Studio, etc.) to help you design and validate Joget forms through natural conversation.

## Features

- **Conversational Form Design** - Describe your form in natural language, get production-ready YAML
- **Smart Validation** - Real-time spec validation with detailed error messages
- **Field Type Discovery** - AI can explain field types, show examples, suggest alternatives
- **Cascading Dropdown Patterns** - Generate parent-child form hierarchies automatically

## Installation

```bash
# From the joget-form-generator directory
pip install -e ".[dev]"

# Verify MCP CLI is available
joget-form-mcp --version
```

## Quick Start

### 1. Run the MCP Server

```bash
# Start the MCP server (stdio transport)
joget-form-mcp serve

# With debug logging
joget-form-mcp serve --debug
```

### 2. Configure Claude Desktop

Add to your Claude Desktop configuration (`~/.config/claude/claude_desktop_config.json` on Linux or `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

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

### 3. Start Designing Forms

In Claude Desktop, you can now say things like:

> "Create a farmer registration form with name, phone, email, farm size, and crop type fields"

> "Add a cascading dropdown to my form where equipment category filters equipment type"

> "Validate this YAML specification and show me any errors"

> "Generate Joget JSON from this YAML spec"

## Available Tools

### Generation Tools
| Tool | Description |
|------|-------------|
| `generate_form` | Transform YAML specification to Joget JSON |
| `generate_multiple_forms` | Generate multiple forms from multi-form spec |

### Validation Tools
| Tool | Description |
|------|-------------|
| `validate_spec` | Validate YAML against JSON Schema + Pydantic |
| `validate_joget_json` | Validate Joget JSON structure |

### Discovery Tools
| Tool | Description |
|------|-------------|
| `list_field_types` | List all 17 supported field types by category |
| `get_field_type_info` | Get detailed docs for a specific field type |
| `get_example_spec` | Get example YAML specifications |

### Specification Tools
| Tool | Description |
|------|-------------|
| `create_form_spec` | Generate YAML from natural language description |
| `create_cascading_dropdown_spec` | Generate parent-child form pattern |
| `add_field_to_spec` | Add a field to existing specification |

## CLI Commands

```bash
# List available tools
joget-form-mcp tools

# List example specifications
joget-form-mcp examples

# Show a specific example
joget-form-mcp example cascading-dropdown

# Start MCP server
joget-form-mcp serve
```

## Example Conversation

**You:** Create a simple contact form with name, email, and message fields

**Claude (using MCP):**
```yaml
form:
  id: contactForm
  name: Contact Form
  description: Simple contact form

fields:
  - id: name
    label: Name
    type: textField
    required: true

  - id: email
    label: Email
    type: textField
    required: true
    validator:
      type: email
      message: Please enter a valid email

  - id: message
    label: Message
    type: textArea
    rows: 5
    required: true
```

**You:** Generate the Joget JSON for this form

**Claude (using MCP):**
Here's the generated Joget JSON for your contact form. You can import this into Joget via the Form Builder or FormCreator API.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Assistant                             │
│               (Claude Desktop, LM Studio)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ MCP Protocol (stdio)
┌──────────────────────────▼──────────────────────────────────┐
│                  joget-form-mcp Server                       │
├──────────────────────────────────────────────────────────────┤
│  Tools:                                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │ Generation  │ │ Validation  │ │ Discovery &             ││
│  │ Tools       │ │ Tools       │ │ Specification Tools     ││
│  └──────┬──────┘ └──────┬──────┘ └───────────┬─────────────┘│
└─────────┼───────────────┼───────────────────┼───────────────┘
          │               │                   │
┌─────────▼───────────────▼───────────────────▼───────────────┐
│              joget-form-generator Core                       │
├──────────────────────────────────────────────────────────────┤
│  • TransformEngine        • Pattern Library (17 fields)      │
│  • JSON Schema Validator  • Pydantic Models                  │
└──────────────────────────────────────────────────────────────┘
```

## Development

### Running Tests

```bash
# Run MCP-specific tests
pytest tests/mcp/ -v

# Run all tests with coverage
pytest --cov=src
```

### Project Structure

```
src/joget_form_mcp/
├── __init__.py          # Package metadata
├── server.py            # Main MCP server (12 tools)
├── cli.py               # CLI entry point
└── tools/
    ├── __init__.py
    ├── generation.py    # Form generation tools
    ├── validation.py    # Spec validation tools
    ├── discovery.py     # Field type discovery
    └── specification.py # YAML spec creation
```

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Joget Form Generator](../README.md)
- [Joget DX Documentation](https://dev.joget.org/community/display/DX8/)

## License

MIT License - see [LICENSE](../../LICENSE) file for details.
