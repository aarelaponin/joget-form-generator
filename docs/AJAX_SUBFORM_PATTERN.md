# Ajax Subform Pattern - Form Generator Documentation

**Version:** 0.2.0
**Last Updated:** 2025-12-19
**Joget Version:** DX8 Enterprise Edition
**Status:** Production Ready

---

## Overview

The **SelectBox + AjaxSubForm** pattern enables dynamic form loading based on user selection. When a user selects a record from a dropdown, the AjaxSubForm automatically loads and displays that record's details from a referenced form.

This pattern is commonly used for:
- Master-detail views (select a customer → show customer details)
- Reference data lookup (select equipment → show specifications)
- Read-only data display from related records

> ⚠️ **Enterprise Edition Only**: AjaxSubForm is only available in Joget Professional and Enterprise editions.

---

## Pattern Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Parent Form                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  SelectBox (id: "record_selector")                       │    │
│  │  ├─ optionsBinder → FormOptionsBinder                    │    │
│  │  │   ├─ formDefId: "targetForm"                         │    │
│  │  │   ├─ idColumn: "" (EMPTY - uses primary key)         │    │
│  │  │   └─ labelColumn: "name"                             │    │
│  │  └─ value: selected record's PRIMARY KEY                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                      │
│                            │ onChange event                       │
│                            ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  AjaxSubForm (id: "detail_viewer")                       │    │
│  │  ├─ ajax: "true" (REQUIRED)                              │    │
│  │  ├─ parentSubFormId: "record_selector" (REQUIRED)        │    │
│  │  ├─ formDefId: "targetForm"                              │    │
│  │  ├─ readonly: "true" (typical for display)               │    │
│  │  └─ Loads record by PRIMARY KEY from SelectBox           │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Critical Configuration Rules

### ⚠️ UNDOCUMENTED BEHAVIORS - LEARNED FROM EXPERIENCE

These rules are **not documented** in official Joget documentation but are **critical** for the pattern to work:

| Rule | Property | Correct Value | Wrong Value | Impact |
|------|----------|---------------|-------------|--------|
| **1** | `idColumn` in SelectBox FormOptionsBinder | `""` (empty) | Any field name | AjaxSubForm lookup fails silently |
| **2** | `ajax` in AjaxSubForm | `"true"` | `""` or missing | No dynamic reload |
| **3** | `parentSubFormId` in AjaxSubForm | SelectBox field ID | Literal "subform_id" or empty | No event listener attached |
| **4** | `subFormParentId` in AjaxSubForm | `""` (empty for this pattern) | Any value | Incorrect data binding |

### Rule 1: SelectBox `idColumn` MUST Be Empty

**Why?** The AjaxSubForm uses the SelectBox value to look up records by **primary key** (`id` column). If you specify a custom `idColumn`, the SelectBox sends that field's value instead of the primary key, and the AjaxSubForm lookup fails.

```json
// ✅ CORRECT - uses record primary key
"optionsBinder": {
  "className": "org.joget.apps.form.lib.FormOptionsBinder",
  "properties": {
    "formDefId": "targetForm",
    "idColumn": "",           // ← EMPTY - critical!
    "labelColumn": "name"
  }
}

// ❌ WRONG - sends field value instead of primary key
"optionsBinder": {
  "properties": {
    "idColumn": "code"        // ← AjaxSubForm will fail!
  }
}
```

### Rule 2: AjaxSubForm `ajax` Must Be "true"

This enables the dynamic reload behavior when the parent field changes.

```json
// ✅ CORRECT
"ajax": "true"

// ❌ WRONG
"ajax": ""
"ajax": "false"
// or property missing entirely
```

### Rule 3: AjaxSubForm `parentSubFormId` Must Match SelectBox ID

This property tells the AjaxSubForm which field to "watch" for changes. It must exactly match the SelectBox's `id` property.

```json
// SelectBox has id: "equipment_selector"

// ✅ CORRECT
"parentSubFormId": "equipment_selector"

// ❌ WRONG - these are literal placeholder text, not field IDs
"parentSubFormId": "subform_id"
"parentSubFormId": "parent_field_id"
"parentSubFormId": ""
```

### Rule 4: AjaxSubForm `subFormParentId` Should Be Empty

For the "lookup by SelectBox" pattern, leave this empty. This property is only used when you need to store the parent form's ID as a foreign key in the subform's data.

```json
// ✅ CORRECT for lookup pattern
"subFormParentId": ""

// ⚠️ Only set if storing FK relationship
"subFormParentId": "parent_id_field"
```

---

## YAML Specification Format

### Pattern Definition for Form Generator

```yaml
# Pattern: ajax_subform_lookup
# Use case: Display details from a referenced form based on dropdown selection

pattern_id: ajax_subform_lookup
pattern_name: "Ajax Subform Lookup"
category: composite
edition: enterprise
description: |
  SelectBox linked to AjaxSubForm for dynamic record display.
  User selects from dropdown → AjaxSubForm loads that record.

use_cases:
  - "Display read-only details from a reference table"
  - "Master-detail view without editing capability"
  - "Dynamic form content based on user selection"

avoid_when:
  - "Need to edit the subform data (use regular Subform)"
  - "Multiple records needed (use Grid element)"
  - "Community Edition (feature not available)"

required_elements:
  - type: selectbox
    role: trigger
    constraints:
      idColumn: ""  # MUST be empty for pattern to work
  - type: ajax_subform
    role: display
    constraints:
      ajax: "true"
      parentSubFormId: "{{trigger_field_id}}"

validation_rules:
  - rule: "idColumn_must_be_empty"
    message: "SelectBox idColumn must be empty when used with AjaxSubForm"
    severity: error
  - rule: "ajax_must_be_true"
    message: "AjaxSubForm ajax property must be 'true'"
    severity: error
  - rule: "parentSubFormId_must_match"
    message: "AjaxSubForm parentSubFormId must match SelectBox id"
    severity: error
```

### Form Specification Example

```yaml
# Example: Equipment Lookup Form
form:
  id: equipment_viewer
  name: "Equipment Viewer"
  tableName: equipment_viewer

sections:
  - id: section1
    label: "Equipment Selection"
    columns:
      - width: "100%"
        fields:
          - id: equipment_selector
            type: selectbox
            label: "Select Equipment"
            optionsSource:
              type: form
              formId: md25equipment
              labelColumn: name
              # NOTE: No idColumn specified - defaults to empty (primary key)
              addEmptyOption: true
            
          - id: equipment_details
            type: ajax_subform
            label: "Equipment Details"
            formDefId: md25equipment
            ajax: true
            parentSubFormId: equipment_selector  # Links to SelectBox above
            readonly: true
            noframe: true
```

---

## Generated JSON Output

### Complete Working Example

```json
{
  "className": "org.joget.apps.form.model.Form",
  "properties": {
    "id": "equipment_viewer",
    "name": "Equipment Viewer",
    "tableName": "equipment_viewer",
    "loadBinder": {
      "className": "org.joget.apps.form.lib.WorkflowFormBinder",
      "properties": {}
    },
    "storeBinder": {
      "className": "org.joget.apps.form.lib.WorkflowFormBinder",
      "properties": {}
    }
  },
  "elements": [
    {
      "className": "org.joget.apps.form.model.Section",
      "properties": {
        "id": "section1",
        "label": "Equipment Selection"
      },
      "elements": [
        {
          "className": "org.joget.apps.form.model.Column",
          "properties": {
            "width": "100%"
          },
          "elements": [
            {
              "className": "org.joget.apps.form.lib.SelectBox",
              "properties": {
                "id": "equipment_selector",
                "label": "Select Equipment",
                "value": "",
                "readonly": "",
                "multiple": "",
                "controlField": "",
                "optionsBinder": {
                  "className": "org.joget.apps.form.lib.FormOptionsBinder",
                  "properties": {
                    "formDefId": "md25equipment",
                    "idColumn": "",
                    "labelColumn": "name",
                    "groupingColumn": "",
                    "extraCondition": "",
                    "addEmptyOption": "true",
                    "emptyLabel": "",
                    "useAjax": "",
                    "cacheInterval": ""
                  }
                },
                "options": [],
                "validator": {
                  "className": "",
                  "properties": {}
                },
                "workflowVariable": "",
                "readonlyLabel": ""
              }
            },
            {
              "className": "org.joget.plugin.enterprise.AjaxSubForm",
              "properties": {
                "id": "equipment_details",
                "label": "Equipment Details",
                "formDefId": "md25equipment",
                "ajax": "true",
                "parentSubFormId": "equipment_selector",
                "subFormParentId": "",
                "readonly": "true",
                "readonlyLabel": "",
                "noframe": "true",
                "noLoad": "",
                "hideEmpty": "",
                "collapsible": "",
                "collapsibleExpanded": "true",
                "collapsibleLabelExpanded": "Hide Details",
                "collapsibleLabelCollapsed": "View Details",
                "permissionHidden": "",
                "storeBinder": {
                  "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                  "properties": {}
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Form Generator Implementation

### Validation Logic

```python
# src/joget_form_generator/patterns/validators/ajax_subform_validator.py

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ValidationError:
    field_id: str
    property_name: str
    message: str
    severity: str  # 'error' | 'warning'

def validate_ajax_subform_pattern(form_spec: dict) -> List[ValidationError]:
    """
    Validates SelectBox + AjaxSubForm pattern configuration.
    
    Critical rules checked:
    1. SelectBox idColumn must be empty when linked to AjaxSubForm
    2. AjaxSubForm ajax property must be "true"
    3. AjaxSubForm parentSubFormId must reference existing SelectBox
    4. AjaxSubForm subFormParentId should be empty for lookup pattern
    """
    errors = []
    
    # Collect all field definitions
    selectboxes = {}
    ajax_subforms = []
    
    for section in form_spec.get('sections', []):
        for column in section.get('columns', []):
            for field in column.get('fields', []):
                if field.get('type') == 'selectbox':
                    selectboxes[field['id']] = field
                elif field.get('type') == 'ajax_subform':
                    ajax_subforms.append(field)
    
    # Validate each AjaxSubForm
    for subform in ajax_subforms:
        subform_id = subform.get('id', 'unknown')
        
        # Rule 1: ajax must be true
        if subform.get('ajax') != True and subform.get('ajax') != 'true':
            errors.append(ValidationError(
                field_id=subform_id,
                property_name='ajax',
                message="AjaxSubForm 'ajax' property must be true for dynamic loading",
                severity='error'
            ))
        
        # Rule 2: parentSubFormId must reference existing SelectBox
        parent_id = subform.get('parentSubFormId', '')
        if not parent_id:
            errors.append(ValidationError(
                field_id=subform_id,
                property_name='parentSubFormId',
                message="AjaxSubForm 'parentSubFormId' must reference a SelectBox field ID",
                severity='error'
            ))
        elif parent_id not in selectboxes:
            errors.append(ValidationError(
                field_id=subform_id,
                property_name='parentSubFormId',
                message=f"AjaxSubForm references non-existent field '{parent_id}'",
                severity='error'
            ))
        else:
            # Rule 3: The linked SelectBox idColumn must be empty
            linked_selectbox = selectboxes[parent_id]
            options_source = linked_selectbox.get('optionsSource', {})
            id_column = options_source.get('idColumn', '')
            
            if id_column:
                errors.append(ValidationError(
                    field_id=parent_id,
                    property_name='optionsSource.idColumn',
                    message=(
                        f"SelectBox '{parent_id}' has idColumn='{id_column}' but is linked "
                        f"to AjaxSubForm. idColumn MUST be empty (use primary key) for "
                        f"AjaxSubForm lookup to work correctly."
                    ),
                    severity='error'
                ))
        
        # Rule 4: Warn if subFormParentId is set (usually wrong for lookup pattern)
        if subform.get('subFormParentId'):
            errors.append(ValidationError(
                field_id=subform_id,
                property_name='subFormParentId',
                message=(
                    "subFormParentId is set but typically should be empty for lookup pattern. "
                    "Only set this if you need to store a foreign key relationship."
                ),
                severity='warning'
            ))
    
    return errors
```

### Pattern Transformer

```python
# src/joget_form_generator/patterns/fields/ajax_subform.py

from typing import Dict, Any

class AjaxSubFormPattern:
    """
    Transforms YAML ajax_subform specification to Joget JSON.
    
    Enterprise Edition only.
    """
    
    joget_class = "org.joget.plugin.enterprise.AjaxSubForm"
    
    def render(self, field_spec: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Joget JSON for AjaxSubForm element.
        
        Required spec properties:
            - id: Field ID
            - formDefId: Form to load in subform
            - parentSubFormId: ID of SelectBox to watch
            
        Optional spec properties:
            - label: Display label
            - ajax: Enable dynamic loading (default: true)
            - readonly: Make subform read-only (default: true for this pattern)
            - noframe: Hide frame styling (default: false)
            - collapsible: Allow collapse (default: false)
        """
        
        # Enforce critical defaults for this pattern
        ajax_value = field_spec.get('ajax', True)
        if isinstance(ajax_value, bool):
            ajax_value = "true" if ajax_value else ""
        
        return {
            "className": self.joget_class,
            "properties": {
                "id": field_spec["id"],
                "label": field_spec.get("label", ""),
                "formDefId": field_spec["formDefId"],
                
                # CRITICAL: These must be set correctly
                "ajax": "true",  # Always true for this pattern
                "parentSubFormId": field_spec["parentSubFormId"],
                "subFormParentId": field_spec.get("subFormParentId", ""),
                
                # Display options
                "readonly": "true" if field_spec.get("readonly", True) else "",
                "readonlyLabel": "",
                "noframe": "true" if field_spec.get("noframe", False) else "",
                "noLoad": "",
                "hideEmpty": "true" if field_spec.get("hideEmpty", False) else "",
                
                # Collapsible options
                "collapsible": "true" if field_spec.get("collapsible", False) else "",
                "collapsibleExpanded": "true" if field_spec.get("collapsibleExpanded", True) else "",
                "collapsibleLabelExpanded": field_spec.get("collapsibleLabelExpanded", "Hide Details"),
                "collapsibleLabelCollapsed": field_spec.get("collapsibleLabelCollapsed", "View Details"),
                
                # Permission
                "permissionHidden": "",
                
                # Binder (required, even if default)
                "storeBinder": {
                    "className": "org.joget.apps.form.lib.WorkflowFormBinder",
                    "properties": {}
                }
            }
        }
```

### SelectBox Pattern Update

Add this to the existing SelectBox pattern to handle the `idColumn` constraint:

```python
# Addition to src/joget_form_generator/patterns/fields/select_box.py

def render_form_options_binder(self, options_source: Dict[str, Any], 
                               linked_to_ajax_subform: bool = False) -> Dict[str, Any]:
    """
    Generate FormOptionsBinder configuration.
    
    Args:
        options_source: The optionsSource spec from YAML
        linked_to_ajax_subform: If True, forces idColumn to empty
    """
    
    id_column = options_source.get('idColumn', '')
    
    # CRITICAL: If linked to AjaxSubForm, idColumn MUST be empty
    if linked_to_ajax_subform and id_column:
        raise ValueError(
            f"SelectBox linked to AjaxSubForm cannot have idColumn='{id_column}'. "
            f"The idColumn must be empty to use the record's primary key for lookup."
        )
    
    return {
        "className": "org.joget.apps.form.lib.FormOptionsBinder",
        "properties": {
            "formDefId": options_source["formId"],
            "idColumn": "",  # Empty for AjaxSubForm pattern
            "labelColumn": options_source["labelColumn"],
            "groupingColumn": options_source.get("groupColumn", ""),
            "extraCondition": options_source.get("extraCondition", ""),
            "addEmptyOption": "true" if options_source.get("addEmptyOption", True) else "",
            "emptyLabel": options_source.get("emptyLabel", ""),
            "useAjax": "true" if options_source.get("useAjax", False) else "",
            "cacheInterval": options_source.get("cacheInterval", "")
        }
    }
```

---

## Troubleshooting Guide

### Problem: AjaxSubForm Doesn't Load Data

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Nothing happens when selecting | `ajax` is not "true" | Set `ajax: "true"` |
| Nothing happens when selecting | `parentSubFormId` empty or wrong | Set to SelectBox field ID |
| Options show but wrong data loads | `idColumn` is not empty | Clear `idColumn` in SelectBox |
| Subform shows "No data" | Form IDs don't match | Ensure `formDefId` matches in both |
| JavaScript console errors | Field ID has special characters | Use alphanumeric IDs only |

### Debugging Steps

1. **Browser Developer Tools (F12)**
   - Network tab: Look for AJAX requests when selecting
   - Console: Check for JavaScript errors

2. **Verify Field IDs**
   ```javascript
   // In browser console
   $('#equipment_selector').val()  // Check SelectBox value
   ```

3. **Check JSON Export**
   - Export form JSON from Joget Form Builder
   - Verify all critical properties are set correctly

4. **Test with Known-Working Example**
   - Download demo app from Joget Marketplace: "Ajax Subform Demo"
   - Compare configurations

---

## Comparison: AjaxSubForm vs Regular Subform vs Grid

| Feature | AjaxSubForm | Subform | Grid |
|---------|-------------|---------|------|
| **Dynamic Loading** | ✅ Yes | ❌ No | ❌ No |
| **Triggered by Field** | ✅ Yes | ❌ No | ❌ No |
| **Single Record** | ✅ Yes | ✅ Yes | ❌ No |
| **Multiple Records** | ❌ No | ❌ No | ✅ Yes |
| **Editable** | ✅ Optional | ✅ Yes | ✅ Yes |
| **Edition Required** | Enterprise | Community | Community |
| **Use Case** | Lookup display | Embedded form | Multi-row data |

---

## Related Patterns

- **Cascading Dropdown Pattern**: SelectBox → SelectBox filtering (`controlField` + `groupingColumn`)
- **Master-Detail Pattern**: Form → Grid with foreign key relationship
- **Subform Pattern**: Embedded form for one-to-one relationships

---

## References

### Joget Documentation
- [AJAX Subform - DX8 Knowledge Base](https://dev.joget.org/community/display/DX8/AJAX+Subform)
- [Subforms - DX8 Knowledge Base](https://dev.joget.org/community/display/DX8/Subforms)
- [Form Field Element Plugin API](https://dev.joget.org/community/display/DX8/Form+Field+Element+Plugin)

### Key Properties from Source Code

From `org.joget.apps.form.model.AbstractSubForm`:
```java
public static final String PROPERTY_PARENT_SUBFORM_ID = "parentSubFormId";
// Field ID in parent form used to store subform primary key as reference

public static final String PROPERTY_SUBFORM_PARENT_ID = "subFormParentId";
// Field ID in subform used to store parent form primary key as foreign key
```

### Project Knowledge
- `METADATA_MANUAL.md` - Cascading dropdown patterns for MDM
- `improved-form-generator.md` - Form generator architecture
- `jdx-form-gen-design.md` - Pattern library design

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.2.0 | 2025-12-19 | Aligned with project version, updated formatting |
| 1.0 | Dec 2024 | Initial documentation based on debugging session |
