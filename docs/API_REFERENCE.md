# Joget Form Generator - API Reference

**Version:** 1.0.0
**Last Updated:** 2025-01-10

## Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)
3. [Schema Validation](#schema-validation)
4. [Transform Engine](#transform-engine)
5. [Pattern Library](#pattern-library)
6. [Normalizer](#normalizer)
7. [Programmatic Usage Examples](#programmatic-usage-examples)

---

## Overview

The Joget Form Generator provides a Python API for programmatic form generation. This document describes the public API for developers who want to integrate the generator into their own tools or workflows.

### Architecture

```
┌─────────────────────────────────────────────┐
│          YAML Specification                  │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│      Schema Validator (JSON Schema)          │
│  - Validates structure                        │
│  - Provides error messages                   │
│  - Generates warnings                         │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│          Normalizer                          │
│  - Applies defaults                          │
│  - Sets tableName = id                       │
│  - Field-specific defaults                   │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│        Transform Engine                      │
│  - Orchestrates generation                   │
│  - Calls pattern renderers                   │
│  - Assembles final form                      │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│      Pattern Library                         │
│  - Field-specific renderers                  │
│  - Jinja2 template rendering                 │
│  - Joget JSON generation                     │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│       Generated Joget JSON Form              │
└─────────────────────────────────────────────┘
```

---

## Core Components

### Package Structure

```
joget_form_generator/
├── __init__.py                  # Package entry point
├── cli/                         # Command-line interface
│   └── main.py
├── models/                      # Pydantic models
│   └── spec.py
├── patterns/                    # Pattern library
│   ├── base.py                  # Base pattern class
│   ├── registry.py              # Pattern registry
│   ├── mixins.py                # Shared pattern logic
│   ├── text_field.py            # Text field pattern
│   ├── select_box.py            # Select box pattern
│   └── templates/               # Jinja2 templates
│       ├── text_field.j2
│       └── select_box.j2
├── schema/                      # JSON Schema validation
│   ├── form_spec_schema.json    # JSON Schema definition
│   └── validator.py             # Schema validator
├── transformers/                # Transformation engine
│   ├── engine.py                # Main engine
│   └── normalizer.py            # Spec normalizer
└── validators.py                # Dual validation (Schema + Pydantic)
```

---

## Schema Validation

### SchemaValidator

Validates YAML specifications against JSON Schema 2020-12.

#### Class: `SchemaValidator`

**Location:** `joget_form_generator.schema.validator`

```python
from joget_form_generator.schema.validator import SchemaValidator, ValidationResult
```

#### Constructor

```python
def __init__(self, schema_path: Optional[Path] = None)
```

**Parameters:**
- `schema_path` (Path, optional): Path to custom JSON Schema file. If None, uses bundled schema.

**Example:**
```python
# Use bundled schema
validator = SchemaValidator()

# Use custom schema
from pathlib import Path
validator = SchemaValidator(schema_path=Path("custom_schema.json"))
```

#### Method: `validate(spec: dict) -> ValidationResult`

Validates a specification against the JSON Schema.

**Parameters:**
- `spec` (dict): Parsed YAML specification

**Returns:**
- `ValidationResult`: Validation result object

**Example:**
```python
import yaml

with open("my_form.yaml") as f:
    spec = yaml.safe_load(f)

result = validator.validate(spec)

if result.valid:
    print("✅ Validation successful")
else:
    print("❌ Validation failed:")
    for error in result.errors:
        print(f"  - {error}")
```

---

### ValidationResult

**Location:** `joget_form_generator.schema.validator`

#### Attributes

```python
class ValidationResult:
    valid: bool                  # True if validation passed
    errors: list[str]            # List of error messages
    warnings: list[str]          # List of warning messages
```

**Example:**
```python
result = validator.validate(spec)

print(f"Valid: {result.valid}")
print(f"Errors: {len(result.errors)}")
print(f"Warnings: {len(result.warnings)}")

if result.warnings:
    print("\nWarnings:")
    for warning in result.warnings:
        print(f"  ⚠️  {warning}")
```

---

## Transform Engine

### TransformEngine

Orchestrates the form generation process.

#### Class: `TransformEngine`

**Location:** `joget_form_generator.transformers.engine`

```python
from joget_form_generator.transformers.engine import TransformEngine
```

#### Constructor

```python
def __init__(self,
             validator: Optional[SchemaValidator] = None,
             normalizer: Optional[Normalizer] = None)
```

**Parameters:**
- `validator` (SchemaValidator, optional): Custom validator instance
- `normalizer` (Normalizer, optional): Custom normalizer instance

**Example:**
```python
# Default instances
engine = TransformEngine()

# Custom instances
from joget_form_generator.schema.validator import SchemaValidator
from joget_form_generator.transformers.normalizer import Normalizer

validator = SchemaValidator()
normalizer = Normalizer()
engine = TransformEngine(validator=validator, normalizer=normalizer)
```

#### Method: `generate(spec: dict) -> dict[str, dict]`

Generates Joget form JSON from specification.

**Parameters:**
- `spec` (dict): Parsed YAML specification

**Returns:**
- `dict[str, dict]`: Dictionary mapping form IDs to generated JSON

**Raises:**
- `ValueError`: If validation fails

**Example:**
```python
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
    output_path = f"output/{form_id}.json"
    with open(output_path, "w") as f:
        json.dump(form_json, f, indent=2)
    print(f"✅ Generated: {output_path}")
```

**Error Handling:**
```python
try:
    forms = engine.generate(spec)
except ValueError as e:
    print(f"❌ Generation failed: {e}")
    # Error message includes validation errors with suggestions
```

---

## Pattern Library

### BasePattern

Abstract base class for all field patterns.

#### Class: `BasePattern`

**Location:** `joget_form_generator.patterns.base`

```python
from joget_form_generator.patterns.base import BasePattern
```

#### Abstract Methods

```python
def render(self, field: dict, context: dict) -> dict:
    """
    Render field to Joget JSON.

    Args:
        field: Field specification
        context: Rendering context (form metadata, etc.)

    Returns:
        Joget JSON field definition
    """
    pass
```

#### Protected Methods

```python
def _prepare_context(self, field: dict, context: dict) -> dict:
    """Prepare template context with defaults."""
    pass

def _post_process(self, result: dict) -> dict:
    """Post-process rendered JSON (cleanup, validation)."""
    pass
```

---

### Pattern Registry

Manages pattern registration and lookup.

#### Class: `PatternRegistry`

**Location:** `joget_form_generator.patterns.registry`

```python
from joget_form_generator.patterns.registry import PatternRegistry
```

#### Method: `get_pattern(field_type: str) -> BasePattern`

Retrieves pattern instance for field type.

**Parameters:**
- `field_type` (str): Field type (e.g., "textField", "selectBox")

**Returns:**
- `BasePattern`: Pattern instance

**Raises:**
- `ValueError`: If field type not registered

**Example:**
```python
registry = PatternRegistry()

# Get pattern for text field
pattern = registry.get_pattern("textField")

# Render field
field_spec = {
    "id": "username",
    "label": "Username",
    "type": "textField",
    "required": True
}

context = {"form_id": "userForm"}
joget_field = pattern.render(field_spec, context)
```

---

### Built-in Patterns

All patterns follow the same interface:

#### Text Field Pattern

```python
from joget_form_generator.patterns.text_field import TextFieldPattern

pattern = TextFieldPattern()
result = pattern.render(field_spec, context)
```

**Supported Properties:**
- `placeholder`, `size`, `maxLength`, `validation`

---

#### Select Box Pattern

```python
from joget_form_generator.patterns.select_box import SelectBoxPattern

pattern = SelectBoxPattern()
result = pattern.render(field_spec, context)
```

**Supported Properties:**
- `options` (static)
- `optionsSource` (dynamic: formData, api, database)
- `multiple`

---

#### Date Picker Pattern

```python
from joget_form_generator.patterns.date_picker import DatePickerPattern

pattern = DatePickerPattern()
result = pattern.render(field_spec, context)
```

**Supported Properties:**
- `dateFormat`

---

## Normalizer

### Normalizer

Applies defaults and resolves references.

#### Class: `Normalizer`

**Location:** `joget_form_generator.transformers.normalizer`

```python
from joget_form_generator.transformers.normalizer import Normalizer
```

#### Method: `normalize(spec: dict) -> dict`

Normalizes specification by applying defaults.

**Parameters:**
- `spec` (dict): Validated specification

**Returns:**
- `dict`: Normalized specification

**Example:**
```python
normalizer = Normalizer()

# Before normalization
spec = {
    "form": {
        "id": "myForm",
        "name": "My Form"
        # tableName missing
    },
    "fields": [
        {
            "id": "field1",
            "label": "Field 1",
            "type": "textField"
            # required missing (should default to False)
        }
    ]
}

# After normalization
normalized = normalizer.normalize(spec)

# normalized["form"]["tableName"] == "myForm" (auto-set)
# normalized["fields"][0]["required"] == False (default applied)
```

#### Default Values

**Form-level Defaults:**
```python
{
    "description": "",
    "tableName": "<form.id>"  # Auto-set if missing
}
```

**Field-level Defaults:**
```python
{
    "required": False,
    "readonly": False,
    "size": "medium"
}
```

**Type-specific Defaults:**
```python
# textArea
{
    "rows": 5,
    "cols": 50
}

# selectBox
{
    "size": 10
}

# datePicker
{
    "dateFormat": "yyyy-MM-dd"
}

# fileUpload
{
    "maxSize": 10,  # MB
    "fileTypes": "*"
}
```

---

## Programmatic Usage Examples

### Example 1: Basic Generation

```python
from joget_form_generator.transformers.engine import TransformEngine
import yaml
import json

# Load specification
with open("customer_form.yaml") as f:
    spec = yaml.safe_load(f)

# Generate form
engine = TransformEngine()
forms = engine.generate(spec)

# Save to file
for form_id, form_json in forms.items():
    with open(f"{form_id}.json", "w") as f:
        json.dump(form_json, f, indent=2)
```

---

### Example 2: Validation Only

```python
from joget_form_generator.schema.validator import SchemaValidator
import yaml

# Load specification
with open("my_form.yaml") as f:
    spec = yaml.safe_load(f)

# Validate
validator = SchemaValidator()
result = validator.validate(spec)

if not result.valid:
    print("❌ Validation failed:")
    for error in result.errors:
        print(f"  - {error}")
else:
    print("✅ Validation passed")
    if result.warnings:
        print("\n⚠️  Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
```

---

### Example 3: Custom Normalization

```python
from joget_form_generator.transformers.normalizer import Normalizer

class CustomNormalizer(Normalizer):
    """Custom normalizer with organization-specific defaults."""

    DEFAULT_FIELD_VALUES = {
        **Normalizer.DEFAULT_FIELD_VALUES,
        "size": "large",  # Override default size
    }

    def _apply_field_defaults(self, field: dict) -> dict:
        """Apply custom defaults."""
        normalized = super()._apply_field_defaults(field)

        # Add custom logic: all email fields get validation
        if field.get("id", "").endswith("_email"):
            normalized.setdefault("validation", {
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                "message": "Please enter a valid email address"
            })

        return normalized

# Use custom normalizer
from joget_form_generator.transformers.engine import TransformEngine

normalizer = CustomNormalizer()
engine = TransformEngine(normalizer=normalizer)
forms = engine.generate(spec)
```

---

### Example 4: Batch Generation

```python
from pathlib import Path
from joget_form_generator.transformers.engine import TransformEngine
import yaml
import json

def generate_all_forms(specs_dir: Path, output_dir: Path):
    """Generate forms from all YAML files in directory."""
    engine = TransformEngine()

    for yaml_file in specs_dir.glob("*.yaml"):
        print(f"Processing: {yaml_file.name}")

        try:
            # Load spec
            with open(yaml_file) as f:
                spec = yaml.safe_load(f)

            # Generate forms
            forms = engine.generate(spec)

            # Save each form
            for form_id, form_json in forms.items():
                output_file = output_dir / f"{form_id}.json"
                with open(output_file, "w") as f:
                    json.dump(form_json, f, indent=2)
                print(f"  ✅ {form_id}.json")

        except Exception as e:
            print(f"  ❌ Failed: {e}")

# Usage
specs_dir = Path("specifications/mdm")
output_dir = Path("generated_forms")
output_dir.mkdir(exist_ok=True)

generate_all_forms(specs_dir, output_dir)
```

---

### Example 5: Integration with Deployment System

```python
from joget_form_generator.transformers.engine import TransformEngine
from pathlib import Path
import yaml
import json
import requests

def generate_and_deploy(yaml_file: Path, joget_api_url: str, api_key: str):
    """Generate form and deploy to Joget via API."""

    # Load specification
    with open(yaml_file) as f:
        spec = yaml.safe_load(f)

    # Generate form
    engine = TransformEngine()
    forms = engine.generate(spec)

    # Deploy each form
    for form_id, form_json in forms.items():
        print(f"Deploying: {form_id}")

        # Save locally
        output_file = f"temp/{form_id}.json"
        with open(output_file, "w") as f:
            json.dump(form_json, f)

        # Deploy to Joget
        response = requests.post(
            f"{joget_api_url}/api/form/formCreator/addWithFiles",
            files={"form_definition_json": open(output_file, "rb")},
            headers={
                "api_id": api_key,
                "api_key": api_key,
                "Referer": f"{joget_api_url}/jw/web/console/app//forms"
            }
        )

        if response.status_code == 200:
            print(f"  ✅ Deployed successfully")
        else:
            print(f"  ❌ Deployment failed: {response.text}")

# Usage
generate_and_deploy(
    yaml_file=Path("md01maritalStatus.yaml"),
    joget_api_url="http://localhost:8080/jw",
    api_key="your_api_key"
)
```

---

## Error Handling

### Exception Types

#### ValueError

Raised by `TransformEngine.generate()` when validation fails.

```python
try:
    forms = engine.generate(spec)
except ValueError as e:
    # Error message includes:
    # - All validation errors
    # - Contextual suggestions
    # - Line numbers (if available)
    print(f"Validation failed:\n{e}")
```

#### Example Error Messages

```
Validation failed:
  [form] 'name' is a required property
  💡 Add required property: name

  [fields[2]] 'type' is not one of ['textField', 'selectBox', ...]
  💡 Use one of the supported field types

  [fields[3]] SelectBox requires either 'options' or 'optionsSource'
  💡 Add either static options or optionsSource configuration
```

---

## Type Hints

The API is fully type-hinted for IDE support:

```python
from typing import Optional, Dict, List
from pathlib import Path

def generate_forms(
    spec: Dict,
    output_dir: Optional[Path] = None
) -> Dict[str, Dict]:
    """
    Generate forms with full type safety.

    Args:
        spec: Form specification dictionary
        output_dir: Optional output directory

    Returns:
        Dictionary mapping form IDs to generated JSON
    """
    pass
```

Use with mypy for type checking:
```bash
mypy your_script.py
```

---

## Next Steps

- **[User Guide](USER_GUIDE.md)** - For YAML specification reference
- **[Pattern Development Guide](PATTERN_DEVELOPMENT_GUIDE.md)** - For adding custom field types
- **[Examples](../examples/)** - Practical usage examples

---

**Document Version:** 1.0.0
**API Version:** 1.0.0
**Last Updated:** 2025-01-10
