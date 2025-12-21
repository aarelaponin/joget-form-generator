# IMM Form Relationships

## Overview

The Input Management Module (IMM) consists of 8 transactional forms. Parent-child relationships use either:
- **Embedded FormGrid** - for short lists (max ~10-20 items)
- **Linked forms** - for potentially long lists (managed via separate CRUD/datalist)

## Design Rules

1. **One grid per form** - Maximum one embedded FormGrid per form
2. **Short lists only** - FormGrid should not be used for potentially long lists
3. **Long lists → Linked forms** - Use separate form with FK reference instead

---

## Form Hierarchy Diagram

```
imCampaign (Main)
└── imCampaignInput (Embedded grid) ────── FK: campaignId

imCampaignDistPt (Linked to imCampaign) ── FK: campaignId  [separate CRUD]

imEntitlement (Main)
└── imEntitlementItem (Embedded grid) ──── FK: entitlementId

imDistribution (Main)
└── imDistribItem (Embedded grid) ───────── FK: distributionId

imAgroDealer (Main - Standalone)
```

---

## Detailed Form Relationships

### 1. Campaign Management

| Parent Form | Child Form | Relationship Type | FK Field |
|-------------|------------|-------------------|----------|
| **imCampaign** | imCampaignInput | Embedded grid | `campaignId` |
| **imCampaign** | imCampaignDistPt | Linked (separate CRUD) | `campaignId` |

**imCampaign** contains ONE FormGrid:
- `campaignInputs` → embeds `imCampaignInput` (min 1 row required)

**imCampaignDistPt** is managed separately:
- Linked via `campaignId` FK field
- Access via datalist filtered by campaign
- Reason: Distribution points list can be very long

### 2. Farmer Entitlement

| Parent Form | Child Form | Relationship Type | FK Field |
|-------------|------------|-------------------|----------|
| **imEntitlement** | imEntitlementItem | Embedded grid | `entitlementId` |

**imEntitlement** contains ONE FormGrid:
- `entitlementItems` → embeds `imEntitlementItem` (readonly)
- Typically short list (package contents, ~5-10 items)

### 3. Distribution Transaction

| Parent Form | Child Form | Relationship Type | FK Field |
|-------------|------------|-------------------|----------|
| **imDistribution** | imDistribItem | Embedded grid | `distributionId` |

**imDistribution** contains ONE FormGrid:
- `itemsDistributed` → embeds `imDistribItem` (min 1 row required)
- Typically short list (items in one transaction, ~1-5 items)

### 4. Agro-Dealer (Standalone)

**imAgroDealer** is a standalone form with no child forms.

---

## Foreign Key (FK) Fields

Each child form has a hidden field storing the parent record's ID:

| Child Form | FK Hidden Field | Parent Form | Relationship |
|------------|-----------------|-------------|--------------|
| imCampaignInput | `campaignId` | imCampaign | Embedded |
| imCampaignDistPt | `campaignId` | imCampaign | Linked |
| imEntitlementItem | `entitlementId` | imEntitlement | Embedded |
| imDistribItem | `distributionId` | imDistribution | Embedded |

---

## MDM Form References

| Transactional Form | References MDM Forms |
|--------------------|---------------------|
| imCampaign | md39CampaignType, md40DistribModel, md42TargetCategory |
| imCampaignInput | md44Input, md41AllocBasis |
| imCampaignDistPt | md45DistribPoint |
| imDistribution | md45DistribPoint |
| imDistribItem | md44Input |
| imEntitlement | md46InputPackage |
| imEntitlementItem | md44Input |
| imAgroDealer | md43DealerCategory, md38InputCategory |

---

## Form Summary Table

| Form ID | Type | Description | Grid Embedding |
|---------|------|-------------|----------------|
| imCampaign | Main | Campaign definition | 1 grid (inputs) |
| imCampaignInput | Detail | Inputs allocated to campaign | Embedded in imCampaign |
| imCampaignDistPt | Linked | Distribution points for campaign | Linked (separate CRUD) |
| imEntitlement | Main | Farmer entitlement record | 1 grid (items) |
| imEntitlementItem | Detail | Individual input entitlements | Embedded in imEntitlement |
| imDistribution | Main | Distribution transaction | 1 grid (items) |
| imDistribItem | Detail | Items in distribution | Embedded in imDistribution |
| imAgroDealer | Main | Agro-dealer registration | No grids |

---

## Notes

1. **One Grid Rule**: Each main form has at most ONE embedded FormGrid to keep complexity manageable.

2. **Long Lists**: Distribution points (`imCampaignDistPt`) are managed via separate CRUD because:
   - A campaign may have hundreds of distribution points
   - Embedded grids become unwieldy with long lists
   - Separate management allows better filtering/searching

3. **FormGrid Configuration**: The FormGrid field specifies:
   - `formId`: Child form to embed
   - `foreignKey`: FK field in child form
   - `columns`: Fields to display in grid
   - `allowAddRow` / `allowDeleteRow`: Row management
   - `validateMinRow`: Minimum required rows
