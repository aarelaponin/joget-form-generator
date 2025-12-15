# YAML Specification Reference

This document describes the YAML specification format for generating Joget DX forms using the `joget-form-generator` tool.

## Table of Contents

- [Overview](#overview)
- [Form Metadata](#form-metadata)
- [Field Types](#field-types)
  - [Standard Fields](#standard-fields)
  - [Advanced Fields](#advanced-fields)
  - [Enterprise Fields](#enterprise-fields)
- [Options Sources](#options-sources)
- [Validation Rules](#validation-rules)
- [Grid Columns](#grid-columns)
- [Multi-Page Forms](#multi-page-forms)
- [Complete Examples](#complete-examples)

---

## Overview

A YAML specification file has two required top-level sections:

```yaml
form:     # Form metadata (required)
  id: myForm
  name: My Form

fields:   # Array of field definitions (required, min 1)
  - id: field1
    label: Field 1
    type: textField
```

### Validation

Validate your specification before generating:

```bash
joget-form-gen validate my_form.yaml
```

### Generation

Generate Joget JSON from your specification:

```bash
joget-form-gen generate my_form.yaml -o output/
```

---

## Form Metadata

The `form:` section defines the form's identity and metadata.

| Property | Type | Required | Constraints | Description |
|----------|------|----------|-------------|-------------|
| `id` | string | **Yes** | Pattern: `^[a-zA-Z][a-zA-Z0-9_]{0,19}$`, Max: 20 chars | Form ID (must match tableName) |
| `name` | string | **Yes** | Min: 1, Max: 255 chars | Human-readable form name |
| `tableName` | string | No | Pattern: `^[a-zA-Z][a-zA-Z0-9_]{0,19}$`, Max: 20 chars | Database table name (defaults to id) |
| `description` | string | No | - | Optional form description |

**Example:**

```yaml
form:
  id: employeeForm
  name: Employee Registration Form
  tableName: employeeForm
  description: Form for registering new employees
```

**Important Notes:**
- `id` and `tableName` should be identical for proper database table creation
- `id` must start with a letter and contain only letters, numbers, and underscores
- Maximum 20 characters for `id` and `tableName`

---

## Field Types

All fields share these common properties:

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `id` | string | **Yes** | - | Field ID (database column name) |
| `label` | string | **Yes** | - | Field label shown in UI |
| `type` | string | **Yes** | - | Field type (see sections below) |
| `required` | boolean | No | `false` | Whether field is mandatory |
| `readonly` | boolean | No | `false` | Whether field is read-only |
| `defaultValue` | string | No | - | Default value for field |
| `size` | string | No | `medium` | Field size: `small`, `medium`, `large` |
| `validation` | object | No | - | Validation rules (see [Validation Rules](#validation-rules)) |

**ID Pattern:** `^[a-zA-Z][a-zA-Z0-9_]*$` (start with letter, max 50 chars)

---

### Standard Fields

#### hiddenField

Hidden field that stores data without displaying to users.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `defaultValue` | string | - | Value to store |

```yaml
- id: formStatus
  label: Status
  type: hiddenField
  defaultValue: "draft"
```

---

#### textField

Single-line text input.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `placeholder` | string | - | Placeholder text |
| `maxlength` | integer | - | Maximum character length |
| `size` | string | `medium` | `small`, `medium`, `large` |

```yaml
- id: firstName
  label: First Name
  type: textField
  required: true
  placeholder: Enter your first name
  maxlength: 100
```

---

#### passwordField

Masked password input.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `placeholder` | string | - | Placeholder text |
| `maxlength` | integer | - | Maximum character length |

```yaml
- id: password
  label: Password
  type: passwordField
  required: true
  placeholder: Enter password
```

---

#### textArea

Multi-line text input.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `placeholder` | string | - | Placeholder text |
| `rows` | integer | - | Number of visible rows (1-50) |
| `cols` | integer | - | Number of visible columns (1-200) |
| `maxlength` | integer | - | Maximum character length |

```yaml
- id: description
  label: Description
  type: textArea
  rows: 5
  cols: 50
  placeholder: Enter detailed description
```

---

#### selectBox

Dropdown selection field.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `options` | array | - | Static options (see [Static Options](#static-options)) |
| `optionsSource` | object | - | Dynamic options (see [Options Sources](#options-sources)) |
| `multiple` | boolean | `false` | Allow multiple selections |

**Requirement:** Must have either `options` OR `optionsSource`.

```yaml
# Static options
- id: department
  label: Department
  type: selectBox
  required: true
  options:
    - value: "HR"
      label: Human Resources
    - value: "IT"
      label: Information Technology
    - value: "FIN"
      label: Finance

# Dynamic options from another form
- id: manager
  label: Manager
  type: selectBox
  optionsSource:
    type: formData
    formId: employeeForm
    valueColumn: id
    labelColumn: fullName
    addEmptyOption: true
```

---

#### checkBox

Multiple-choice checkbox field.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `options` | array | - | Static options |
| `optionsSource` | object | - | Dynamic options |
| `multiple` | boolean | `false` | Store multiple values |

**Requirement:** Must have either `options` OR `optionsSource`.

```yaml
- id: skills
  label: Skills
  type: checkBox
  options:
    - value: "java"
      label: Java
    - value: "python"
      label: Python
    - value: "javascript"
      label: JavaScript
```

---

#### radio

Single-choice radio button field.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `options` | array | - | Static options |
| `optionsSource` | object | - | Dynamic options |

**Requirement:** Must have either `options` OR `optionsSource`.

```yaml
- id: gender
  label: Gender
  type: radio
  required: true
  options:
    - value: "M"
      label: Male
    - value: "F"
      label: Female
    - value: "O"
      label: Other
```

---

#### datePicker

Date selection field.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `dateFormat` | string | `yyyy-MM-dd` | Date format pattern |

**Common Format Patterns:**
- `yyyy-MM-dd` - 2024-01-15
- `dd/MM/yyyy` - 15/01/2024
- `MM/dd/yyyy` - 01/15/2024
- `yyyy-MM-dd HH:mm` - 2024-01-15 14:30

```yaml
- id: birthDate
  label: Date of Birth
  type: datePicker
  required: true
  dateFormat: yyyy-MM-dd
```

---

#### fileUpload

File upload field.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `maxSize` | integer | - | Maximum file size in MB |
| `fileTypes` | string | - | Allowed extensions (comma-separated) |

```yaml
- id: resume
  label: Resume
  type: fileUpload
  maxSize: 10
  fileTypes: "pdf,doc,docx"
```

---

### Advanced Fields

#### customHTML

Custom HTML content (display only, not stored).

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `html` | string | - | HTML content to display |

```yaml
- id: instructions
  label: Instructions
  type: customHTML
  html: |
    <div class="alert alert-info">
      <h4>Please Note:</h4>
      <p>Fill in all required fields marked with *</p>
    </div>
```

---

#### idGenerator

Auto-generated ID field.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `prefix` | string | - | ID prefix |
| `postfix` | string | - | ID postfix |
| `format` | string | - | Format pattern, e.g., `{prefix}{count:05d}{postfix}` |

```yaml
- id: ticketId
  label: Ticket ID
  type: idGenerator
  prefix: "TKT-"
  format: "{prefix}{count:05d}"
```

---

#### grid

Simple tabular data entry (non-form-based).

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `columns` | array | - | Column definitions (see [Grid Columns](#grid-columns)) |
| `readonly` | boolean | `false` | Read-only grid |
| `validateMinRow` | integer | - | Minimum number of rows |
| `validateMaxRow` | integer | - | Maximum number of rows |
| `errorMessage` | string | - | Error message for row validation |

```yaml
- id: phoneNumbers
  label: Phone Numbers
  type: grid
  columns:
    - id: phoneType
      label: Type
      type: selectBox
      options:
        - value: "mobile"
          label: Mobile
        - value: "home"
          label: Home
        - value: "work"
          label: Work
    - id: number
      label: Number
      type: textField
  validateMinRow: 1
  validateMaxRow: 5
```

---

#### calculationField

Field that calculates values from other fields.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `equation` | string | - | Calculation formula |
| `storeNumeric` | boolean | `true` | Store result as numeric |

```yaml
- id: totalPrice
  label: Total Price
  type: calculationField
  equation: "{quantity} * {unitPrice}"
  storeNumeric: true
```

---

### Enterprise Fields

#### richTextEditor

Rich text editing with formatting options.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `editor` | string | `tinymce` | Editor type: `tinymce`, `quill` |

```yaml
- id: content
  label: Content
  type: richTextEditor
  editor: tinymce
```

---

#### subform

Embedded reference to another form.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `formId` | string | - | Referenced form ID |
| `readonly` | boolean | `false` | Read-only subform |

```yaml
- id: addressSection
  label: Address
  type: subform
  formId: addressForm
```

---

#### formGrid

Grid with embedded form fields per row.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `formId` | string | - | Form ID to use for each row |
| `columns` | array | - | Column definitions |
| `allowAddRow` | boolean | `true` | Allow adding rows |
| `allowDeleteRow` | boolean | `true` | Allow deleting rows |
| `validateMinRow` | integer | - | Minimum rows |
| `validateMaxRow` | integer | - | Maximum rows |

```yaml
- id: orderItems
  label: Order Items
  type: formGrid
  formId: orderItemForm
  allowAddRow: true
  allowDeleteRow: true
  validateMinRow: 1
```

---

#### multiPagedForm

Multi-step wizard form.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `pages` | array | - | Page definitions (see [Multi-Page Forms](#multi-page-forms)) |
| `showNavigation` | boolean | `true` | Show page navigation |
| `showProgressBar` | boolean | `true` | Show progress bar |

```yaml
- id: registrationWizard
  label: Registration
  type: multiPagedForm
  showNavigation: true
  showProgressBar: true
  pages:
    - formId: personalInfoForm
      label: Personal Info
    - formId: contactInfoForm
      label: Contact Details
    - formId: preferencesForm
      label: Preferences
```

---

## Options Sources

For fields that support options (`selectBox`, `checkBox`, `radio`), you can use static options or dynamic sources.

### Static Options

```yaml
options:
  - value: "stored_value"
    label: "Display Label"
```

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `value` | string | **Yes** | Value stored in database |
| `label` | string | **Yes** | Label displayed to user |

---

### Dynamic Options

Use `optionsSource` for dynamic data loading.

#### formData Type

Load options from another Joget form's data.

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `type` | string | **Yes** | - | Must be `formData` |
| `formId` | string | **Yes** | - | Source form ID |
| `valueColumn` | string | No | `id` | Column for option value |
| `labelColumn` | string | No | `name` | Column for option label |
| `groupingColumn` | string | No | - | Column for grouping options |
| `addEmptyOption` | boolean | No | `true` | Add empty first option |
| `emptyLabel` | string | No | `""` | Label for empty option |
| `useAjax` | boolean | No | `false` | Load via AJAX |
| `parentField` | string | No | - | Parent field for cascading |
| `filterField` | string | No | - | Filter column for cascading |

**Basic Example:**

```yaml
optionsSource:
  type: formData
  formId: departmentList
  valueColumn: code
  labelColumn: name
  addEmptyOption: true
```

**Cascading Dropdown Example:**

```yaml
# Parent dropdown
- id: country
  label: Country
  type: selectBox
  optionsSource:
    type: formData
    formId: countryList
    valueColumn: code
    labelColumn: name

# Child dropdown (depends on parent)
- id: city
  label: City
  type: selectBox
  optionsSource:
    type: formData
    formId: cityList
    valueColumn: code
    labelColumn: name
    parentField: country
    filterField: countryCode
    useAjax: true
```

---

#### api Type

Load options from external REST API.

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `type` | string | **Yes** | - | Must be `api` |
| `jsonUrl` | string | **Yes** | - | API endpoint URL |
| `idColumn` | string | **Yes** | - | JSON field for value |
| `labelColumn` | string | **Yes** | - | JSON field for label |
| `requestType` | string | No | `GET` | HTTP method: `GET`, `POST`, `PUT`, `DELETE` |
| `postMethod` | string | No | `parameters` | Body format: `parameters`, `jsonPayload`, `custom` |
| `params` | array | No | - | Request parameters |
| `headers` | array | No | - | HTTP headers |
| `customPayload` | string | No | - | Custom JSON payload |
| `multirowBaseObject` | string | No | - | JSON path for array extraction |
| `addEmptyOption` | boolean | No | `true` | Add empty first option |

**Example:**

```yaml
optionsSource:
  type: api
  jsonUrl: "https://api.example.com/countries"
  idColumn: countryCode
  labelColumn: countryName
  requestType: GET
  headers:
    - name: Authorization
      value: "Bearer {token}"
  multirowBaseObject: "data.countries"
  addEmptyOption: true
```

---

#### database Type

Load options directly from database.

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `type` | string | **Yes** | - | Must be `database` |
| `tableName` | string | **Yes** | - | Database table name |
| `valueColumn` | string | **Yes** | - | Column for value |
| `labelColumn` | string | **Yes** | - | Column for label |
| `jdbcDatasource` | string | No | `default` | JDBC datasource name |
| `extraCondition` | string | No | - | SQL WHERE condition |
| `groupingColumn` | string | No | - | Column for grouping |
| `addEmpty` | boolean | No | `true` | Add empty first option |

**Example:**

```yaml
optionsSource:
  type: database
  tableName: app_fd_products
  valueColumn: c_productId
  labelColumn: c_productName
  jdbcDatasource: default
  extraCondition: "c_active = 'true'"
  addEmpty: true
```

---

## Validation Rules

Add validation to any field using the `validation` property.

| Property | Type | Description |
|----------|------|-------------|
| `pattern` | string | Regex pattern for validation |
| `minLength` | integer | Minimum character length |
| `maxLength` | integer | Maximum character length |
| `message` | string | Custom error message |

**Examples:**

```yaml
# Email validation
- id: email
  label: Email
  type: textField
  required: true
  validation:
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    message: Please enter a valid email address

# Phone number validation
- id: phone
  label: Phone
  type: textField
  validation:
    pattern: "^\\+?[0-9]{10,15}$"
    minLength: 10
    maxLength: 15
    message: Please enter a valid phone number

# Length validation only
- id: username
  label: Username
  type: textField
  required: true
  validation:
    minLength: 3
    maxLength: 20
    message: Username must be 3-20 characters
```

---

## Grid Columns

Grid and formGrid fields use column definitions.

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `id` | string | **Yes** | - | Column ID |
| `label` | string | **Yes** | - | Column header label |
| `type` | string | **Yes** | - | Field type: `textField`, `selectBox`, `datePicker`, `checkBox` |
| `options` | array | No | - | Options for selectBox type |
| `editable` | boolean | No | `true` | Whether column is editable |

**Example:**

```yaml
columns:
  - id: itemName
    label: Item Name
    type: textField
    editable: true

  - id: quantity
    label: Qty
    type: textField

  - id: category
    label: Category
    type: selectBox
    options:
      - value: "A"
        label: Category A
      - value: "B"
        label: Category B

  - id: dueDate
    label: Due Date
    type: datePicker
```

---

## Multi-Page Forms

For `multiPagedForm` type, define pages array.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `formId` | string | **Yes** | Referenced form ID for this page |
| `label` | string | No | Page label/title |
| `description` | string | No | Page description |

**Example:**

```yaml
- id: onboardingWizard
  label: Employee Onboarding
  type: multiPagedForm
  showNavigation: true
  showProgressBar: true
  pages:
    - formId: personalInfoForm
      label: Personal Information
      description: Basic personal details

    - formId: employmentForm
      label: Employment Details
      description: Job and department info

    - formId: documentsForm
      label: Documents
      description: Upload required documents
```

---

## Complete Examples

### Basic Form

```yaml
form:
  id: contactForm
  name: Contact Form
  tableName: contactForm

fields:
  - id: firstName
    label: First Name
    type: textField
    required: true
    placeholder: Enter first name

  - id: lastName
    label: Last Name
    type: textField
    required: true

  - id: email
    label: Email
    type: textField
    required: true
    validation:
      pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      message: Invalid email format

  - id: phone
    label: Phone
    type: textField
    placeholder: "+1234567890"

  - id: subject
    label: Subject
    type: selectBox
    required: true
    options:
      - value: "inquiry"
        label: General Inquiry
      - value: "support"
        label: Technical Support
      - value: "sales"
        label: Sales

  - id: message
    label: Message
    type: textArea
    required: true
    rows: 5
```

### Form with Dynamic Options

```yaml
form:
  id: orderForm
  name: Order Form
  tableName: orderForm

fields:
  - id: orderId
    label: Order ID
    type: idGenerator
    prefix: "ORD-"
    format: "{prefix}{count:06d}"

  - id: customer
    label: Customer
    type: selectBox
    required: true
    optionsSource:
      type: formData
      formId: customerList
      valueColumn: id
      labelColumn: companyName
      addEmptyOption: true

  - id: product
    label: Product
    type: selectBox
    required: true
    optionsSource:
      type: api
      jsonUrl: "https://api.example.com/products"
      idColumn: productId
      labelColumn: productName

  - id: quantity
    label: Quantity
    type: textField
    required: true

  - id: unitPrice
    label: Unit Price
    type: textField
    readonly: true

  - id: totalAmount
    label: Total Amount
    type: calculationField
    equation: "{quantity} * {unitPrice}"
    storeNumeric: true

  - id: notes
    label: Notes
    type: richTextEditor
    editor: tinymce
```

### MDM-Style Form (Cascading Dropdowns)

```yaml
form:
  id: equipmentForm
  name: Equipment Registration
  tableName: equipmentForm

fields:
  - id: equipmentCode
    label: Equipment Code
    type: textField
    required: true

  - id: equipmentName
    label: Equipment Name
    type: textField
    required: true

  - id: category
    label: Category
    type: selectBox
    required: true
    optionsSource:
      type: formData
      formId: equipmentCategory
      valueColumn: code
      labelColumn: name
      addEmptyOption: true

  - id: subCategory
    label: Sub-Category
    type: selectBox
    optionsSource:
      type: formData
      formId: equipmentSubCategory
      valueColumn: code
      labelColumn: name
      parentField: category
      filterField: categoryCode
      useAjax: true
      addEmptyOption: true

  - id: isActive
    label: Active
    type: radio
    required: true
    defaultValue: "Y"
    options:
      - value: "Y"
        label: Yes
      - value: "N"
        label: No
```

---

## Quick Reference

### Field Type Summary

| Type | Category | Stores Data | Options Support |
|------|----------|-------------|-----------------|
| `hiddenField` | Standard | Yes | No |
| `textField` | Standard | Yes | No |
| `passwordField` | Standard | Yes | No |
| `textArea` | Standard | Yes | No |
| `selectBox` | Standard | Yes | **Yes** |
| `checkBox` | Standard | Yes | **Yes** |
| `radio` | Standard | Yes | **Yes** |
| `datePicker` | Standard | Yes | No |
| `fileUpload` | Standard | Yes | No |
| `customHTML` | Advanced | No | No |
| `idGenerator` | Advanced | Yes | No |
| `grid` | Advanced | Yes | No |
| `calculationField` | Advanced | Yes | No |
| `richTextEditor` | Enterprise | Yes | No |
| `subform` | Enterprise | No (Reference) | No |
| `formGrid` | Enterprise | Yes | No |
| `multiPagedForm` | Enterprise | No (Container) | No |

### Options Source Summary

| Source Type | Use Case | Required Properties |
|-------------|----------|---------------------|
| Static `options` | Small, fixed lists | `value`, `label` |
| `formData` | Data from Joget forms | `formId` |
| `api` | External REST APIs | `jsonUrl`, `idColumn`, `labelColumn` |
| `database` | Direct database queries | `tableName`, `valueColumn`, `labelColumn` |
