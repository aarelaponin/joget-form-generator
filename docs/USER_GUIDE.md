# Joget Form Generator - User Guide

**Version:** 1.0.0
**Last Updated:** 2025-01-10

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [YAML Specification Reference](#yaml-specification-reference)
5. [Field Types Reference](#field-types-reference)
6. [Options and Data Binding](#options-and-data-binding)
7. [Validation](#validation)
8. [CLI Usage](#cli-usage)
9. [Examples](#examples)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

The **Joget Form Generator** is a command-line tool that transforms human-readable YAML specifications into production-ready Joget DX form JSON definitions. It provides:

- **Schema-driven validation** using JSON Schema 2020-12
- **Pattern library** for consistent form generation
- **Auto-completion support** in VS Code and compatible IDEs
- **CLI with progress reporting** and detailed error messages
- **100% backward compatibility** with existing Joget forms

### Key Benefits

- **No manual JSON editing** - write forms in clean, readable YAML
- **Catch errors early** - validation before deployment
- **Reusable patterns** - consistent field configurations
- **Team collaboration** - version control friendly YAML specs

### Supported Field Types

**Phase 1 (Core Fields):**
1. Hidden Field
2. Text Field
3. Password Field
4. Text Area
5. Select Box (with cascading dropdown support)
6. Check Box
7. Radio Button
8. Date Picker
9. File Upload

**Phase 2 (Advanced Fields):**
10. Custom HTML
11. ID Generator
12. Subform (master-detail)
13. Grid (tabular data)

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Joget DX Enterprise Edition (for deployment)

### Install from Source

```bash
# Clone the repository
cd /path/to/joget-form-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Verify installation
joget-form-gen --version
```

### Install from PyPI (Future)

```bash
pip install joget-form-generator
```

---

## Quick Start

### 1. Create a Simple Form Specification

Create a file `my_form.yaml`:

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
    size: medium

  - id: lastName
    label: Last Name
    type: textField
    required: true
    placeholder: Enter last name
    size: medium

  - id: email
    label: Email Address
    type: textField
    required: true
    placeholder: email@example.com
    validation:
      pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      message: Please enter a valid email address

  - id: dateOfBirth
    label: Date of Birth
    type: datePicker
    dateFormat: yyyy-MM-dd

  - id: notes
    label: Additional Notes
    type: textArea
    rows: 5
    cols: 50
```

### 2. Generate the Form

```bash
joget-form-gen generate my_form.yaml -o output/
```

### 3. Deploy to Joget

The generated JSON file will be in `output/customerInfo.json`. You can:

- **Manual**: Upload via Joget Form Builder UI
- **Automated**: Use the FormCreator API (see gam_utilities/joget_utility)

---

## YAML Specification Reference

### Top-Level Structure

```yaml
form:           # Form metadata (required)
  id: string
  name: string
  tableName: string    # Optional, defaults to id
  description: string  # Optional, defaults to empty

fields:         # Array of field definitions (required, min 1)
  - id: string
    label: string
    type: string
    # ... field-specific properties
```

### Form Metadata

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | Yes | Form ID (max 20 chars, pattern: `^[a-zA-Z][a-zA-Z0-9_]{0,19}$`) |
| `name` | string | Yes | Human-readable form name displayed in Joget |
| `tableName` | string | No | Database table name (defaults to `id`, must match) |
| `description` | string | No | Optional form description (defaults to empty) |

**Important:**
- `id` and `tableName` must match (if provided)
- Both are limited to 20 characters
- This is a Joget DX requirement for database table creation

### Field Common Properties

These properties are available for ALL field types:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `id` | string | **Required** | Field ID (database column name) |
| `label` | string | **Required** | Field label shown in UI |
| `type` | enum | **Required** | Field type (see Field Types Reference) |
| `required` | boolean | `false` | Whether field is mandatory |
| `readonly` | boolean | `false` | Whether field is read-only |
| `defaultValue` | string | - | Default value for field |
| `placeholder` | string | - | Placeholder text (textField, textArea, passwordField) |
| `size` | enum | `medium` | Field size: `small`, `medium`, `large` |

### Field Type-Specific Properties

See [Field Types Reference](#field-types-reference) for detailed properties.

---

## Field Types Reference

### 1. Hidden Field

Stores data without displaying it to the user.

```yaml
- id: recordId
  label: Record ID
  type: hiddenField
  defaultValue: "12345"
```

**Properties:**
- `defaultValue` - Hidden value to store

---

### 2. Text Field

Single-line text input.

```yaml
- id: username
  label: Username
  type: textField
  required: true
  placeholder: Enter username
  size: medium
  validation:
    pattern: "^[a-zA-Z0-9_]{3,20}$"
    message: Username must be 3-20 alphanumeric characters
    minLength: 3
    maxLength: 20
```

**Properties:**
- `placeholder` - Placeholder text
- `size` - Field width: `small`, `medium`, `large`
- `maxLength` - Maximum character length
- `validation` - Validation rules (see Validation section)

---

### 3. Password Field

Masked text input for passwords.

```yaml
- id: password
  label: Password
  type: passwordField
  required: true
  placeholder: Enter password
  validation:
    minLength: 8
    message: Password must be at least 8 characters
```

**Properties:**
- Same as Text Field
- Input is automatically masked

---

### 4. Text Area

Multi-line text input.

```yaml
- id: description
  label: Description
  type: textArea
  rows: 5
  cols: 50
  placeholder: Enter detailed description
  validation:
    maxLength: 500
```

**Properties:**
- `rows` - Number of rows (default: 5)
- `cols` - Number of columns (default: 50)
- `placeholder` - Placeholder text
- `maxLength` - Maximum character length

---

### 5. Select Box

Dropdown selection with static or dynamic options.

#### Static Options

```yaml
- id: status
  label: Status
  type: selectBox
  required: true
  options:
    - value: active
      label: Active
    - value: inactive
      label: Inactive
    - value: pending
      label: Pending
```

#### Dynamic Options (Nested LOV)

```yaml
- id: category
  label: Category
  type: selectBox
  required: true
  optionsSource:
    type: formData
    formId: categories        # Parent form ID
    valueColumn: code          # Value field (default: code)
    labelColumn: name          # Label field (default: name)
    addEmptyOption: "true"
    useAjax: "false"
```

#### Multi-Select

```yaml
- id: skills
  label: Skills
  type: selectBox
  multiple: true
  options:
    - value: python
      label: Python
    - value: java
      label: Java
```

**Properties:**
- `options` - Array of static options (value/label pairs)
- `optionsSource` - Dynamic options configuration
- `multiple` - Enable multi-select (boolean)
- `size` - Visible items in dropdown (default: 10)

**Options Source Types:**
- `formData` - Load from another Joget form
- `api` - Load from REST API (Phase 2)
- `database` - Load from SQL query (Phase 2)

---

### 6. Check Box

Multiple selection checkboxes.

```yaml
- id: interests
  label: Interests
  type: checkBox
  options:
    - value: sports
      label: Sports
    - value: music
      label: Music
    - value: reading
      label: Reading
```

**Properties:**
- `options` - Array of checkbox options (**required**)

---

### 7. Radio Button

Single selection radio buttons.

```yaml
- id: gender
  label: Gender
  type: radio
  required: true
  options:
    - value: male
      label: Male
    - value: female
      label: Female
    - value: other
      label: Other
```

**Properties:**
- `options` - Array of radio options (**required**)

---

### 8. Date Picker

Date selection with calendar widget.

```yaml
- id: birthDate
  label: Date of Birth
  type: datePicker
  required: true
  dateFormat: yyyy-MM-dd
  defaultValue: "2000-01-01"
```

**Properties:**
- `dateFormat` - Date format pattern (default: `yyyy-MM-dd`)
  - Examples: `dd/MM/yyyy`, `MM-dd-yyyy`, `yyyy-MM-dd`

---

### 9. File Upload

File upload with validation.

```yaml
- id: resume
  label: Resume/CV
  type: fileUpload
  required: true
  maxSize: 5              # Max size in MB
  fileTypes: "*.pdf,*.doc,*.docx"
```

**Properties:**
- `maxSize` - Maximum file size in megabytes (default: 10)
- `fileTypes` - Allowed file types (default: `*` for all)
  - Examples: `*.pdf`, `*.jpg,*.png`, `image/*`

---

### 10. Custom HTML (Phase 2)

Display custom HTML content in forms.

```yaml
- id: welcomeBanner
  label: Welcome Banner
  type: customHTML
  html: |
    <div class="alert alert-info">
      <h3>Welcome to the Application</h3>
      <p>Please complete all sections carefully.</p>
    </div>
```

**Properties:**
- `html` - HTML content to display (supports inline styles and JavaScript)
- `label` - Optional label (can be omitted for display-only content)

**Use Cases:**
- Informational banners and notices
- Section headers with custom styling
- Help text with formatting
- Dynamic content with JavaScript

---

### 11. ID Generator (Phase 2)

Auto-generates unique IDs for records.

```yaml
- id: invoiceNumber
  label: Invoice Number
  type: idGenerator
  prefix: "INV-"
  postfix: "-2025"
  format: "{prefix}{count:08d}{postfix}"
  defaultValue: ""
```

**Properties:**
- `prefix` - ID prefix (optional, e.g., "INV-")
- `postfix` - ID postfix (optional, e.g., "-2025")
- `format` - Format pattern (optional, default: `{prefix}{count:05d}{postfix}`)
  - `{prefix}` - Inserts the prefix
  - `{count:08d}` - Inserts counter with zero-padding (8 digits)
  - `{postfix}` - Inserts the postfix
- `defaultValue` - Initial value (usually empty string)

**Format Examples:**
- `{prefix}{count:05d}{postfix}` → INV-00001-2025
- `{prefix}-{count:08d}` → CUST-00000001
- `APP-###-??????` → APP-123-456789

**Note:** Field is automatically read-only.

---

### 12. Subform (Phase 2)

Embeds another form for master-detail relationships.

```yaml
- id: equipmentRequests
  label: Equipment Requests
  type: subform
  formId: equipmentRequestsGrid  # Referenced form ID
  required: true
  addButtonLabel: "Add Equipment"
  deleteButtonLabel: "Remove"
  readonly: false
  noAddButton: false
  noDeleteButton: false
```

**Properties:**
- `formId` - Referenced form definition ID (required)
- `addButtonLabel` - Label for add button (default: "Add")
- `deleteButtonLabel` - Label for delete button (default: "Delete")
- `noAddButton` - Hide add button (default: false)
- `noDeleteButton` - Hide delete button (default: false)
- `readonly` - Make subform read-only (default: false)
- `readonlyLabel` - Make label read-only (default: false)
- `workflowVariable` - Bind to workflow variable (optional)

**Use Cases:**
- Order line items
- Multiple contacts for a customer
- Equipment requests in application
- Document uploads with metadata

**Example: Equipment Requests**
```yaml
# Parent form field
- id: equipmentList
  label: Requested Equipment
  type: subform
  formId: equipmentItemForm
  required: true
  addButtonLabel: "Add Item"

# equipmentItemForm would contain fields like:
# - equipmentCategory (selectBox)
# - equipmentType (selectBox)
# - quantity (textField)
# - justification (textArea)
```

---

### 13. Grid (Phase 2)

Simple tabular data entry with defined columns.

```yaml
- id: productGrid
  label: Product List
  type: grid
  columns:
    - id: productCode
      label: Product Code
    - id: productName
      label: Product Name
    - id: quantity
      label: Quantity
    - id: unitPrice
      label: Unit Price
  validateMinRow: 1
  validateMaxRow: 50
  errorMessage: "Please enter between 1 and 50 products"
  readonly: false
```

**Properties:**
- `columns` - Array of column definitions (required)
  - Each column has: `id` (field ID) and `label` (column header)
- `validateMinRow` - Minimum number of rows (optional)
- `validateMaxRow` - Maximum number of rows (optional)
- `errorMessage` - Error message for row validation (optional)
- `readonly` - Make grid read-only (default: false)

**Use Cases:**
- Product listings
- Budget line items
- Simple data tables
- Cost breakdowns

**Difference from Subform:**
- Grid: Simple table with columns (no form embedding)
- Subform: Embeds entire form definition (supports complex fields)

**Example: Budget Items**
```yaml
- id: budgetItems
  label: Budget Line Items
  type: grid
  columns:
    - id: category
      label: Category
    - id: description
      label: Description
    - id: amount
      label: Amount
  validateMinRow: 1
  validateMaxRow: 100
  errorMessage: "At least one budget item required"
```

---

## Options and Data Binding

### Static Options

For SelectBox, CheckBox, and Radio fields:

```yaml
options:
  - value: code1
    label: Display Name 1
  - value: code2
    label: Display Name 2
```

### Dynamic Options (FormData Source)

Load options from another Joget form (Nested LOV pattern):

```yaml
optionsSource:
  type: formData
  formId: parentFormId           # Form to load data from
  valueColumn: code               # Column for option value (default: code)
  labelColumn: name               # Column for option label (default: name)
  addEmptyOption: "true"          # Add empty first option (default: true)
  useAjax: "false"                # Use AJAX loading (default: false)
```

**Example Use Case: Equipment Category Selection**

```yaml
# In md25equipment form
fields:
  - id: equipment_category
    label: Equipment Category
    type: selectBox
    required: true
    optionsSource:
      type: formData
      formId: md25equipCategory   # References parent category form
      valueColumn: code
      labelColumn: name
```

### API Source (Phase 2 - Not Yet Implemented)

```yaml
optionsSource:
  type: api
  url: https://api.example.com/categories
  method: GET
  valueJsonPath: $.value
  labelJsonPath: $.label
```

### Database Source (Phase 2 - Not Yet Implemented)

```yaml
optionsSource:
  type: database
  datasource: default
  sql: "SELECT code, name FROM categories WHERE active = 1"
```

---

## Validation

### Built-in Validators

The generator automatically creates Joget validators based on field configuration:

#### Required Field Validation

```yaml
- id: email
  label: Email
  type: textField
  required: true     # Generates DefaultValidator with mandatory=true
```

Generates:
```json
{
  "validator": {
    "className": "org.joget.apps.form.lib.DefaultValidator",
    "properties": {
      "mandatory": "true"
    }
  }
}
```

#### Length Validation

```yaml
- id: username
  label: Username
  type: textField
  validation:
    minLength: 3
    maxLength: 20
    message: Username must be 3-20 characters
```

Generates:
```json
{
  "validator": {
    "className": "org.joget.apps.form.lib.DefaultValidator",
    "properties": {
      "type": "custom",
      "minLength": "3",
      "maxLength": "20",
      "errorMessage": "Username must be 3-20 characters"
    }
  }
}
```

#### Regex Pattern Validation

```yaml
- id: email
  label: Email
  type: textField
  validation:
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    message: Please enter a valid email address
```

Generates:
```json
{
  "validator": {
    "className": "org.joget.apps.form.lib.RegexValidator",
    "properties": {
      "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
      "errorMessage": "Please enter a valid email address"
    }
  }
}
```

### Validation Properties

| Property | Type | Description |
|----------|------|-------------|
| `pattern` | string | Regular expression pattern |
| `message` | string | Error message to display |
| `minLength` | integer | Minimum string length |
| `maxLength` | integer | Maximum string length |

---

## CLI Usage

### Basic Commands

```bash
# Generate forms from YAML specification
joget-form-gen generate <spec_file> [OPTIONS]

# Validate specification without generating
joget-form-gen validate <spec_file>

# Show version
joget-form-gen --version
```

### Generate Command

```bash
joget-form-gen generate my_form.yaml -o output/ [OPTIONS]
```

**Options:**
- `-o, --output <dir>` - Output directory (default: current directory)
- `--validate-only` - Validate specification without generating
- `--verbose` - Show detailed progress and debug information
- `--help` - Show help message

**Examples:**

```bash
# Generate with default output
joget-form-gen generate customer_form.yaml

# Generate to specific directory
joget-form-gen generate customer_form.yaml -o generated_forms/

# Validate only (no generation)
joget-form-gen generate customer_form.yaml --validate-only

# Verbose output with detailed progress
joget-form-gen generate customer_form.yaml --verbose
```

### Validate Command

```bash
joget-form-gen validate my_form.yaml [OPTIONS]
```

**Options:**
- `--verbose` - Show detailed validation results
- `--help` - Show help message

**Output:**
- Validation errors with line numbers
- Contextual suggestions for fixes
- Warnings for potential issues

**Example Output:**

```
Validating: customer_form.yaml

✅ Validation successful!

Warnings:
  ⚠️  Field 'email' should have validation pattern for email format
  ⚠️  Consider adding placeholder text for better UX

Summary:
  Forms: 1
  Fields: 4
  Errors: 0
  Warnings: 2
```

---

## Examples

### Example 1: Simple Master Data Form

```yaml
# File: md01maritalStatus.yaml
form:
  id: md01maritalStatus
  name: MD.01 - Marital Status
  description: Master data for marital status codes

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
```

### Example 2: Form with Nested LOV (Foreign Key)

```yaml
# File: md25equipment.yaml
form:
  id: md25equipment
  name: MD.25 - Equipment
  description: Equipment master data with category reference

fields:
  - id: code
    label: Equipment Code
    type: textField
    required: true

  - id: name
    label: Equipment Name
    type: textField
    required: true

  # Nested LOV: References parent category form
  - id: equipment_category
    label: Equipment Category
    type: selectBox
    required: true
    optionsSource:
      type: formData
      formId: md25equipCategory
      valueColumn: code
      labelColumn: name
      addEmptyOption: "true"
      useAjax: "false"

  - id: estimated_cost_lsl
    label: Estimated Cost (LSL)
    type: textField
    required: false

  - id: typical_lifespan_years
    label: Typical Lifespan (Years)
    type: textField
    required: false
```

### Example 3: User Registration Form

```yaml
# File: user_registration.yaml
form:
  id: userRegistration
  name: User Registration
  description: New user registration form

fields:
  - id: username
    label: Username
    type: textField
    required: true
    placeholder: Choose a username
    validation:
      pattern: "^[a-zA-Z0-9_]{3,20}$"
      message: Username must be 3-20 alphanumeric characters
      minLength: 3
      maxLength: 20

  - id: email
    label: Email Address
    type: textField
    required: true
    placeholder: your.email@example.com
    validation:
      pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      message: Please enter a valid email address

  - id: password
    label: Password
    type: passwordField
    required: true
    placeholder: Enter secure password
    validation:
      minLength: 8
      message: Password must be at least 8 characters

  - id: confirmPassword
    label: Confirm Password
    type: passwordField
    required: true
    placeholder: Re-enter password

  - id: dateOfBirth
    label: Date of Birth
    type: datePicker
    required: true
    dateFormat: yyyy-MM-dd

  - id: gender
    label: Gender
    type: radio
    required: true
    options:
      - value: male
        label: Male
      - value: female
        label: Female
      - value: other
        label: Other

  - id: interests
    label: Interests
    type: checkBox
    options:
      - value: technology
        label: Technology
      - value: sports
        label: Sports
      - value: music
        label: Music
      - value: reading
        label: Reading

  - id: bio
    label: Bio
    type: textArea
    rows: 5
    cols: 50
    placeholder: Tell us about yourself
    validation:
      maxLength: 500

  - id: profilePhoto
    label: Profile Photo
    type: fileUpload
    maxSize: 2
    fileTypes: "*.jpg,*.png,*.gif"

  - id: termsAccepted
    label: I accept the terms and conditions
    type: checkBox
    required: true
    options:
      - value: accepted
        label: Yes, I accept
```

---

## Troubleshooting

### Common Errors

#### 1. Validation Failed: Required Property Missing

**Error:**
```
[form] 'name' is a required property
💡 Add required property: name
```

**Solution:**
Ensure all required properties are present:
```yaml
form:
  id: myForm
  name: My Form    # This was missing
```

---

#### 2. SelectBox Requires Options

**Error:**
```
[field: category] SelectBox requires either 'options' or 'optionsSource'
```

**Solution:**
Add either static options or options source:
```yaml
# Option 1: Static options
options:
  - value: opt1
    label: Option 1

# Option 2: Dynamic options
optionsSource:
  type: formData
  formId: parentForm
```

---

#### 3. Form ID Too Long

**Error:**
```
[form.id] 'veryLongFormIdentifierName' exceeds maximum length of 20
```

**Solution:**
Shorten the form ID to 20 characters or less:
```yaml
form:
  id: veryLongFormId    # Changed from veryLongFormIdentifierName (26 chars)
```

---

#### 4. ID Pattern Validation Failed

**Error:**
```
[form.id] '123form' does not match pattern '^[a-zA-Z][a-zA-Z0-9_]{0,19}$'
```

**Solution:**
Form ID must start with a letter:
```yaml
form:
  id: form123    # Changed from 123form
```

---

#### 5. ID and TableName Mismatch

**Warning:**
```
⚠️ Form 'id' and 'tableName' should match for Joget DX compatibility
```

**Solution:**
Either remove `tableName` (it will default to `id`) or ensure they match:
```yaml
form:
  id: myForm
  tableName: myForm    # Must match id
```

Or just omit tableName:
```yaml
form:
  id: myForm    # tableName will automatically be set to 'myForm'
```

---

### Getting Help

If you encounter issues not covered here:

1. **Check the JSON Schema**: The schema file provides detailed validation rules
   - Location: `src/joget_form_generator/schema/form_spec_schema.json`

2. **Run with --verbose**: Get detailed debug information
   ```bash
   joget-form-gen generate my_form.yaml --verbose
   ```

3. **Validate before generating**: Catch errors early
   ```bash
   joget-form-gen validate my_form.yaml
   ```

4. **Check examples**: Review working examples in `examples/` directory

5. **Report issues**: Submit bug reports to the project repository

---

## Next Steps

- **[API Reference](API_REFERENCE.md)** - For programmatic usage
- **[Pattern Development Guide](PATTERN_DEVELOPMENT_GUIDE.md)** - For extending with custom field types
- **[Examples](../examples/)** - More real-world examples

---

**Document Version:** 1.0.0
**Generator Version:** 1.0.0
**Last Updated:** 2025-01-10
