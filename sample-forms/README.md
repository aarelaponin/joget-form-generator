# Sample Forms Reference

This folder contains tested, working Joget DX8 form definitions that serve as reference examples for the form generator. These are production-quality JSON exports that demonstrate correct syntax and patterns.

## Purpose

These sample forms serve multiple purposes:

1. **Syntax Reference** - Demonstrate correct Joget JSON structure for various field types
2. **Pattern Examples** - Show how to implement common patterns (cascading dropdowns, AJAX subforms, etc.)
3. **Validation Source** - Used to verify form generator output matches expected Joget format
4. **Learning Resource** - Help understand Joget form architecture

## Folder Structure

```
sample-forms/
├── 01_nested_lovs/           # Cascading (nested) dropdown pattern
├── 02_master_details/        # Master-detail form relationships
├── 03_tabs/                  # Tab-based form layout
├── 04_farmer-application-form/  # Complex multi-tab wizard form
└── 05_ajax-subform/          # AJAX Subform lookup pattern
```

## Example Categories

### 01_nested_lovs - Cascading Dropdowns

Demonstrates how to create cascading (dependent) dropdowns where child options filter based on parent selection.

**Key files:**
- `JOGET_NESTED_LOV_GUIDE.md` - Comprehensive guide with step-by-step instructions
- `lov1.json` - Parent LOV form (categories)
- `lov2.json` - Child LOV form with parent reference
- `x100Test.json` - Main form using cascading LOVs

**Key patterns shown:**
- `FormOptionsBinder` with `groupingColumn` and `controlField`
- `useAjax: "true"` for dynamic filtering
- Parent-child data relationships

### 02_master_details - Master-Detail Relationships

Shows how to create master-detail form relationships using subforms.

### 03_tabs - Tab-Based Forms

Demonstrates tab layout configuration.

### 04_farmer-application-form - Complex Multi-Tab Wizard

A comprehensive real-world example showing a 7-page farmer registration wizard. This is an excellent reference for:

**Form Architecture:**
- Main form (`f01-main.json`) with `MultiPagedForm` element
- 7 sub-forms for each wizard page

**Field Types Demonstrated:**
- `TextField` with various validators (`DefaultValidator`, `DuplicateValueValidator`)
- `SelectBox` with `FormOptionsBinder` (loading from MDM tables)
- `Radio` with static options
- `DatePicker` with `yearRange` configuration
- `HiddenField` for parent ID tracking
- `CustomHTML` for instructions
- `FormGrid` with `MultirowFormBinder` for household members

**Validators Shown:**
- `DefaultValidator` with `mandatory`, `type: "email"`
- `DuplicateValueValidator` for unique field validation

**Key files:**
| File | Description |
|------|-------------|
| `f01-main.json` | Main wizard form with MultiPagedForm |
| `f01.01.json` | Basic Information (personal details) |
| `f01.02.json` | Location & Farm |
| `f01.03.json` | Agricultural Activities |
| `f01.04.json` | Household Members (FormGrid example) |
| `f01.05.json` | Crops & Livestock |
| `f01.06.json` | Income & Programs |
| `f01.07.json` | Declaration |

### 05_ajax-subform - AJAX Subform Lookup

Demonstrates the SelectBox + AjaxSubForm pattern for dynamic record lookup.

**Key files:**
- `parent-form-x2.json` - Parent form with SelectBox triggering AjaxSubForm
- `subform-x1.json` - Subform that loads based on selection

**Critical patterns shown:**
- `AjaxSubForm` with `ajax: "true"` and `parentSubFormId`
- `SelectBox` with `idColumn: ""` (MUST be empty for AjaxSubForm pattern)

**See also:** [AJAX Subform Pattern Documentation](../docs/AJAX_SUBFORM_PATTERN.md)

## Using These Examples

### As Syntax Reference

When generating JSON, compare output structure against these examples:

```python
# Example: Verify SelectBox structure matches sample
with open("sample-forms/01_nested_lovs/lov1.json") as f:
    reference = json.load(f)
    # Compare generated selectbox against reference structure
```

### As Pattern Templates

Copy and adapt JSON structures for new forms:

1. Find relevant example in appropriate folder
2. Understand the pattern from accompanying documentation
3. Adapt field IDs, labels, and configuration for your use case

### For Testing

Use these forms to validate generator output:

```bash
# Generate form and compare structure
joget-form-gen generate spec.yaml -o output/
diff output/form.json sample-forms/04_farmer-application-form/f01.01.json
```

## Key Joget JSON Conventions

These examples demonstrate important Joget conventions:

### Empty String vs Missing Property
```json
// Joget uses empty string "" for false/disabled
"readonly": "",
"multiple": "",
"useAjax": ""

// vs populated for true/enabled
"readonly": "true",
"multiple": "true",
"useAjax": "true"
```

### Validator Structure
```json
// Empty validator (no validation)
"validator": {
    "className": "",
    "properties": {}
}

// Active validator
"validator": {
    "className": "org.joget.apps.form.lib.DefaultValidator",
    "properties": {
        "mandatory": "true",
        "type": "email",
        "message": "Please enter valid email"
    }
}
```

### Options Binder Structure
```json
"optionsBinder": {
    "className": "org.joget.apps.form.lib.FormOptionsBinder",
    "properties": {
        "formDefId": "mdTable",
        "idColumn": "code",
        "labelColumn": "name",
        "groupingColumn": "",  // For cascading: parent field in source form
        "extraCondition": "",
        "addEmptyOption": "true",
        "emptyLabel": "",
        "useAjax": "true",     // For cascading: enable dynamic loading
        "cacheInterval": ""
    }
}
```

## Related Documentation

- [YAML Specification Reference](../docs/YAML_SPECIFICATION.md) - Input format for form generator
- [Nested LOV Refactoring Pattern](../docs/NESTED_LOV_REFACTORING_PATTERN.md) - Convert flat LOVs to hierarchical selections
- [AJAX Subform Pattern](../docs/AJAX_SUBFORM_PATTERN.md) - Detailed AJAX subform documentation
- [Enterprise Fields Guide](../ENTERPRISE_FIELDS.md) - Enterprise field types

---

**Version:** 0.2.0
**Last Updated:** 2025-12-22
