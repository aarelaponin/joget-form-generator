# Nested LOV Refactoring Pattern - Form Generator Documentation

**Version:** 0.2.0
**Last Updated:** 2025-12-21
**Joget Version:** DX8 Enterprise/Community Edition
**Status:** Production Ready

---

## Overview

The **Nested (Cascading) LOV Pattern** transforms flat, lengthy dropdown lists into hierarchical category-based selections. When a user selects a category, the child dropdown is dynamically filtered to show only items belonging to that category.

This pattern is commonly used for:
- Long reference data lists (crops, equipment, products)
- Hierarchical data (country → state → city)
- Categorized master data (category → items)

### When to Apply This Refactoring

| Indicator | Action |
|-----------|--------|
| Flat LOV with 15+ items | Strong candidate for nesting |
| Data has natural categories | Apply this pattern |
| Users struggle to find items | Improves UX significantly |
| CSV has a `category` column | Ready for extraction |

---

## Pattern Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  BEFORE: Flat LOV (md19crops)                                        │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ code    | name           | crop_category (just a text column)  │  │
│  │ maize   | Maize          | cereals                             │  │
│  │ rice    | Rice           | cereals                             │  │
│  │ groundnuts | Groundnuts  | legumes                             │  │
│  │ ... (20+ items in one long dropdown)                           │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘

                              ↓ REFACTOR TO ↓

┌──────────────────────────────────────────────────────────────────────┐
│  AFTER: Nested LOV                                                   │
│                                                                      │
│  ┌─────────────────────────┐                                         │
│  │  Parent MDM Form        │  (md191cropCategory)                    │
│  │  code    | name         │                                         │
│  │  cereals | Cereals      │                                         │
│  │  legumes | Legumes      │                                         │
│  │  tubers  | Tubers       │                                         │
│  └─────────────────────────┘                                         │
│              ↑                                                       │
│              │ SelectBox loads from parent                           │
│              │                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │  Child MDM Form (md19crops)                                   │   │
│  │  code    | crop_category (SelectBox!) | name                  │   │
│  │  maize   | cereals                    | Maize                 │   │
│  │  rice    | cereals                    | Rice                  │   │
│  │  groundnuts | legumes                 | Groundnuts            │   │
│  └───────────────────────────────────────────────────────────────┘   │
│              ↑                                                       │
│              │ Both used in Consumer Form                            │
│              │                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │  Consumer Form (f01.05-1 - Crop Management)                   │   │
│  │                                                               │   │
│  │  cropCategory (SelectBox - Parent)                            │   │
│  │    └─ Loads from: md191cropCategory                           │   │
│  │                                                               │   │
│  │  cropType (SelectBox - Child with Cascading)                  │   │
│  │    ├─ Loads from: md19crops                                   │   │
│  │    ├─ groupingColumn: "crop_category"                         │   │
│  │    ├─ controlField: "cropCategory"                            │   │
│  │    └─ useAjax: "true"                                         │   │
│  └───────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

### How Cascading Works

1. User selects "Cereals" in `cropCategory` field
2. The `controlField` property links `cropType` to `cropCategory`
3. Joget filters `md19crops` table WHERE `crop_category` = "cereals"
4. `cropType` shows only: Maize, Sorghum, Rice, Millet, Wheat

---

## Step-by-Step Refactoring Process

### Step 1: Identify Categories from Existing Data

Analyze your existing CSV/data to extract unique categories:

```csv
# Original md19crops.csv
id,code,name,crop_category
1,maize,Maize,cereals
2,sorghum,Sorghum,cereals
...
6,groundnuts,Groundnuts,legumes
```

Extract unique categories:
```
cereals, legumes, tubers, vegetables, other
```

### Step 2: Create Parent MDM Form (Category)

Create a new MDM form for categories with **only code and name**:

**Form ID:** `md191cropCategory` (use `.1` suffix for sub-categories)
**Fields:**
- `code` - TextField with DuplicateValueValidator
- `name` - TextField (required)
- `isActive` - Radio Y/N (optional but recommended)

```json
{
  "className": "org.joget.apps.form.model.Form",
  "properties": {
    "id": "md191cropCategory",
    "name": "MD.19.1 - Crop Category",
    "tableName": "md191cropCategory"
  },
  "elements": [
    {
      "className": "org.joget.apps.form.lib.TextField",
      "properties": {
        "id": "code",
        "label": "Code",
        "validator": {
          "className": "org.joget.apps.form.lib.DuplicateValueValidator",
          "properties": {
            "formDefId": "md191cropCategory",
            "fieldId": "code",
            "mandatory": "true"
          }
        }
      }
    },
    {
      "className": "org.joget.apps.form.lib.TextField",
      "properties": {
        "id": "name",
        "label": "Name",
        "validator": {
          "className": "org.joget.apps.form.lib.DefaultValidator",
          "properties": { "mandatory": "true" }
        }
      }
    }
  ]
}
```

### Step 3: Update Child MDM Form (Add SelectBox)

**CRITICAL:** The category field MUST be a **SelectBox**, not a TextField!

Update the existing child form to replace the text-based category column with a SelectBox that loads from the parent:

```json
{
  "className": "org.joget.apps.form.lib.SelectBox",
  "properties": {
    "id": "crop_category",
    "label": "Crop Category",
    "optionsBinder": {
      "className": "org.joget.apps.form.lib.FormOptionsBinder",
      "properties": {
        "formDefId": "md191cropCategory",
        "idColumn": "code",
        "labelColumn": "name",
        "addEmptyOption": "true"
      }
    },
    "validator": {
      "className": "org.joget.apps.form.lib.DefaultValidator",
      "properties": { "mandatory": "true" }
    }
  }
}
```

### Step 4: Update Consumer Forms (Add Cascading)

Add a new category SelectBox and configure cascading on the existing type SelectBox:

**New Field - Category (Parent):**
```json
{
  "className": "org.joget.apps.form.lib.SelectBox",
  "properties": {
    "id": "cropCategory",
    "label": "Crop Category",
    "optionsBinder": {
      "className": "org.joget.apps.form.lib.FormOptionsBinder",
      "properties": {
        "formDefId": "md191cropCategory",
        "idColumn": "code",
        "labelColumn": "name",
        "addEmptyOption": "true",
        "emptyLabel": "-- Select Category --"
      }
    },
    "validator": {
      "className": "org.joget.apps.form.lib.DefaultValidator",
      "properties": { "mandatory": "true" }
    }
  }
}
```

**Updated Field - Type (Child with Cascading):**
```json
{
  "className": "org.joget.apps.form.lib.SelectBox",
  "properties": {
    "id": "cropType",
    "label": "Crop Type",
    "optionsBinder": {
      "className": "org.joget.apps.form.lib.FormOptionsBinder",
      "properties": {
        "formDefId": "md19crops",
        "idColumn": "code",
        "labelColumn": "name",
        "groupingColumn": "crop_category",
        "addEmptyOption": "true",
        "emptyLabel": "-- Select Crop --",
        "useAjax": "true"
      }
    },
    "controlField": "cropCategory",
    "validator": {
      "className": "org.joget.apps.form.lib.DefaultValidator",
      "properties": { "mandatory": "true" }
    }
  }
}
```

---

## Critical Configuration Rules

### The 4 Must-Have Properties

| Property | Location | Value | Purpose |
|----------|----------|-------|---------|
| **groupingColumn** | Child SelectBox optionsBinder | Field ID in child MDM (e.g., `crop_category`) | Tells Joget which field to filter by |
| **controlField** | Child SelectBox properties | Parent field ID in same form (e.g., `cropCategory`) | Links child to parent field |
| **useAjax** | Child SelectBox optionsBinder | `"true"` | Enables dynamic filtering |
| **SelectBox in Child MDM** | Child MDM form | Category field must be SelectBox | Creates the filterable relationship |

### Common Pitfalls

| Mistake | Symptom | Solution |
|---------|---------|----------|
| Category field is TextField in child MDM | Cascading doesn't work | Change to SelectBox with FormOptionsBinder |
| `groupingColumn` is empty | Child shows all options | Set to category field ID in child form |
| `controlField` is empty | Child shows all options | Set to parent field ID in consumer form |
| `useAjax` is empty or false | Options don't refresh | Set to `"true"` |
| Wrong `groupingColumn` value | No matches found | Must match the **field ID** in child MDM |
| Wrong `controlField` value | Child doesn't react | Must match the **field ID** in current form |

---

## Configuration Reference Table

### Property Mapping

```
Consumer Form                          Child MDM Form              Parent MDM Form
─────────────────────────────────────  ────────────────────────   ──────────────────
┌─────────────────────┐                ┌──────────────────────┐   ┌────────────────┐
│ cropCategory        │ ───loads───→  │                      │   │ md191cropCategory │
│ (Parent SelectBox)  │   from        │                      │   │ code | name    │
│ formDefId: "md191   │               │                      │   └────────────────┘
│   cropCategory"     │               │                      │          ↑
│ idColumn: "code"    │               │ md19crops            │          │
│ labelColumn: "name" │               │ code | crop_category │──────────┘
└─────────────────────┘               │       (SelectBox!)   │   loads category
        ↓                             │       | name         │   options from
        │                             └──────────────────────┘   parent
        │ controlField                         ↑
        ↓                                      │
┌─────────────────────┐                        │
│ cropType            │ ─────loads from────────┘
│ (Child SelectBox)   │
│ formDefId: "md19    │
│   crops"            │
│ idColumn: "code"    │
│ labelColumn: "name" │
│ groupingColumn:     │ ← Must match field ID in child MDM
│   "crop_category"   │
│ controlField:       │ ← Must match parent field ID in THIS form
│   "cropCategory"    │
│ useAjax: "true"     │ ← Required for dynamic filtering
└─────────────────────┘
```

---

## YAML Specification Example (Future)

```yaml
# Nested LOV pattern for form generator
form:
  id: cropManagementForm
  name: "Crop Management"
  tableName: crop_management

fields:
  - id: cropCategory
    type: selectBox
    label: "Crop Category"
    required: true
    optionsSource:
      type: form
      formId: md191cropCategory
      idColumn: code
      labelColumn: name
      addEmptyOption: true
      emptyLabel: "-- Select Category --"

  - id: cropType
    type: selectBox
    label: "Crop Type"
    required: true
    optionsSource:
      type: form
      formId: md19crops
      idColumn: code
      labelColumn: name
      groupingColumn: crop_category   # Field in source form
      addEmptyOption: true
      emptyLabel: "-- Select Crop --"
      useAjax: true
    controlField: cropCategory        # Field in this form
```

---

## Troubleshooting Guide

### Problem: Child Dropdown Shows All Options (No Filtering)

| Check | Expected | Fix |
|-------|----------|-----|
| `groupingColumn` | Field ID (e.g., `crop_category`) | Set the correct field name |
| `controlField` | Parent field ID (e.g., `cropCategory`) | Set to match parent SelectBox |
| `useAjax` | `"true"` | Must be string "true" |
| Category field type in child MDM | SelectBox | Change TextField to SelectBox |

### Problem: Child Dropdown Is Empty

| Check | Expected | Fix |
|-------|----------|-----|
| Parent MDM has data | Records exist | Add category records first |
| Child MDM has matching values | `crop_category` matches parent `code` | Verify data consistency |
| Case sensitivity | Exact match | `cereals` ≠ `Cereals` |

### Problem: Cascading Works But Wrong Data Saves

| Check | Expected | Fix |
|-------|----------|-----|
| `idColumn` in child | Field that stores value (e.g., `code`) | Verify idColumn setting |
| Database column exists | Column for new field | Run form to create table |

### Debugging Steps

1. **Verify Parent Data First**
   - Open parent MDM form, confirm records exist
   - Note the exact `code` values (case-sensitive)

2. **Verify Child Data**
   - Open child MDM form, check that category SelectBox works
   - Confirm category values match parent codes exactly

3. **Test in Consumer Form**
   - Select a category → check if child dropdown updates
   - If not, check browser console for JavaScript errors

4. **Check JSON Export**
   - Export form from Joget Form Builder
   - Verify all 4 critical properties are set correctly

---

## Real-World Examples

### Example 1: Crops (md19)

**Before:**
- Single dropdown with 22 crop types
- User scrolls through long list

**After:**
- First select: Cereals, Legumes, Tubers, Vegetables, Other (5 options)
- Then select: Only crops in that category (3-8 options each)

### Example 2: Livestock (md16)

**Before:**
- Single dropdown with 18 livestock types

**After:**
- First select: Large Livestock, Small Livestock, Poultry, Working Animals, Wildlife, Other
- Then select: Only animals in that category

### Example 3: Equipment (md25)

**Categories:** Tillage, Planting, Irrigation, Pest Control, Livestock, Storage, Processing, Transport, General Tools

---

## Naming Conventions

### Form IDs

| Type | Pattern | Example |
|------|---------|---------|
| Parent Category | `md{XX}.1{entity}Category` | `md191cropCategory` |
| Child Items | `md{XX}{entity}` | `md19crops` |

### Field IDs

| Type | Pattern | Example |
|------|---------|---------|
| Category field in child MDM | `{entity}_category` or `category` | `crop_category` |
| Parent dropdown in consumer | `{entity}Category` | `cropCategory` |
| Child dropdown in consumer | `{entity}Type` or `{entity}` | `cropType` |

---

## Checklist for Refactoring

- [ ] Identify categories from existing data (CSV column or unique values)
- [ ] Create parent MDM form (code + name + isActive)
- [ ] Create category reference data (CSV or manual entry)
- [ ] Update child MDM: Change category TextField → **SelectBox**
- [ ] Configure child SelectBox to load from parent MDM
- [ ] Find all consumer forms using the child MDM
- [ ] Add parent category SelectBox to each consumer form
- [ ] Update child SelectBox with cascading configuration:
  - [ ] `groupingColumn` = category field ID in child MDM
  - [ ] `controlField` = parent field ID in consumer form
  - [ ] `useAjax` = `"true"`
- [ ] Test cascading behavior
- [ ] Verify data saves correctly

---

## Related Patterns

- **AJAX Subform Pattern**: SelectBox → AjaxSubForm for dynamic record display
- **Three-Level Cascading**: Region → Country → State → City
- **Multiple Parent Dependencies**: Filter by Category AND Brand

---

## References

### Joget Documentation
- [Dynamic Cascading Drop-Down List](https://dev.joget.org/community/display/DX8/Dynamic+Cascading+Drop-Down+List)
- [Form Options Binder](https://dev.joget.org/community/display/DX8/Form+Options+Binder)

### Project Documentation
- `sample-forms/01_nested_lovs/JOGET_NESTED_LOV_GUIDE.md` - Comprehensive implementation guide
- `docs/AJAX_SUBFORM_PATTERN.md` - Related dynamic loading pattern

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.2.0 | 2025-12-21 | Initial documentation for nested LOV refactoring pattern |
