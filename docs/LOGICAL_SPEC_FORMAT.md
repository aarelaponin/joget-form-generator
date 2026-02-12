# Logical Specification Format for Joget Forms

This document describes the recommended format for writing logical specifications that can be processed by the Joget Form Generation sub-agent.

## Overview

The sub-agent can convert logical specifications into:
1. YAML form specifications
2. Joget JSON form definitions
3. Complete wizard packages with interconnected subforms

Provide specifications in the formats below for optimal results.

---

## Single Form Specification

Use this format for MDM (Master Data) forms or simple transactional forms.

### Template

```markdown
## Form: [formId]
**Name:** [Display Name]
**Purpose:** [Brief description of the form's purpose]
**Table:** [tableName - only if different from formId]

### Fields:
1. **fieldId** (type, required/optional) - Description
2. **fieldId** (type, required/optional) - Description
   - Additional notes or constraints

### Lookups:
- fieldId → sourceFormId (valueColumn/labelColumn)

### Validation Rules:
- fieldId: [validation description]
```

### Example: MDM Form

```markdown
## Form: md38InputCategory
**Name:** MD.38 - Input Category
**Purpose:** Categories for agricultural inputs (seeds, fertilizer, etc.)

### Fields:
1. **code** (text, required, max 30) - Unique category code
2. **name** (text, required, max 100) - Display name
3. **description** (textarea, optional) - Additional details
4. **parentCategory** (dropdown, optional) - Parent category for hierarchy
5. **sortOrder** (text, optional, default: "0") - Display ordering
6. **isActive** (radio Y/N, required, default: Y) - Soft delete flag

### Lookups:
- parentCategory → md38InputCategory (code/name)
```

### Example: Transactional Form

```markdown
## Form: equipmentRequest
**Name:** Equipment Request
**Purpose:** Submit requests for farm equipment

### Fields:
1. **requestNumber** (idGenerator, readonly) - Auto-generated ID, format: REQ-######
2. **requestDate** (date, required, default: today) - Date of request
3. **farmer** (smartSearch, required) - Farmer lookup
4. **equipmentCategory** (dropdown, required) - Equipment category
5. **equipmentType** (dropdown, required, cascading) - Specific equipment
6. **quantity** (text, required) - Number of items requested
7. **justification** (textarea, required) - Reason for request
8. **status** (dropdown, required, default: DRAFT) - Request status

### Lookups:
- equipmentCategory → md25equipCategory (code/name)
- equipmentType → md25equipment (code/name, cascading from equipmentCategory via category_code)

### Validation Rules:
- quantity: must be positive integer
- justification: minimum 20 characters
```

---

## Wizard Package Specification

Use this format for multi-tab/multi-page forms with related subforms.

### Template

```markdown
## Package: [packageId]
**Main Form:** [mainFormId]
**Purpose:** [Overall purpose of the wizard]
**Display Mode:** tab | wizard

### Tab 1: [Label] → [subformId]
- **fieldId** (type, required/optional) - Description
- **fieldId** (type, required/optional) - Description

### Tab 2: [Label] → [subformId]
- **fieldId** (type, required/optional) - Description

### Tab N: [Label] → [subformId] (FormGrid 1:N)
- **fieldId** (type) - Description
- **fieldId** (type) - Description

### Relationships:
- [Describe how forms relate to each other]

### Lookups:
- fieldId → sourceFormId (valueColumn/labelColumn)
- fieldId → sourceFormId (cascading from parentField)
```

### Example: Farmer Registration Wizard

```markdown
## Package: farmerRegistration
**Main Form:** farmerRegistrationMain
**Purpose:** Complete farmer registration with personal info, location, and land parcels
**Display Mode:** tab

### Tab 1: Basic Information → farmerBasicInfo
- **national_id** (text, required, unique) - 13-digit national ID
- **first_name** (text, required, max 50) - First name
- **last_name** (text, required, max 50) - Last name
- **other_names** (text, optional) - Middle/other names
- **gender** (radio M/F, required) - Gender
- **date_of_birth** (date, required) - Date of birth
- **marital_status** (dropdown, required) - Marital status

### Tab 2: Contact Details → farmerContact
- **phone_primary** (text, required) - Primary phone, format: +266XXXXXXXX
- **phone_secondary** (text, optional) - Secondary phone
- **email** (text, optional) - Email address with validation

### Tab 3: Residency → farmerResidency
- **district** (dropdown, required) - District
- **community_council** (dropdown, required, cascading) - Community council
- **village** (dropdown, required, cascading) - Village
- **physical_address** (textarea, optional) - Physical address description

### Tab 4: Farming Profile → farmerProfile
- **farming_experience_years** (text, optional) - Years of experience
- **primary_activity** (dropdown, required) - Main farming activity
- **farm_size_hectares** (text, optional) - Total farm size
- **is_commercial** (radio Y/N, required, default: N) - Commercial farmer flag

### Tab 5: Land Parcels → farmerParcels (FormGrid 1:N)
- **parcel_name** (text, required) - Parcel identifier
- **area_hectares** (text, required) - Area in hectares
- **land_use** (dropdown, required) - Primary land use
- **ownership_type** (dropdown, required) - Ownership type
- **geometry** (gisPolygonCapture, optional) - Parcel boundary

### Tab 6: Household Members → farmerHousehold (FormGrid 1:N)
- **member_name** (text, required) - Full name
- **relationship** (dropdown, required) - Relationship to farmer
- **date_of_birth** (date, optional) - Date of birth
- **is_dependent** (radio Y/N, required) - Financial dependent

### Relationships:
- All subforms link to main form via parent_id
- farmerParcels: 1:N relationship (multiple parcels per farmer)
- farmerHousehold: 1:N relationship (multiple members per farmer)

### Lookups:
- marital_status → md01maritalStatus (code/name)
- district → md03district (code/name)
- community_council → md04council (code/name, cascading from district via district_code)
- village → md05village (code/name, cascading from community_council via council_code)
- primary_activity → md15farmingActivity (code/name)
- land_use → md10landUse (code/name)
- ownership_type → md11ownershipType (code/name)
- relationship → md02relationship (code/name)
```

---

## Field Type Reference

Use these type hints in your specifications:

| Type Hint | Joget Field Type | Notes |
|-----------|------------------|-------|
| `text` | textField | Single-line text input |
| `textarea` | textArea | Multi-line text input |
| `password` | passwordField | Masked input |
| `dropdown` | selectBox | Single selection |
| `dropdown, multiple` | selectBox | Multiple selection |
| `radio` | radio | Radio button group |
| `checkbox` | checkBox | Checkbox group |
| `date` | datePicker | Date selection |
| `file` | fileUpload | File attachment |
| `hidden` | hiddenField | Hidden value storage |
| `idGenerator` | idGenerator | Auto-generated IDs |
| `calculation` | calculationField | Computed values |
| `richText` | richTextEditor | WYSIWYG editor |
| `html` | customHTML | Static HTML content |
| `smartSearch` | smartSearch | Fuzzy search (GovStack) |
| `gisPolygonCapture` | gisPolygonCapture | GPS polygon (GovStack) |
| `concat` | concatField | Field concatenation (GovStack) |

---

## Modifier Keywords

Add these keywords to field definitions:

| Keyword | Meaning | Example |
|---------|---------|---------|
| `required` | Field is mandatory | `(text, required)` |
| `optional` | Field is not mandatory | `(text, optional)` |
| `unique` | Value must be unique | `(text, required, unique)` |
| `readonly` | Field is read-only | `(text, readonly)` |
| `cascading` | Filtered by parent dropdown | `(dropdown, required, cascading)` |
| `default: X` | Default value | `(radio Y/N, default: Y)` |
| `max N` | Maximum length | `(text, required, max 50)` |
| `min N` | Minimum length | `(text, required, min 10)` |
| `format: X` | Format pattern | `(text, format: +266XXXXXXXX)` |

---

## Relationship Types

### 1:1 Subform (Wizard Pages)
Each tab in a wizard stores data in its own table, linked by `parent_id`.

```markdown
### Tab 1: Basic Info → basicInfoForm
### Tab 2: Contact → contactForm
```

### 1:N FormGrid (Repeating Records)
Multiple child records per parent, displayed as editable grid.

```markdown
### Tab 5: Parcels → parcelsForm (FormGrid 1:N)
```

### Cascading Dropdowns
Child dropdown filtered by parent selection.

```markdown
### Lookups:
- district → md03district (code/name)
- village → md05village (code/name, cascading from district via district_code)
```

---

## Best Practices

1. **Use MDM for all lookups** - Never hardcode dropdown options
2. **Follow naming conventions**:
   - MDM forms: `mdXX<EntityName>` (e.g., `md25equipment`)
   - Transactional forms: descriptive camelCase (e.g., `farmerRegistration`)
3. **Always include code/name** as first two fields in MDM forms
4. **Include isActive** field for soft delete pattern
5. **Specify cascading relationships** clearly with parent field reference
6. **Mark FormGrid relationships** explicitly as `(FormGrid 1:N)`
7. **Include validation hints** for complex rules

---

## Processing the Specification

Once you provide a logical specification in this format, the sub-agent will:

1. Parse the specification to understand structure and relationships
2. Generate YAML form specifications using the appropriate field types
3. Apply correct Joget patterns (validators, binders, options sources)
4. Create interconnected forms for wizard packages
5. Output production-ready Joget JSON

You can then import the generated JSON into Joget DX via the Form Builder or FormCreator API.
