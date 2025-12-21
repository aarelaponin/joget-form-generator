# Pattern Development Guide

**Version:** 0.2.0
**Last Updated:** 2025-12-19

## Table of Contents

1. [Introduction](#introduction)
2. [Pattern Architecture](#pattern-architecture)
3. [Creating a New Pattern](#creating-a-new-pattern)
4. [Template Development](#template-development)
5. [Mixins and Shared Logic](#mixins-and-shared-logic)
6. [Testing Patterns](#testing-patterns)
7. [Registration](#registration)
8. [Best Practices](#best-practices)
9. [Examples](#examples)

---

## Introduction

This guide explains how to extend the Joget Form Generator with custom field types by creating new **patterns**. Patterns are responsible for transforming YAML field specifications into Joget JSON field definitions.

### When to Create a Custom Pattern

- Adding support for a new Joget field type
- Implementing custom field rendering logic
- Creating organization-specific field configurations
- Extending existing patterns with additional features

### Pattern Lifecycle

```
YAML Field Spec
       ↓
[Pattern.render()]
       ↓
[_prepare_context()]    ← Prepare Jinja2 template context
       ↓
[Template Rendering]    ← Jinja2 renders field JSON
       ↓
[_post_process()]       ← Cleanup and validation
       ↓
Joget JSON Field
```

---

## Pattern Architecture

### Pattern Base Class

All patterns inherit from `BasePattern`:

```python
from joget_form_generator.patterns.base import BasePattern
from typing import Any

class BasePattern(ABC):
    """Abstract base class for field patterns."""

    def __init__(self):
        """Initialize pattern with Jinja2 environment."""
        self.env = self._setup_jinja_env()

    @abstractmethod
    def render(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Render field to Joget JSON.

        Args:
            field: Field specification from YAML
            context: Rendering context (form metadata, etc.)

        Returns:
            Joget JSON field definition
        """
        pass

    def _setup_jinja_env(self) -> jinja2.Environment:
        """Set up Jinja2 environment with custom filters."""
        pass

    def _prepare_context(self, field: dict, context: dict) -> dict:
        """Prepare template context with defaults."""
        pass

    def _post_process(self, result: dict) -> dict:
        """Post-process rendered JSON."""
        pass
```

### Pattern Components

Each pattern typically consists of:

1. **Python Class** - `patterns/<field_type>.py`
   - Inherits from `BasePattern`
   - Implements `render()` method
   - May use mixins for shared logic

2. **Jinja2 Template** - `patterns/templates/<field_type>.j2`
   - Defines Joget JSON structure
   - Uses custom filters for formatting
   - Receives context from Python class

3. **Unit Tests** - `tests/patterns/test_<field_type>.py`
   - Tests pattern rendering
   - Validates Joget JSON structure
   - Covers edge cases

---

## Creating a New Pattern

### Step 1: Define the Pattern Class

Create `src/joget_form_generator/patterns/number_field.py`:

```python
"""NumberField pattern for numeric input."""

from typing import Any
from joget_form_generator.patterns.base import BasePattern
from joget_form_generator.patterns.mixins import ReadOnlyMixin, ValidationMixin


class NumberFieldPattern(ReadOnlyMixin, ValidationMixin, BasePattern):
    """Pattern for rendering number fields."""

    def render(self, field: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Render number field to Joget JSON.

        Args:
            field: Field specification with properties:
                - id: Field ID
                - label: Field label
                - type: "numberField"
                - min: Minimum value (optional)
                - max: Maximum value (optional)
                - step: Increment step (optional, default: 1)
                - decimalPlaces: Number of decimal places (optional)
            context: Rendering context

        Returns:
            Joget JSON field definition
        """
        # Prepare template context
        template_context = self._prepare_context(field, context)

        # Add number-specific properties
        template_context.update({
            "min": field.get("min"),
            "max": field.get("max"),
            "step": field.get("step", 1),
            "decimalPlaces": field.get("decimalPlaces", 0),
        })

        # Build validators
        validators = self._build_validators(field)
        if validators:
            template_context["validator"] = validators

        # Render template
        template = self.env.get_template("number_field.j2")
        result_json = template.render(**template_context)

        # Parse and post-process
        import json
        result = json.loads(result_json)
        return self._post_process(result)
```

### Step 2: Create the Jinja2 Template

Create `src/joget_form_generator/patterns/templates/number_field.j2`:

```jinja2
{
  "className": "org.joget.apps.form.lib.TextField",
  "properties": {
    "id": "{{ id }}",
    "label": "{{ label }}",
    "value": "{{ defaultValue|default('') }}",
    "size": "{{ size|default('medium') }}",
    "maxlength": "{{ maxLength|default('') }}",
    "placeholder": "{{ placeholder|default('') }}",
    "readonly": "{{ readonly|to_joget_bool }}",
    "readonlyLabel": "{{ readonlyLabel|default('') }}",
    "workflowVariable": "",
    {% if validator %}
    "validator": {{ validator|tojson_pretty }},
    {% endif %}
    "encryption": "",
    "storeNumeric": "true",
    "numberMetaData": {
      "min": "{{ min|default('') }}",
      "max": "{{ max|default('') }}",
      "step": "{{ step|default(1) }}",
      "decimalPlaces": "{{ decimalPlaces|default(0) }}"
    }
  }
}
```

### Step 3: Register the Pattern

Add to `src/joget_form_generator/patterns/__init__.py`:

```python
from joget_form_generator.patterns.number_field import NumberFieldPattern

# In __all__ list
__all__ = [
    # ... existing patterns
    "NumberFieldPattern",
]
```

Add to `src/joget_form_generator/patterns/registry.py`:

```python
from joget_form_generator.patterns.number_field import NumberFieldPattern

class PatternRegistry:
    def __init__(self):
        self._patterns = {
            # ... existing patterns
            "numberField": NumberFieldPattern(),
        }
```

### Step 4: Update JSON Schema

Add to `src/joget_form_generator/schema/form_spec_schema.json`:

```json
{
  "$defs": {
    "Field": {
      "properties": {
        "type": {
          "enum": [
            "hiddenField",
            "textField",
            // ... existing types
            "numberField"  // Add new type
          ]
        },
        // Add number field specific properties
        "min": {
          "type": "number",
          "description": "Minimum value (numberField only)"
        },
        "max": {
          "type": "number",
          "description": "Maximum value (numberField only)"
        },
        "step": {
          "type": "number",
          "default": 1,
          "description": "Increment step (numberField only)"
        },
        "decimalPlaces": {
          "type": "integer",
          "minimum": 0,
          "maximum": 10,
          "default": 0,
          "description": "Number of decimal places (numberField only)"
        }
      }
    }
  }
}
```

### Step 5: Write Tests

Create `tests/patterns/test_number_field.py`:

```python
"""Unit tests for NumberFieldPattern."""

import pytest
from joget_form_generator.patterns.number_field import NumberFieldPattern


@pytest.fixture
def pattern():
    """Fixture providing NumberFieldPattern instance."""
    return NumberFieldPattern()


def test_number_field_basic(pattern):
    """Test basic number field rendering."""
    field = {
        "id": "quantity",
        "label": "Quantity",
        "type": "numberField",
        "required": True,
    }
    context = {}

    result = pattern.render(field, context)

    assert result["className"] == "org.joget.apps.form.lib.TextField"
    assert result["properties"]["id"] == "quantity"
    assert result["properties"]["storeNumeric"] == "true"


def test_number_field_with_constraints(pattern):
    """Test number field with min/max/step."""
    field = {
        "id": "price",
        "label": "Price",
        "type": "numberField",
        "min": 0,
        "max": 1000,
        "step": 0.01,
        "decimalPlaces": 2,
    }
    context = {}

    result = pattern.render(field, context)

    metadata = result["properties"]["numberMetaData"]
    assert metadata["min"] == "0"
    assert metadata["max"] == "1000"
    assert metadata["step"] == "0.01"
    assert metadata["decimalPlaces"] == "2"


def test_number_field_validation(pattern):
    """Test number field with validation."""
    field = {
        "id": "age",
        "label": "Age",
        "type": "numberField",
        "required": True,
        "min": 0,
        "max": 150,
    }
    context = {}

    result = pattern.render(field, context)

    # Should have validator for required field
    assert "validator" in result["properties"]
    validator = result["properties"]["validator"]
    assert validator["className"] == "org.joget.apps.form.lib.DefaultValidator"
    assert validator["properties"]["mandatory"] == "true"
```

---

## Template Development

### Jinja2 Custom Filters

The pattern base class provides custom filters:

#### `tojson_pretty`

Formats Python objects as indented JSON.

```jinja2
"validator": {{ validator|tojson_pretty }}
```

Output:
```json
"validator": {
  "className": "org.joget.apps.form.lib.DefaultValidator",
  "properties": {
    "mandatory": "true"
  }
}
```

#### `to_joget_bool`

Converts Python boolean to Joget string boolean.

```jinja2
"readonly": "{{ readonly|to_joget_bool }}"
```

- `True` → `"true"`
- `False` → `"false"`
- `None` → `"false"`

### Template Best Practices

1. **Use defaults for optional properties**
   ```jinja2
   "placeholder": "{{ placeholder|default('') }}"
   ```

2. **Conditional sections for complex properties**
   ```jinja2
   {% if validator %}
   "validator": {{ validator|tojson_pretty }},
   {% endif %}
   ```

3. **Avoid trailing commas**
   ```jinja2
   {
     "property1": "value1"{% if property2 %},{% endif %}
     {% if property2 %}"property2": "{{ property2 }}"{% endif %}
   }
   ```

4. **Format numbers as strings** (Joget requirement)
   ```jinja2
   "maxlength": "{{ maxLength|default('') }}"
   ```

---

## Mixins and Shared Logic

### Available Mixins

#### ReadOnlyMixin

Handles `readonly` and `required` properties.

```python
from joget_form_generator.patterns.mixins import ReadOnlyMixin

class MyPattern(ReadOnlyMixin, BasePattern):
    pass
```

**Adds:**
- `readonly` property handling
- `readonlyLabel` support

#### ValidationMixin

Builds Joget validators.

```python
from joget_form_generator.patterns.mixins import ValidationMixin

class MyPattern(ValidationMixin, BasePattern):
    def render(self, field, context):
        validators = self._build_validators(field)
        # Use validators in template context
```

**Methods:**
- `_build_validators(field)` - Returns validator dict or None
- Supports: DefaultValidator, RegexValidator, length validators

#### OptionsMixin

Builds options binders for select-based fields.

```python
from joget_form_generator.patterns.mixins import OptionsMixin

class MyPattern(OptionsMixin, BasePattern):
    def render(self, field, context):
        if "options" in field:
            options_binder = self._build_static_options(field["options"])
        elif "optionsSource" in field:
            options_binder = self._build_dynamic_options(field["optionsSource"], context)
        # Use options_binder in template
```

**Methods:**
- `_build_static_options(options)` - For static options
- `_build_dynamic_options(source, context)` - For formData, api, database sources

### Creating Custom Mixins

```python
from typing import Any

class CustomFormattingMixin:
    """Mixin for custom formatting logic."""

    def _format_currency(self, value: float) -> str:
        """Format value as currency."""
        return f"${value:,.2f}"

    def _apply_custom_styling(self, field: dict) -> dict:
        """Apply organization-specific styling."""
        if field.get("important"):
            return {
                "style": "background-color: #ffebee; font-weight: bold;"
            }
        return {}
```

Usage:
```python
class PriceFieldPattern(CustomFormattingMixin, ValidationMixin, BasePattern):
    def render(self, field, context):
        template_context = self._prepare_context(field, context)

        # Use mixin methods
        if "defaultValue" in field:
            template_context["formattedDefault"] = self._format_currency(field["defaultValue"])

        styling = self._apply_custom_styling(field)
        template_context.update(styling)

        # ... render template
```

---

## Testing Patterns

### Unit Test Structure

```python
import pytest
from joget_form_generator.patterns.my_pattern import MyPattern


@pytest.fixture
def pattern():
    """Provide pattern instance for all tests."""
    return MyPattern()


class TestBasicRendering:
    """Test basic field rendering."""

    def test_minimal_field(self, pattern):
        """Test field with only required properties."""
        field = {
            "id": "myField",
            "label": "My Field",
            "type": "myType",
        }
        context = {}

        result = pattern.render(field, context)

        assert result["className"] == "org.joget.apps.form.lib.MyFieldClass"
        assert result["properties"]["id"] == "myField"
        assert result["properties"]["label"] == "My Field"


class TestPropertyHandling:
    """Test specific property handling."""

    def test_custom_property(self, pattern):
        """Test custom property rendering."""
        field = {
            "id": "field1",
            "label": "Field 1",
            "type": "myType",
            "customProp": "customValue",
        }
        context = {}

        result = pattern.render(field, context)

        assert result["properties"]["customProp"] == "customValue"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_missing_optional_property(self, pattern):
        """Test field with missing optional property."""
        field = {
            "id": "field1",
            "label": "Field 1",
            "type": "myType",
            # customProp is missing
        }
        context = {}

        result = pattern.render(field, context)

        # Should use default value
        assert result["properties"].get("customProp", "") == ""
```

### Integration Test Example

```python
def test_pattern_in_full_form():
    """Test pattern in complete form generation."""
    from joget_form_generator.transformers.engine import TransformEngine

    spec = {
        "form": {
            "id": "testForm",
            "name": "Test Form",
        },
        "fields": [
            {
                "id": "myField",
                "label": "My Field",
                "type": "myType",
                "customProp": "value",
            }
        ],
    }

    engine = TransformEngine()
    forms = engine.generate(spec)

    # Navigate to field in generated form
    form = forms["testForm"]
    section = form["elements"][0]
    column = section["elements"][0]
    field = column["elements"][0]

    # Verify field structure
    assert field["className"] == "org.joget.apps.form.lib.MyFieldClass"
    assert field["properties"]["customProp"] == "value"
```

---

## Registration

### Pattern Registry

Patterns must be registered in `PatternRegistry` to be available:

```python
# src/joget_form_generator/patterns/registry.py

from joget_form_generator.patterns.base import BasePattern
from joget_form_generator.patterns.my_pattern import MyPattern


class PatternRegistry:
    """Registry of available field patterns."""

    def __init__(self):
        """Initialize registry with all patterns."""
        self._patterns: dict[str, BasePattern] = {
            "hiddenField": HiddenFieldPattern(),
            "textField": TextFieldPattern(),
            # ... existing patterns
            "myType": MyPattern(),  # Add new pattern
        }

    def get_pattern(self, field_type: str) -> BasePattern:
        """Get pattern instance for field type."""
        if field_type not in self._patterns:
            raise ValueError(
                f"Unknown field type: {field_type}. "
                f"Supported types: {list(self._patterns.keys())}"
            )
        return self._patterns[field_type]
```

### Dynamic Registration

For plugins or runtime registration:

```python
class PatternRegistry:
    def register(self, field_type: str, pattern: BasePattern):
        """Register a custom pattern."""
        self._patterns[field_type] = pattern

    def unregister(self, field_type: str):
        """Unregister a pattern."""
        if field_type in self._patterns:
            del self._patterns[field_type]


# Usage
registry = PatternRegistry()
registry.register("customType", CustomPattern())
```

---

## Best Practices

### 1. Follow Naming Conventions

- **Pattern Class**: `<FieldType>Pattern` (e.g., `TextFieldPattern`)
- **Template File**: `<field_type>.j2` (e.g., `text_field.j2`)
- **Test File**: `test_<field_type>.py` (e.g., `test_text_field.py`)

### 2. Use Mixins for Shared Logic

Don't duplicate code across patterns. Extract common logic into mixins:

```python
# Good
class SelectBoxPattern(OptionsMixin, ValidationMixin, BasePattern):
    pass

# Bad - duplicates validation logic
class SelectBoxPattern(BasePattern):
    def _build_validators(self, field):  # Duplicate code!
        # ... 50 lines of validation logic
```

### 3. Validate Input in render()

```python
def render(self, field, context):
    # Validate required properties
    if "options" not in field and "optionsSource" not in field:
        raise ValueError(
            f"SelectBox field '{field['id']}' requires either 'options' or 'optionsSource'"
        )

    # Continue with rendering
    ...
```

### 4. Document Template Context

```python
def render(self, field, context):
    """
    Render field to Joget JSON.

    Template Context:
        id: Field ID
        label: Field label
        customProp: Custom property value
        validator: Validator configuration (if required=true)
    """
    pass
```

### 5. Handle Defaults Properly

```python
# In pattern class
template_context = {
    "id": field["id"],
    "label": field["label"],
    "customProp": field.get("customProp", "defaultValue"),
}

# In template
"customProp": "{{ customProp }}"  # Already has default from Python
```

### 6. Test Edge Cases

```python
def test_empty_options(pattern):
    """Test select box with no options (should fail)."""
    field = {
        "id": "category",
        "label": "Category",
        "type": "selectBox",
        # Missing: options or optionsSource
    }

    with pytest.raises(ValueError, match="requires either"):
        pattern.render(field, {})
```

---

## Examples

### Example 1: Simple Pattern (Read-Only Field)

```python
# src/joget_form_generator/patterns/display_field.py

class DisplayFieldPattern(BasePattern):
    """Pattern for read-only display fields."""

    def render(self, field, context):
        template_context = self._prepare_context(field, context)

        template = self.env.get_template("display_field.j2")
        result_json = template.render(**template_context)

        import json
        return self._post_process(json.loads(result_json))
```

```jinja2
{# src/joget_form_generator/patterns/templates/display_field.j2 #}
{
  "className": "org.joget.apps.form.lib.CustomHTML",
  "properties": {
    "id": "{{ id }}",
    "label": "{{ label }}",
    "value": "<div class='display-field'>{{ defaultValue|default('') }}</div>"
  }
}
```

### Example 2: Complex Pattern (Rich Text Editor)

```python
# src/joget_form_generator/patterns/rich_text.py

class RichTextPattern(ValidationMixin, BasePattern):
    """Pattern for rich text editor field."""

    def render(self, field, context):
        template_context = self._prepare_context(field, context)

        # Rich text specific properties
        template_context.update({
            "toolbar": field.get("toolbar", "full"),
            "height": field.get("height", 300),
            "allowImages": field.get("allowImages", True),
            "allowTables": field.get("allowTables", True),
        })

        # Validators
        validators = self._build_validators(field)
        if validators:
            template_context["validator"] = validators

        template = self.env.get_template("rich_text.j2")
        result_json = template.render(**template_context)

        import json
        return self._post_process(json.loads(result_json))
```

### Example 3: Pattern with Custom Validation

```python
# src/joget_form_generator/patterns/phone_field.py

class PhoneFieldPattern(ValidationMixin, BasePattern):
    """Pattern for phone number field with format validation."""

    PHONE_PATTERNS = {
        "US": r"^\+1[0-9]{10}$",
        "UK": r"^\+44[0-9]{10}$",
        "international": r"^\+[0-9]{10,15}$",
    }

    def render(self, field, context):
        template_context = self._prepare_context(field, context)

        # Get phone format
        phone_format = field.get("phoneFormat", "international")

        # Build custom validator
        validators = self._build_phone_validator(field, phone_format)
        if validators:
            template_context["validator"] = validators

        template = self.env.get_template("phone_field.j2")
        result_json = template.render(**template_context)

        import json
        return self._post_process(json.loads(result_json))

    def _build_phone_validator(self, field, phone_format):
        """Build validator for phone number format."""
        pattern = self.PHONE_PATTERNS.get(phone_format)

        if pattern:
            return {
                "className": "org.joget.apps.form.lib.RegexValidator",
                "properties": {
                    "pattern": pattern,
                    "errorMessage": field.get(
                        "validationMessage",
                        f"Please enter a valid {phone_format} phone number"
                    ),
                },
            }

        # Use standard validators
        return self._build_validators(field)
```

---

## Next Steps

- Review existing patterns in `src/joget_form_generator/patterns/`
- Study Joget DX field types documentation
- Implement Phase 2 field types (Grid, Subform, Custom HTML, ID Generator)

---

**Document Version:** 0.2.0
**Last Updated:** 2025-12-19
