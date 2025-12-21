# Enterprise Edition Field Types

This document describes the 4 Enterprise Edition field types supported by the Joget Form Generator.

## Overview

The form generator supports **17 field types** total:
- **Phase 1 (9 standard fields)**: hiddenField, textField, passwordField, textArea, selectBox, checkBox, radio, datePicker, fileUpload
- **Phase 2 (4 advanced fields)**: customHTML, idGenerator, subform, grid
- **Phase 3 (4 Enterprise fields)**: calculationField, richTextEditor, formGrid, multiPagedForm

**Note**: Multi Select Box is not a separate field type - use `selectBox` with `multiple: true`.

## Enterprise Field Types

### Multi Select Box (Not a Separate Type)

**Description**: SelectBox with multi-selection capability and auto-complete behavior. Useful for selecting multiple items from long lists.

**Availability**: Professional and Enterprise Editions

**Implementation**: Use the standard `selectBox` field type with `multiple: true`. This is not a separate field type.

**Properties**:
- `multiple`: Set to `true` for multi-selection
- `size`: Controls visible options (default: 10)
- All standard SelectBox properties apply

**Example**:
```yaml
fields:
  - id: technologies
    label: Technologies
    type: selectBox
    multiple: true
    size: large
    options:
      - value: java
        label: Java
      - value: python
        label: Python
```

**Joget className**: `org.joget.apps.form.lib.SelectBox` (with `multiple: "true"`)

---

### 1. Calculation Field

**Description**: Performs arithmetic computations on form field values. Results can be stored as numeric or string values.

**Availability**: Professional and Enterprise Editions

**Properties**:
- `equation` **(required)**: Mathematical expression to calculate (e.g., `"fieldA + fieldB"`, `"quantity * price"`)
- `storeNumeric`: Whether to store result as number (default: `true`)
- `defaultValue`: Fallback value if calculation fails
- `readonly`: Typically set to `true` since values are calculated

**Example**:
```yaml
fields:
  - id: quantity
    label: Quantity
    type: textField
    defaultValue: "1"

  - id: unitPrice
    label: Unit Price
    type: textField
    defaultValue: "100.00"

  - id: total
    label: Total
    type: calculationField
    equation: quantity * unitPrice
    storeNumeric: true
    readonly: true
```

**Joget className**: `org.joget.plugin.enterprise.CalculationField`

**Common Use Cases**:
- Order totals: `(quantity * price) * (1 + tax/100)`
- Discounts: `price * (1 - discount/100)`
- Subtotals and tax calculations
- Complex financial formulas

---

### 2. Rich Text Editor

**Description**: WYSIWYG HTML editor for creating formatted content. Supports two editor types: TinyMCE and Quill.

**Availability**: Enterprise Edition only

**Properties**:
- `editor`: Editor type - `"tinymce"` or `"quill"` (default: `"tinymce"`)
- `rows`: Height in rows (default: 10)
- `placeholder`: Placeholder text
- `defaultValue`: Default HTML content
- `required`: Whether content is required
- `readonly`: Read-only mode

**Example**:
```yaml
fields:
  - id: description
    label: Product Description
    type: richTextEditor
    editor: tinymce
    rows: 15
    placeholder: Enter detailed description...
    required: true

  - id: emailTemplate
    label: Email Template
    type: richTextEditor
    editor: quill
    rows: 12
    defaultValue: <p>Dear <strong>Customer</strong>,</p>
```

**Joget className**: `org.joget.plugin.enterprise.RichTextEditor`

**Common Use Cases**:
- Product descriptions
- Email templates
- Article content
- Formatted notes and documentation
- Terms and conditions

---

### 3. Form Grid

**Description**: Advanced grid that extends the default grid functionality. Supports complex field types within cells including selectBox, datePicker, and more.

**Availability**: Professional and Enterprise Editions

**Properties**:
- `columns` **(required)**: Array of column definitions
  - `id`: Column identifier
  - `label`: Column label
  - `type`: Field type (`textField`, `selectBox`, `datePicker`, `checkBox`)
  - `options`: For selectBox columns (array of `{value, label}`)
  - `editable`: Whether column is editable (default: `true`)
- `formId`: Referenced form ID for grid rows
- `validateMinRow`: Minimum number of rows
- `validateMaxRow`: Maximum number of rows
- `allowAddRow`: Allow adding new rows (default: `true`)
- `allowDeleteRow`: Allow deleting rows (default: `true`)
- `readonly`: Make entire grid read-only

**Example**:
```yaml
fields:
  - id: orderLines
    label: Order Line Items
    type: formGrid
    validateMinRow: 1
    validateMaxRow: 20
    allowAddRow: true
    allowDeleteRow: true
    columns:
      - id: product
        label: Product
        type: textField
        editable: true
      - id: quantity
        label: Qty
        type: textField
        editable: true
      - id: status
        label: Status
        type: selectBox
        editable: true
        options:
          - value: pending
            label: Pending
          - value: shipped
            label: Shipped
```

**Joget className**: `org.joget.plugin.enterprise.FormGrid`

**Difference from Regular Grid**:
- Regular `grid`: Simple table with text columns only
- `formGrid`: Supports complex field types (selectBox, datePicker, etc.) in cells

**Common Use Cases**:
- Order line items with product selection
- Task lists with status dropdowns
- Expense reports with date pickers
- Dynamic data entry tables

---

### 4. Multi Paged Form

**Description**: Incorporates multiple forms in one single form with elegant page navigation. Ideal for multi-step wizards and workflows.

**Availability**: Professional and Enterprise Editions

**Properties**:
- `pages` **(required)**: Array of page definitions
  - `formId` **(required)**: Referenced form ID for this page
  - `label`: Page label/title
  - `description`: Page description text
- `showNavigation`: Show page navigation controls (default: `true`)
- `showProgressBar`: Show progress bar (default: `true`)
- `readonly`: Make all pages read-only

**Example**:
```yaml
fields:
  - id: registrationWizard
    label: User Registration
    type: multiPagedForm
    showNavigation: true
    showProgressBar: true
    pages:
      - formId: personalInfo
        label: Personal Information
        description: Enter your basic details
      - formId: addressInfo
        label: Address
        description: Provide your contact information
      - formId: preferences
        label: Preferences
        description: Set your account preferences
```

**Joget className**: `org.joget.plugin.enterprise.PageFormElement`

**Common Use Cases**:
- Multi-step registration forms
- Application wizards
- Survey forms
- Onboarding processes
- Complex data entry workflows

---

## Testing

All Enterprise field types have comprehensive test coverage:

```bash
# Run Enterprise field tests only
pytest tests/patterns/test_calculation_field.py \
      tests/patterns/test_rich_text_editor.py \
      tests/patterns/test_form_grid.py \
      tests/patterns/test_multi_paged_form.py

# Run all tests
pytest tests/
```

Run `pytest --cov=src` for current test statistics and coverage.

## Examples

See `examples/enterprise_showcase.yaml` for a comprehensive demonstration of all Enterprise field types.

Generate the example:
```bash
joget-form-gen generate examples/enterprise_showcase.yaml
```

## Schema Validation

Enterprise field types are fully validated by the JSON Schema at `src/joget_form_generator/schema/form_spec_schema.json`.

Validate your YAML:
```bash
joget-form-gen validate your-form.yaml
```

## Notes

1. **Multi Select Box** is implemented using the standard `selectBox` with `multiple: true` - no separate field type needed.

2. **Calculation Field** formulas can reference any field ID in the form. Complex formulas are supported: `(field1 + field2) * (1 + tax/100)`.

3. **Rich Text Editor** supports both TinyMCE and Quill editors. Choose based on your requirements.

4. **Form Grid** is more powerful than regular Grid - use it when you need dropdown selections, date pickers, or complex validation within grid cells.

5. **Multi Paged Form** references child form IDs - ensure those forms exist before deploying the parent form.

6. All Enterprise field types support standard properties like `required`, `readonly`, and validation where applicable.

---

## Composite Patterns (Enterprise)

Beyond individual field types, Joget Enterprise Edition enables powerful **composite patterns** that combine multiple elements for advanced functionality.

### AJAX Subform Pattern

**Description**: Dynamic form loading based on dropdown selection. When a user selects a record from a SelectBox, an AjaxSubForm automatically loads and displays that record's details.

**Components**:
- `SelectBox` with `FormOptionsBinder` (trigger)
- `AjaxSubForm` element (display)

**Use cases**:
- Master-detail views (select customer → show details)
- Reference data lookup (select equipment → show specifications)
- Read-only data display from related records

**Critical configuration** (undocumented in official Joget docs):

| Property | Location | Required Value | Why |
|----------|----------|----------------|-----|
| `idColumn` | SelectBox optionsBinder | `""` (empty) | AjaxSubForm looks up by primary key |
| `ajax` | AjaxSubForm | `"true"` | Enables dynamic reload |
| `parentSubFormId` | AjaxSubForm | SelectBox field ID | Links to trigger field |

**Documentation**: See [AJAX Subform Pattern](docs/AJAX_SUBFORM_PATTERN.md) for complete guide with examples.

**Working example**: `sample-forms/05_ajax-subform/`

### Cascading Dropdown Pattern

**Description**: Parent-child dropdown filtering where child options depend on parent selection.

**Components**:
- Parent `SelectBox`
- Child `SelectBox` with `groupingColumn` and `controlField`

**Key configuration**:
```yaml
# Parent dropdown
- id: category
  type: selectBox
  optionsSource:
    type: form
    formId: mdCategory
    idColumn: code
    labelColumn: name

# Child dropdown (cascading)
- id: product
  type: selectBox
  optionsSource:
    type: form
    formId: mdProduct
    idColumn: code
    labelColumn: name
    groupingColumn: categoryCode  # Field in child form referencing parent
    useAjax: true
  controlField: category          # Parent field in current form
```

**Documentation**: See [Nested LOV Guide](sample-forms/01_nested_lovs/JOGET_NESTED_LOV_GUIDE.md)

**Working example**: `sample-forms/01_nested_lovs/`

### Multi-Page Wizard Pattern

**Description**: Complex multi-step forms with tab navigation and per-page validation.

**Components**:
- Main form with `MultiPagedForm` element
- Multiple sub-forms (one per page/tab)

**Working example**: `sample-forms/04_farmer-application-form/`
- 7-page farmer registration wizard
- Demonstrates FormGrid, various validators, MDM lookups

## Version

**Version:** 0.2.0 (Enterprise Features Update)
**Last Updated:** 2025-12-19
