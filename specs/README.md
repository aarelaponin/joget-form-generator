# Form Specifications

This folder contains YAML specifications for Joget DX forms organized by component/module.

## Folder Structure

Each component folder follows a standardized structure:

```
specs/
├── <component>/
│   ├── input/      # YAML specifications (source files)
│   ├── output/     # Generated JSON files (Joget form definitions)
│   └── data/       # CSV reference/seed data for master data
│       └── archive/  # Archived/consolidated CSV files
```

### Current Components

- `existing-farmer/` - Farmer registration forms (existing system)
- `existing-mdm/` - Master Data Management reference data (existing system)
- `imm/` - Input Management Module forms

### Nested LOV Pattern Applied

The following MDM data has been consolidated using the [Nested LOV Refactoring Pattern](../docs/NESTED_LOV_REFACTORING_PATTERN.md):

| Parent Form | Child Form | Description |
|-------------|------------|-------------|
| md191cropCategory | md19crops | Crop types by category (cereals, legumes, etc.) |
| md161livestockCategory | md16livestockType | Livestock by category (poultry, large livestock, etc.) |
| md25equipmentCategory | md25equipmentType | Equipment by category (tillage, planting, etc.) |
| md27inputCategory | md27inputType | Agricultural inputs by category (fertilizer, pesticides, etc.) |

Original separate CSV files are archived in `existing-mdm/data/archive/`.

## Usage

### Generate forms from YAML specifications

```bash
# Generate a single form
joget-form-gen generate specs/imm/input/md38InputCategory.yaml -o specs/imm/output/

# Generate all specs in a component
for f in specs/imm/input/*.yaml; do
  joget-form-gen generate "$f" -o specs/imm/output/
done
```

### Validate specifications

```bash
# Validate a single spec
joget-form-gen validate specs/imm/input/md38InputCategory.yaml

# Validate all specs in a component
for f in specs/imm/input/*.yaml; do
  echo "=== Validating: $f ==="
  joget-form-gen validate "$f"
done
```

## Naming Conventions

### YAML Specifications (input/)
- MDM forms: `md<NN><EntityName>.yaml` (e.g., `md38InputCategory.yaml`)
- Transaction forms: `<module><EntityName>.yaml` (e.g., `imCampaign.yaml`)

### Generated JSON (output/)
- Same base name as YAML: `md38InputCategory.json`, `imCampaign.json`

### Reference Data (data/)
- CSV files matching MDM form names: `md38InputCategory.csv`
- Used for seeding master data tables

## Specification Reference

See [YAML Specification Reference](../docs/YAML_SPECIFICATION.md) for complete documentation on:
- Form metadata requirements
- All 17 supported field types
- Options sources (static, formData, api, database)
- Validation rules
- Examples
