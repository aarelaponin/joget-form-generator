# Form Specifications

This folder contains YAML specifications for Joget DX forms organized by module and component.

For complete governance rules, see [Configuration Management Plan](CONFIGURATION_MANAGEMENT_PLAN.md).

## Folder Structure

```
specs/
├── CONFIGURATION_MANAGEMENT_PLAN.md   # Governance rules and templates
├── README.md                          # This file
│
├── <module>/                          # System module (e.g., frs, imm, spm)
│   ├── <MODULE>_OVERVIEW.md           # System specification
│   ├── <MODULE>_FORM_MODEL.md         # Entity relationships
│   ├── <MODULE>_CHANGELOG.md          # Version history
│   │
│   ├── <component>/                   # Functional component
│   │   ├── input/                     # YAML specifications (source)
│   │   ├── output/                    # Generated JSON forms
│   │   └── data/                      # Reference/seed data (CSV)
│   │
│   └── _archive/                      # Superseded specifications
│
├── mdm/                               # Master Data Management (shared)
└── gis/                               # GIS Integration (shared)
```

## Current Modules

| Module | Description | Status | Components |
|--------|-------------|--------|------------|
| `frs/` | Farmer Registration System | Active | farm, parcel |
| `imm/` | Input Management Module | Active | campaign, allocation, distribution |
| `spm/` | Social Protection Module | Active | program, application, eligibility |
| `mdm/` | Master Data Management | Active | (shared reference data) |
| `gis/` | GIS Integration | Planning | (shared spatial services) |
| `jre/` | Joget Rules Engine | Active | rules, fields, scopes |

## Quick Start

### Generate forms from YAML specifications

```bash
# Generate a single form
joget-form-gen generate specs/frs/farm/input/frFarmer.yaml -o specs/frs/farm/output/

# Generate all specs in a component
for f in specs/frs/farm/input/*.yaml; do
  joget-form-gen generate "$f" -o specs/frs/farm/output/
done
```

### Validate specifications

```bash
# Validate a single spec
joget-form-gen validate specs/frs/farm/input/frFarmer.yaml

# Validate all specs in a module
for f in specs/frs/*/input/*.yaml; do
  echo "=== Validating: $f ==="
  joget-form-gen validate "$f"
done
```

## Naming Conventions

### Form IDs by Module

| Module | Pattern | Example |
|--------|---------|---------|
| MDM | `md<NN><EntityName>` | `md03district`, `md19crops` |
| FRS | `fr<EntityName>` | `frFarmer`, `frParcel` |
| IMM | `im<EntityName>` | `imCampaign`, `imAllocation` |
| SPM | `sp<EntityName>` | `spProgram`, `spApplication` |
| GIS | `gs<EntityName>` | `gsParcelBoundary` |

### Files

| Type | Convention | Example |
|------|------------|---------|
| YAML spec | `<formId>.yaml` | `frFarmer.yaml` |
| Generated JSON | `<formId>.json` | `frFarmer.json` |
| Reference data | `<formId>.csv` | `md03district.csv` |

## Nested LOV Pattern

The following MDM data uses cascading dropdowns via the [Nested LOV Pattern](../docs/NESTED_LOV_REFACTORING_PATTERN.md):

| Parent Form | Child Form | Description |
|-------------|------------|-------------|
| md191cropCategory | md19crops | Crop types by category |
| md161livestockCategory | md16livestockType | Livestock by category |
| md25equipmentCategory | md25equipmentType | Equipment by category |
| md27inputCategory | md27inputType | Agricultural inputs by category |

## References

- [Configuration Management Plan](CONFIGURATION_MANAGEMENT_PLAN.md) - Governance rules
- [YAML Specification Reference](../docs/YAML_SPECIFICATION.md) - Field types and options
- [API Reference](../docs/API_REFERENCE.md) - Generator API documentation
