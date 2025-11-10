# Joget Form Generator

Schema-driven form generation for Joget DX Enterprise Edition.

## Features

- **JSON Schema Validation**: IDE autocomplete and fail-fast validation
- **Pattern Library**: Reusable templates for 28 Joget field types
- **CLI**: User-friendly command-line interface with progress reporting
- **Type Safe**: Full type hints with auto-generated Pydantic models

## Installation

```bash
pip install joget-form-generator
```

## Quick Start

```bash
# Validate a specification
joget-form-gen validate myform.yaml

# Generate forms
joget-form-gen generate myform.yaml -o output/
```

## Development

```bash
# Clone repository
git clone https://github.com/aarelaponin/joget-form-generator.git
cd joget-form-generator

# Install development dependencies
python3.10 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src
```

## Documentation

See [docs/](docs/) for detailed documentation.

## License

MIT License - see [LICENSE](LICENSE) file.
