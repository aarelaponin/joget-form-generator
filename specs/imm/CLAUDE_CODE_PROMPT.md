# Claude Code Prompt: Generate IMM Joget Forms

## Context

Generate Joget DX forms for the **Inputs Management Module (IMM)** from YAML specifications located in `specs/imm/`.

## Project Location

```
/Users/aarelaponin/PycharmProjects/dev/joget-form-generator
```

## Form Inventory (18 specs)

### Main Transactional Forms (4)
| Form | Description |
|------|-------------|
| `imCampaign.yaml` | Campaign management with grids |
| `imEntitlement.yaml` | Farmer entitlements |
| `imDistribution.yaml` | Distribution transactions |
| `imAgroDealer.yaml` | Agro-dealer registration |

### Grid Sub-forms (5)
| Form | Used By |
|------|---------|
| `imCampaignInput.yaml` | imCampaign |
| `imCampaignDistPt.yaml` | imCampaign |
| `imEntitlementItem.yaml` | imEntitlement |
| `imDistribItem.yaml` | imDistribution |
| `mdPackageContent.yaml` | mdInputPackage |

### Master Data Forms (9)
| Form | Description |
|------|-------------|
| `mdInputCategory.yaml` | Input categories (Seed, Fertilizer, etc.) |
| `mdInput.yaml` | Input catalogue |
| `mdInputPackage.yaml` | Pre-defined bundles |
| `mdDistribPoint.yaml` | Distribution locations |
| `mdCampaignType.yaml` | Campaign types |
| `mdDistribModel.yaml` | Distribution methods |
| `mdAllocBasis.yaml` | Allocation calculation methods |
| `mdTargetCategory.yaml` | Target farmer categories |
| `mdDealerCategory.yaml` | Dealer tiers |

## Task: Validate and Generate Forms

### Step 1: Validate All Specifications

```bash
cd /Users/aarelaponin/PycharmProjects/dev/joget-form-generator
source venv/bin/activate

# Validate all specs
for spec in specs/imm/*.yaml; do
  [[ $(basename "$spec") == "CLAUDE_CODE_PROMPT.md" ]] && continue
  echo "=== Validating: $spec ==="
  joget-form-gen validate "$spec"
done
```

### Step 2: Generate Forms in Dependency Order

```bash
mkdir -p specs/imm/output

# Phase 1: Simple Master Data (no dependencies)
for spec in mdInputCategory mdCampaignType mdDistribModel mdAllocBasis mdTargetCategory mdDealerCategory; do
  echo "=== Generating: $spec ==="
  joget-form-gen generate specs/imm/${spec}.yaml -o specs/imm/output/
done

# Phase 2: Master Data with Dependencies
for spec in mdInput mdDistribPoint mdPackageContent mdInputPackage; do
  echo "=== Generating: $spec ==="
  joget-form-gen generate specs/imm/${spec}.yaml -o specs/imm/output/
done

# Phase 3: Grid Sub-forms
for spec in imCampaignInput imCampaignDistPt imEntitlementItem imDistribItem; do
  echo "=== Generating: $spec ==="
  joget-form-gen generate specs/imm/${spec}.yaml -o specs/imm/output/
done

# Phase 4: Main Transactional Forms
for spec in imAgroDealer imCampaign imEntitlement imDistribution; do
  echo "=== Generating: $spec ==="
  joget-form-gen generate specs/imm/${spec}.yaml -o specs/imm/output/
done
```

### Step 3: Verify Output

```bash
echo "=== Generated Files ==="
ls -la specs/imm/output/*.json 2>/dev/null | wc -l
ls specs/imm/output/
```

## Expected Output

18 JSON files in `specs/imm/output/`:
```
imAgroDealer.json      imDistribution.json     mdAllocBasis.json      mdDistribPoint.json
imCampaign.json        imEntitlement.json      mdCampaignType.json    mdInput.json
imCampaignDistPt.json  imEntitlementItem.json  mdDealerCategory.json  mdInputCategory.json
imCampaignInput.json   imDistribItem.json      mdDistribModel.json    mdInputPackage.json
                                               mdPackageContent.json  mdTargetCategory.json
```

## Common Validation Fixes

### If validation fails on `formGrid` type:
The specs use Enterprise `formGrid`. If not supported, convert to basic structure:
```yaml
# Before (Enterprise)
- id: items
  type: formGrid
  formId: subFormId

# After (basic alternative - remove if generator doesn't support)
# Or keep and handle the error during generation
```

### If validation fails on `calculationField`:
This is an Enterprise feature. Remove or convert to textField with readonly:
```yaml
# Before
- type: calculationField
  equation: "..."

# After
- type: textField
  readonly: true
```

### If validation fails on `optionsSource`:
Ensure referenced forms exist or use inline options:
```yaml
# optionsSource references another form
optionsSource:
  type: formData
  formId: mdCampaignType  # This form must exist
```

## Import to Joget

Import in this order:
1. Master Data forms (md*.json)
2. Grid sub-forms (imCampaignInput, imCampaignDistPt, etc.)
3. Main forms (imCampaign, imEntitlement, etc.)

## Notes

- All specs reference `mdDistrict` and `mdAgroEcoZone` from existing Farmer Registry
- `imAgroDealer` must be imported before `mdDistribPoint` (has lookup reference)
- Form IDs are max 20 characters as required by Joget
