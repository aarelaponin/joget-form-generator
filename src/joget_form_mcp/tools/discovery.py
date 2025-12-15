"""
Discovery tools for MCP server.

Provides tools to discover field types, get documentation, and retrieve examples.
"""

import logging
from typing import Any

from joget_form_generator.patterns import PatternRegistry

logger = logging.getLogger(__name__)


# Field type metadata with descriptions and properties
FIELD_TYPE_INFO = {
    # Standard fields (Phase 1)
    "hiddenField": {
        "category": "standard",
        "description": "Hidden field for storing values not visible to users",
        "use_cases": ["Store IDs", "Pass workflow variables", "Hidden defaults"],
        "properties": ["id", "value", "workflowVariable"],
        "example": {"id": "recordId", "type": "hiddenField", "value": "#currentUser.id#"},
    },
    "textField": {
        "category": "standard",
        "description": "Single-line text input field",
        "use_cases": ["Names", "Email", "Phone", "Short text"],
        "properties": [
            "id",
            "label",
            "required",
            "placeholder",
            "maxLength",
            "validator",
            "readonly",
        ],
        "validators": ["email", "numeric", "alphanumeric", "regex"],
        "example": {
            "id": "email",
            "label": "Email Address",
            "type": "textField",
            "required": True,
            "validator": {"type": "email", "message": "Please enter valid email"},
        },
    },
    "passwordField": {
        "category": "standard",
        "description": "Password input with masked display",
        "use_cases": ["Password entry", "PIN codes", "Sensitive data"],
        "properties": ["id", "label", "required", "placeholder", "maxLength"],
        "example": {
            "id": "password",
            "label": "Password",
            "type": "passwordField",
            "required": True,
        },
    },
    "textArea": {
        "category": "standard",
        "description": "Multi-line text input",
        "use_cases": ["Comments", "Descriptions", "Notes", "Long text"],
        "properties": ["id", "label", "required", "rows", "cols", "placeholder", "maxLength"],
        "example": {
            "id": "description",
            "label": "Description",
            "type": "textArea",
            "rows": 5,
            "cols": 60,
        },
    },
    "selectBox": {
        "category": "standard",
        "description": "Dropdown selection with static or dynamic options",
        "use_cases": ["Status selection", "Categories", "Lookup values", "Cascading dropdowns"],
        "properties": ["id", "label", "required", "options", "optionsSource", "multiple"],
        "options_sources": ["static", "formData", "api", "database"],
        "example": {
            "id": "status",
            "label": "Status",
            "type": "selectBox",
            "required": True,
            "options": [
                {"value": "active", "label": "Active"},
                {"value": "inactive", "label": "Inactive"},
            ],
        },
    },
    "checkBox": {
        "category": "standard",
        "description": "Multiple selection checkboxes",
        "use_cases": ["Multi-select options", "Boolean flags", "Feature toggles"],
        "properties": ["id", "label", "required", "options"],
        "example": {
            "id": "features",
            "label": "Features",
            "type": "checkBox",
            "options": [
                {"value": "wifi", "label": "WiFi"},
                {"value": "parking", "label": "Parking"},
            ],
        },
    },
    "radio": {
        "category": "standard",
        "description": "Single selection radio buttons",
        "use_cases": ["Yes/No questions", "Single choice from small set"],
        "properties": ["id", "label", "required", "options"],
        "example": {
            "id": "gender",
            "label": "Gender",
            "type": "radio",
            "options": [{"value": "M", "label": "Male"}, {"value": "F", "label": "Female"}],
        },
    },
    "datePicker": {
        "category": "standard",
        "description": "Date selection with calendar popup",
        "use_cases": ["Birth dates", "Due dates", "Event dates"],
        "properties": [
            "id",
            "label",
            "required",
            "dateFormat",
            "startDateFieldId",
            "endDateFieldId",
        ],
        "formats": ["yyyy-MM-dd", "dd/MM/yyyy", "MM/dd/yyyy"],
        "example": {
            "id": "birthDate",
            "label": "Date of Birth",
            "type": "datePicker",
            "dateFormat": "yyyy-MM-dd",
        },
    },
    "fileUpload": {
        "category": "standard",
        "description": "File upload field",
        "use_cases": ["Document uploads", "Images", "Attachments"],
        "properties": ["id", "label", "required", "allowedTypes", "maxSize", "multiple"],
        "example": {
            "id": "documents",
            "label": "Upload Documents",
            "type": "fileUpload",
            "allowedTypes": ["pdf", "doc", "docx"],
            "maxSize": 10485760,
        },
    },
    # Advanced fields (Phase 2)
    "customHTML": {
        "category": "advanced",
        "description": "Custom HTML content for display or complex layouts",
        "use_cases": ["Instructions", "Headers", "Custom widgets", "Embedded content"],
        "properties": ["id", "label", "html", "cssClass"],
        "example": {
            "id": "instructions",
            "label": "Instructions",
            "type": "customHTML",
            "html": "<div class='alert alert-info'>Please fill all required fields.</div>",
        },
    },
    "idGenerator": {
        "category": "advanced",
        "description": "Auto-generated unique ID field",
        "use_cases": ["Record IDs", "Reference numbers", "Sequential codes"],
        "properties": ["id", "label", "format", "envVariable"],
        "formats": ["???", "APP-???", "YYYY-MM-???"],
        "example": {
            "id": "referenceNo",
            "label": "Reference Number",
            "type": "idGenerator",
            "format": "REF-???",
        },
    },
    "subform": {
        "category": "advanced",
        "description": "Embed another form (master-detail pattern)",
        "use_cases": ["Master-detail records", "Embedded forms", "Related data"],
        "properties": ["id", "label", "formId", "parentField", "foreignKeyField", "readonly"],
        "example": {
            "id": "addresses",
            "label": "Addresses",
            "type": "subform",
            "formId": "addressForm",
            "parentField": "id",
            "foreignKeyField": "customerId",
        },
    },
    "grid": {
        "category": "advanced",
        "description": "Simple tabular data entry grid",
        "use_cases": ["Line items", "Repeating data", "Simple lists"],
        "properties": ["id", "label", "columns", "minRows", "maxRows"],
        "column_types": ["textField", "selectBox", "datePicker"],
        "example": {
            "id": "lineItems",
            "label": "Line Items",
            "type": "grid",
            "columns": [
                {"id": "description", "label": "Description", "type": "textField"},
                {"id": "quantity", "label": "Qty", "type": "textField"},
                {"id": "price", "label": "Price", "type": "textField"},
            ],
        },
    },
    # Enterprise fields (Phase 3)
    "calculationField": {
        "category": "enterprise",
        "description": "Computed field with arithmetic expressions",
        "use_cases": ["Totals", "Tax calculations", "Derived values"],
        "properties": ["id", "label", "equation", "storeNumeric", "readonly", "cssClass"],
        "operators": ["+", "-", "*", "/", "(", ")"],
        "example": {
            "id": "total",
            "label": "Total",
            "type": "calculationField",
            "equation": "quantity * unitPrice",
            "storeNumeric": True,
            "readonly": True,
        },
    },
    "richTextEditor": {
        "category": "enterprise",
        "description": "WYSIWYG HTML editor (TinyMCE/Quill)",
        "use_cases": ["Formatted content", "Email templates", "Rich descriptions"],
        "properties": ["id", "label", "required", "height", "toolbar", "editorType"],
        "editor_types": ["tinymce", "quill"],
        "example": {
            "id": "content",
            "label": "Content",
            "type": "richTextEditor",
            "height": 300,
            "editorType": "tinymce",
        },
    },
    "formGrid": {
        "category": "enterprise",
        "description": "Advanced grid supporting complex field types in cells",
        "use_cases": ["Complex line items", "Nested data", "Invoice lines with calculations"],
        "properties": ["id", "label", "columns", "minRows", "maxRows", "showRowNumber"],
        "column_types": ["textField", "selectBox", "datePicker", "calculationField", "fileUpload"],
        "example": {
            "id": "invoiceLines",
            "label": "Invoice Lines",
            "type": "formGrid",
            "columns": [
                {"id": "item", "label": "Item", "type": "selectBox"},
                {"id": "qty", "label": "Quantity", "type": "textField"},
                {"id": "price", "label": "Unit Price", "type": "textField"},
                {
                    "id": "total",
                    "label": "Line Total",
                    "type": "calculationField",
                    "equation": "qty * price",
                },
            ],
        },
    },
    "multiPagedForm": {
        "category": "enterprise",
        "description": "Multi-step wizard form with page navigation",
        "use_cases": ["Wizards", "Long forms", "Step-by-step processes"],
        "properties": ["id", "label", "pages", "showPageNumbers", "allowBackNavigation"],
        "example": {
            "id": "registrationWizard",
            "label": "Registration",
            "type": "multiPagedForm",
            "pages": [
                {"id": "page1", "label": "Personal Info", "fields": ["name", "email"]},
                {"id": "page2", "label": "Address", "fields": ["street", "city"]},
                {"id": "page3", "label": "Review", "fields": ["summary"]},
            ],
        },
    },
}


# Example specifications
EXAMPLES = {
    "simple-form": """# Simple Contact Form
form:
  id: contactForm
  name: Contact Form
  description: Simple contact form example

fields:
  - id: fullName
    label: Full Name
    type: textField
    required: true
    placeholder: Enter your full name

  - id: email
    label: Email Address
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
""",
    "cascading-dropdown": """# Cascading Dropdown Example (Equipment Category → Equipment)
form:
  id: md25equipment
  name: MD.25 - Equipment
  description: Equipment with cascading category dropdown

fields:
  - id: code
    label: Code
    type: textField
    required: true

  - id: name
    label: Name
    type: textField
    required: true

  - id: categoryCode
    label: Category
    type: selectBox
    required: true
    optionsSource:
      type: formData
      formId: md25equipCategory
      valueColumn: code
      labelColumn: name
""",
    "mdm-form": """# Master Data Management Form
form:
  id: md01maritalStatus
  name: MD.01 - Marital Status
  description: Simple MDM lookup table

fields:
  - id: code
    label: Code
    type: textField
    required: true
    maxLength: 10

  - id: name
    label: Name
    type: textField
    required: true
    maxLength: 100

  - id: description
    label: Description
    type: textArea
    rows: 3
""",
    "enterprise-showcase": """# Enterprise Features Showcase
form:
  id: invoiceForm
  name: Invoice Form
  description: Demonstrates enterprise field types

fields:
  - id: invoiceNo
    label: Invoice Number
    type: idGenerator
    format: INV-????

  - id: customer
    label: Customer
    type: textField
    required: true

  - id: subtotal
    label: Subtotal
    type: textField
    required: true
    defaultValue: "0.00"

  - id: taxRate
    label: Tax Rate (%)
    type: textField
    defaultValue: "10"

  - id: tax
    label: Tax Amount
    type: calculationField
    equation: subtotal * (taxRate / 100)
    storeNumeric: true
    readonly: true

  - id: total
    label: Total
    type: calculationField
    equation: subtotal + tax
    storeNumeric: true
    readonly: true

  - id: notes
    label: Notes
    type: richTextEditor
    height: 200
""",
    "calculation-form": """# Calculation Field Examples
form:
  id: orderCalculation
  name: Order Calculation Demo
  description: Shows various calculation patterns

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

  - id: discount
    label: Discount (%)
    type: textField
    defaultValue: "0"

  - id: subtotal
    label: Subtotal
    type: calculationField
    equation: quantity * unitPrice
    readonly: true

  - id: discountAmount
    label: Discount Amount
    type: calculationField
    equation: subtotal * (discount / 100)
    readonly: true

  - id: total
    label: Total
    type: calculationField
    equation: subtotal - discountAmount
    storeNumeric: true
    readonly: true
""",
    "multi-page-form": """# Multi-Page Wizard Form
form:
  id: registrationWizard
  name: Registration Wizard
  description: Multi-step registration form

fields:
  # Page 1: Personal Information
  - id: firstName
    label: First Name
    type: textField
    required: true

  - id: lastName
    label: Last Name
    type: textField
    required: true

  - id: email
    label: Email
    type: textField
    required: true
    validator:
      type: email

  # Page 2: Address
  - id: street
    label: Street Address
    type: textField
    required: true

  - id: city
    label: City
    type: textField
    required: true

  - id: postalCode
    label: Postal Code
    type: textField

  # Page 3: Preferences
  - id: newsletter
    label: Subscribe to Newsletter
    type: checkBox
    options:
      - value: "yes"
        label: "Yes, send me updates"

  - id: termsAccepted
    label: Terms & Conditions
    type: checkBox
    required: true
    options:
      - value: "accepted"
        label: "I accept the terms and conditions"
""",
}


class DiscoveryTools:
    """Tools for discovering field types, documentation, and examples."""

    def list_field_types(self) -> dict[str, Any]:
        """
        List all supported field types grouped by category.

        Returns:
            Dictionary with field types by category
        """
        # Get registered types from pattern registry
        registered = PatternRegistry.list_types()

        # Group by category
        categories = {"standard": [], "advanced": [], "enterprise": []}

        for field_type in registered:
            info = FIELD_TYPE_INFO.get(field_type, {})
            category = info.get("category", "standard")
            categories[category].append(
                {
                    "type": field_type,
                    "description": info.get("description", "No description available"),
                    "use_cases": info.get("use_cases", []),
                }
            )

        return {
            "total_types": len(registered),
            "categories": categories,
            "registered_types": registered,
        }

    def get_field_type_info(self, field_type: str) -> dict[str, Any]:
        """
        Get detailed information about a specific field type.

        Args:
            field_type: Field type name

        Returns:
            Detailed field type information
        """
        if field_type not in FIELD_TYPE_INFO:
            # Check if it's registered but not documented
            if PatternRegistry.is_registered(field_type):
                return {
                    "type": field_type,
                    "registered": True,
                    "documented": False,
                    "message": f"Field type '{field_type}' is registered but documentation is pending",
                }
            return {
                "error": f"Unknown field type: '{field_type}'",
                "available_types": PatternRegistry.list_types(),
            }

        info = FIELD_TYPE_INFO[field_type].copy()
        info["type"] = field_type
        info["registered"] = PatternRegistry.is_registered(field_type)

        return info

    def get_example_spec(self, example_name: str) -> dict[str, Any]:
        """
        Get an example YAML specification.

        Args:
            example_name: Name of the example

        Returns:
            Dictionary with example YAML and description
        """
        # Normalize name (handle both "simple_form" and "simple-form")
        normalized_name = example_name.replace("_", "-").lower()

        if normalized_name not in EXAMPLES:
            return {
                "error": f"Example not found: '{example_name}'",
                "available_examples": list(EXAMPLES.keys()),
            }

        return {
            "name": normalized_name,
            "yaml_spec": EXAMPLES[normalized_name],
            "description": f"Example specification: {normalized_name}",
        }

    def get_field_types_documentation(self) -> str:
        """Get complete field types documentation as Markdown."""
        lines = [
            "# Joget Form Generator - Field Types Documentation\n",
            "## Overview\n",
            f"Total supported field types: {len(FIELD_TYPE_INFO)}\n",
        ]

        for category in ["standard", "advanced", "enterprise"]:
            lines.append(f"\n## {category.title()} Fields\n")

            for field_type, info in FIELD_TYPE_INFO.items():
                if info.get("category") == category:
                    lines.append(f"### {field_type}\n")
                    lines.append(f"**Description:** {info.get('description', 'N/A')}\n")
                    lines.append(f"**Use Cases:** {', '.join(info.get('use_cases', []))}\n")
                    lines.append(f"**Properties:** `{', '.join(info.get('properties', []))}`\n")

                    if "example" in info:
                        lines.append("\n**Example:**\n```yaml")
                        for key, value in info["example"].items():
                            lines.append(f"  {key}: {value}")
                        lines.append("```\n")

        return "\n".join(lines)

    def get_cascading_dropdown_documentation(self) -> str:
        """Get cascading dropdown documentation as Markdown."""
        return """# Cascading Dropdowns Guide (Nested LOV)

## Overview

Cascading dropdowns allow child select boxes to filter based on parent selection.
This is commonly used for hierarchical data like:
- Country → State → City
- Category → Subcategory → Item
- Equipment Category → Equipment Type

## Pattern: formData Options Source

### Parent Form (md25equipCategory)
```yaml
form:
  id: md25equipCategory
  name: MD.25 - Equipment Category

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

### Child Form (md25equipment)
```yaml
form:
  id: md25equipment
  name: MD.25 - Equipment

fields:
  - id: code
    label: Code
    type: textField
    required: true

  - id: name
    label: Name
    type: textField
    required: true

  - id: categoryCode
    label: Category
    type: selectBox
    required: true
    optionsSource:
      type: formData
      formId: md25equipCategory  # References parent form
      valueColumn: code           # Value stored in child record
      labelColumn: name           # Display text in dropdown
```

## How It Works

1. **Parent form** stores lookup values (code, name)
2. **Child form** references parent via `optionsSource.formId`
3. Joget automatically:
   - Fetches options from parent form's data
   - Populates dropdown dynamically
   - Stores selected value in child record

## Multi-Level Cascading

For 3+ levels (e.g., Category → Subcategory → Item):

```yaml
# Level 1: Category (no parent)
form:
  id: category
  name: Category

# Level 2: Subcategory (parent: category)
fields:
  - id: categoryCode
    type: selectBox
    optionsSource:
      type: formData
      formId: category
      valueColumn: code
      labelColumn: name

# Level 3: Item (parent: subcategory)
fields:
  - id: subcategoryCode
    type: selectBox
    optionsSource:
      type: formData
      formId: subcategory
      valueColumn: code
      labelColumn: name
      # Filter by parent selection
      filterColumn: categoryCode
      filterValue: "#form.categoryCode#"
```

## Best Practices

1. Use consistent naming: `parentCode` for FK fields
2. Always set `required: true` for FK fields
3. Use meaningful labels in parent forms
4. Consider API source for large datasets

## References

- Joget Documentation: https://dev.joget.org/community/display/DX8/Select+Box
- METADATA_MANUAL.md: Pattern 2 (Parent-child hierarchies)
"""
