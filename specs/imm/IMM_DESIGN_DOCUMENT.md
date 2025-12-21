# Inputs Management Module (IMM) Design Document

## Document Information

| Attribute | Value |
|-----------|-------|
| Version | 1.0 |
| Date | December 2024 |
| Author | FRS Architecture Team |
| Status | Draft |
| Module | IMM - Inputs Management Module |

---

## 1. Executive Summary

The Inputs Management Module (IMM) is responsible for the **operational distribution** of agricultural inputs to farmers who have already been approved through the Subsidy Program application process. 

**Critical Design Principle**: IMM does NOT perform eligibility determination. Eligibility rules, criteria evaluation, and approval decisions are the exclusive responsibility of the **Subsidy Program Module**. IMM operates on the principle that if a farmer has an approved application for a linked program, they are entitled to receive inputs through campaigns associated with that program.

This architecture aligns with international best practices, particularly the **WFP SCOPE** beneficiary management system used by the World Food Programme for global food assistance distribution.

---

## 2. WFP SCOPE Alignment

### 2.1 WFP SCOPE Overview

WFP's SCOPE (Beneficiary Information and Transfer Management Platform) is a cloud-based system that manages distributions from registration to reconciliation. Key SCOPE concepts that inform IMM design:

| SCOPE Concept | SCOPE Definition | FRS Equivalent |
|---------------|------------------|----------------|
| **Identity Registration** | Recording beneficiary personal information | Farmer Registration Module |
| **Intervention** | A program/project providing assistance | Subsidy Program |
| **Enrollment** | Adding eligible beneficiaries to intervention | Application Approval |
| **Distribution Cycle** | Scheduled distribution period | IMM Campaign |
| **Entitlement** | What a beneficiary is entitled to receive | imEntitlement |
| **Distribution** | Actual transfer/delivery of assistance | imDistribution |

### 2.2 SCOPE Process Flow

```
SCOPE Process (WFP):
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Register    │    │   Create     │    │   Enroll     │
│  Identities  │ ─► │ Intervention │ ─► │ Beneficiaries│
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                    ┌──────────────────────────┘
                    ▼
           ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
           │   Approve    │    │   Create     │    │   Create     │
           │  Enrolments  │ ─► │ Dist. Cycle  │ ─► │ Dist. List   │
           └──────────────┘    └──────────────┘    └──────┬───────┘
                                                         │
                    ┌────────────────────────────────────┘
                    ▼
           ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
           │   Execute    │    │   Record     │    │   Reconcile  │
           │ Distribution │ ─► │ Redemption   │ ─► │  & Report    │
           └──────────────┘    └──────────────┘    └──────────────┘
```

**Key Insight from SCOPE**: Beneficiaries must be enrolled AND approved in an intervention BEFORE they can appear on any distribution list. The enrollment/approval is a prerequisite to distribution - distribution systems do not determine eligibility.

---

## 3. Module Boundaries

### 3.1 System Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         FARMERS REGISTRY SYSTEM (FRS)                       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────────────────┐        ┌─────────────────────────────────┐   │
│  │  FARMER REGISTRATION    │        │      SUBSIDY PROGRAM MODULE     │   │
│  │  MODULE                 │        │                                 │   │
│  │                         │        │  ┌───────────────────────────┐  │   │
│  │  • Personal Data        │        │  │ Program Design            │  │   │
│  │  • Household Members    │        │  │  • Basic Information      │  │   │
│  │  • Land Holdings        │        │  │  • Budget & Timeline      │  │   │
│  │  • Crops & Livestock    │        │  │  • ELIGIBILITY RULES  ◄───┼──┼── │
│  │  • Income & Assets      │        │  │  • Benefit Model          │  │   │
│  │                         │        │  └───────────────────────────┘  │   │
│  │         │               │        │                                 │   │
│  │         │ Farmer Data   │        │  ┌───────────────────────────┐  │   │
│  │         ▼               │        │  │ Application Processing    │  │   │
│  │  ┌─────────────┐        │        │  │  • Farmer Applies         │  │   │
│  │  │   Farmer    │────────┼────────┼─►│  • Eligibility Evaluated  │  │   │
│  │  │   Profile   │        │        │  │  • Decision Made          │  │   │
│  │  └─────────────┘        │        │  │  • Application APPROVED   │  │   │
│  │                         │        │  └────────────┬──────────────┘  │   │
│  └─────────────────────────┘        │               │                 │   │
│                                     └───────────────┼─────────────────┘   │
│                                                     │                     │
│  ═══════════════════════════════════════════════════════════════════════  │
│                         ELIGIBILITY BOUNDARY                              │
│      Eligibility rules and approval decisions are ABOVE this line         │
│      Distribution operations are BELOW this line                          │
│  ═══════════════════════════════════════════════════════════════════════  │
│                                                     │                     │
│                                                     │ Approved            │
│                                                     │ Applications        │
│                                                     ▼                     │
│                    ┌────────────────────────────────────────────────┐    │
│                    │       INPUTS MANAGEMENT MODULE (IMM)           │    │
│                    │                                                │    │
│                    │  ┌──────────────────────────────────────────┐  │    │
│                    │  │ Campaign Management                      │  │    │
│                    │  │  • Link to Program (mandatory)           │  │    │
│                    │  │  • Timeline & Budget                     │  │    │
│                    │  │  • Distribution Points                   │  │    │
│                    │  │  • Available Inputs                      │  │    │
│                    │  └──────────────────────────────────────────┘  │    │
│                    │                                                │    │
│                    │  ┌──────────────────────────────────────────┐  │    │
│                    │  │ Entitlement Generation                   │  │    │
│                    │  │  • FROM approved applications ONLY       │  │    │
│                    │  │  • Calculate input quantities            │  │    │
│                    │  │  • Assign distribution points            │  │    │
│                    │  │  • Issue vouchers (if applicable)        │  │    │
│                    │  └──────────────────────────────────────────┘  │    │
│                    │                                                │    │
│                    │  ┌──────────────────────────────────────────┐  │    │
│                    │  │ Distribution Execution                   │  │    │
│                    │  │  • Verify farmer identity                │  │    │
│                    │  │  • Check entitlement exists & valid      │  │    │
│                    │  │  • Record items distributed              │  │    │
│                    │  │  • Capture payment & evidence            │  │    │
│                    │  └──────────────────────────────────────────┘  │    │
│                    │                                                │    │
│                    └────────────────────────────────────────────────┘    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Responsibility Matrix

| Responsibility | Subsidy Program Module | IMM |
|---------------|------------------------|-----|
| Define eligibility criteria | ✅ YES | ❌ NO |
| Evaluate farmer against criteria | ✅ YES | ❌ NO |
| Approve/reject applications | ✅ YES | ❌ NO |
| Create campaigns | ❌ NO | ✅ YES |
| Link campaign to program | ❌ NO | ✅ YES |
| Generate entitlements | ❌ NO | ✅ YES |
| Manage distribution points | ❌ NO | ✅ YES |
| Execute distributions | ❌ NO | ✅ YES |
| Track input inventory | ❌ NO | ✅ YES |
| Record redemptions | ❌ NO | ✅ YES |

### 3.3 What IMM Does NOT Do

**IMM explicitly does NOT:**

1. ❌ Define or store eligibility rules
2. ❌ Evaluate farmer characteristics against eligibility criteria
3. ❌ Make eligibility decisions
4. ❌ Determine who qualifies for support
5. ❌ Override program approval decisions
6. ❌ Allow distribution to farmers without approved applications

**IMM explicitly DOES:**

1. ✅ Verify farmer has approved application for linked program
2. ✅ Verify entitlement exists and is valid
3. ✅ Verify entitlement has not been fully redeemed
4. ✅ Verify voucher has not expired
5. ✅ Verify distribution point is valid for the campaign
6. ✅ Verify farmer identity at collection time

---

## 4. Data Model

### 4.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL ENTITIES                              │
│                        (Managed by other modules)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐          ┌─────────────┐          ┌─────────────┐        │
│   │   farmer    │          │   program   │          │ application │        │
│   │─────────────│          │─────────────│          │─────────────│        │
│   │ id (PK)     │          │ id (PK)     │          │ id (PK)     │        │
│   │ nationalId  │◄─────────┤ programCode │◄────┬────┤ programId   │        │
│   │ fullName    │          │ programName │     │    │ farmerId    │────────┤
│   │ districtCode│          │ status      │     │    │ status      │        │
│   │ phone       │          │ eligRules   │     │    │ approvedDate│        │
│   │ ...         │          │ ...         │     │    │ ...         │        │
│   └─────────────┘          └─────────────┘     │    └─────────────┘        │
│                                    ▲           │            │               │
└────────────────────────────────────┼───────────┼────────────┼───────────────┘
                                     │           │            │
═══════════════════════════════════════════════════════════════════════════════
                               ELIGIBILITY BOUNDARY
═══════════════════════════════════════════════════════════════════════════════
                                     │           │            │
┌────────────────────────────────────┼───────────┼────────────┼───────────────┐
│                              IMM ENTITIES                   │               │
├────────────────────────────────────┼───────────┼────────────┼───────────────┤
│                                    │           │            │               │
│   ┌─────────────────────┐          │           │            │               │
│   │     imCampaign      │          │           │            │               │
│   │─────────────────────│          │           │            │               │
│   │ id (PK)             │          │           │            │               │
│   │ campaignCode        │          │           │            │               │
│   │ campaignName        │          │           │            │               │
│   │ programId (FK) ─────┼──────────┘           │            │               │
│   │ campaignType        │                      │            │               │
│   │ distributionModel   │                      │            │               │
│   │ startDate           │                      │            │               │
│   │ endDate             │                      │            │               │
│   │ totalBudget         │                      │            │               │
│   │ status              │                      │            │               │
│   └──────────┬──────────┘                      │            │               │
│              │                                 │            │               │
│              │ 1:N                             │            │               │
│              ▼                                 │            │               │
│   ┌─────────────────────┐                      │            │               │
│   │  imCampaignInput    │                      │            │               │
│   │─────────────────────│                      │            │               │
│   │ id (PK)             │                      │            │               │
│   │ campaignId (FK)     │                      │            │               │
│   │ inputCode (FK)──────┼──────────────────────┼─►md44Input │               │
│   │ totalQtyAvailable   │                      │            │               │
│   │ subsidyRatePct      │                      │            │               │
│   │ maxPerFarmer        │                      │            │               │
│   └─────────────────────┘                      │            │               │
│                                                │            │               │
│   ┌─────────────────────┐                      │            │               │
│   │ imCampaignDistPt    │                      │            │               │
│   │─────────────────────│                      │            │               │
│   │ id (PK)             │                      │            │               │
│   │ campaignId (FK)─────┼──► imCampaign        │            │               │
│   │ distPointCode (FK)──┼──────────────────────┼─►md45DistribPoint          │
│   │ allocatedBudget     │                      │            │               │
│   │ targetBeneficiaries │                      │            │               │
│   │ operatingSchedule   │                      │            │               │
│   └─────────────────────┘                      │            │               │
│                                                │            │               │
│   ┌─────────────────────┐                      │            │               │
│   │    imEntitlement    │                      │            │               │
│   │─────────────────────│                      │            │               │
│   │ id (PK)             │                      │            │               │
│   │ entitlementCode     │                      │            │               │
│   │ campaignId (FK)─────┼──► imCampaign        │            │               │
│   │ applicationId (FK)──┼──────────────────────┴────────────┘               │
│   │ farmerId (FK)───────┼──► farmer (copied from application)               │
│   │ distPointCode (FK)  │                                                   │
│   │ packageCode (FK)    │                                                   │
│   │ totalEntitleValue   │                                                   │
│   │ totalSubsidyValue   │                                                   │
│   │ voucherCode         │                                                   │
│   │ voucherExpiry       │                                                   │
│   │ status              │                                                   │
│   └──────────┬──────────┘                                                   │
│              │                                                              │
│              │ 1:N                                                          │
│              ▼                                                              │
│   ┌─────────────────────┐                                                   │
│   │ imEntitlementItem   │                                                   │
│   │─────────────────────│                                                   │
│   │ id (PK)             │                                                   │
│   │ entitlementId (FK)  │                                                   │
│   │ inputCode (FK)──────┼──────────────────────────────────►md44Input       │
│   │ qtyEntitled         │                                                   │
│   │ subsidyAmount       │                                                   │
│   │ farmerContrib       │                                                   │
│   │ qtyRedeemed         │                                                   │
│   │ itemStatus          │                                                   │
│   └─────────────────────┘                                                   │
│                                                                             │
│   ┌─────────────────────┐                                                   │
│   │   imDistribution    │                                                   │
│   │─────────────────────│                                                   │
│   │ id (PK)             │                                                   │
│   │ transactionCode     │                                                   │
│   │ campaignId (FK)─────┼──► imCampaign                                     │
│   │ entitlementId (FK)──┼──► imEntitlement                                  │
│   │ farmerId (FK)       │                                                   │
│   │ distributionDate    │                                                   │
│   │ distPointCode (FK)  │                                                   │
│   │ agroDealerId (FK)───┼──► imAgroDealer                                   │
│   │ verificationMethod  │                                                   │
│   │ collectorType       │                                                   │
│   │ totalValue          │                                                   │
│   │ status              │                                                   │
│   └──────────┬──────────┘                                                   │
│              │                                                              │
│              │ 1:N                                                          │
│              ▼                                                              │
│   ┌─────────────────────┐                                                   │
│   │   imDistribItem     │                                                   │
│   │─────────────────────│                                                   │
│   │ id (PK)             │                                                   │
│   │ distributionId (FK) │                                                   │
│   │ inputCode (FK)──────┼──────────────────────────────────►md44Input       │
│   │ quantity            │                                                   │
│   │ unitPrice           │                                                   │
│   │ subsidyAmount       │                                                   │
│   │ farmerPays          │                                                   │
│   │ batchNumber         │                                                   │
│   └─────────────────────┘                                                   │
│                                                                             │
│   ┌─────────────────────┐                                                   │
│   │    imAgroDealer     │ (standalone)                                      │
│   │─────────────────────│                                                   │
│   │ id (PK)             │                                                   │
│   │ dealerCode          │                                                   │
│   │ businessName        │                                                   │
│   │ dealerCategory (FK)─┼──────────────────────────────────►md43DealerCat   │
│   │ districtCode (FK)   │                                                   │
│   │ status              │                                                   │
│   │ ...                 │                                                   │
│   └─────────────────────┘                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Entity Descriptions

#### 4.2.1 Transactional Entities

| Entity | Table Name | Description | Parent |
|--------|------------|-------------|--------|
| **Campaign** | imCampaign | Distribution campaign linked to a subsidy program | - |
| **Campaign Input** | imCampaignInput | Inputs available in a campaign with allocation rules | imCampaign |
| **Campaign Dist Point** | imCampaignDistPt | Distribution points activated for a campaign | imCampaign |
| **Entitlement** | imEntitlement | Farmer's entitlement record for a campaign | imCampaign |
| **Entitlement Item** | imEntitlementItem | Individual input items within an entitlement | imEntitlement |
| **Distribution** | imDistribution | Distribution transaction record | imEntitlement |
| **Distribution Item** | imDistribItem | Individual items in a distribution transaction | imDistribution |
| **Agro-Dealer** | imAgroDealer | Registered agro-dealers in distribution network | - |

#### 4.2.2 Master Data Entities

| Entity | Table Name | Description | Key Columns |
|--------|------------|-------------|-------------|
| **Input Category** | md38InputCategory | Categories of agricultural inputs | code, name, requiresLicense |
| **Campaign Type** | md39CampaignType | Types of distribution campaigns | code, name, typicalDuration |
| **Distribution Model** | md40DistribModel | Models for input distribution | code, name, requiresVoucher |
| **Allocation Basis** | md41AllocBasis | Basis for calculating allocations | code, name, formula |
| **Target Category** | md42TargetCategory | Farmer target categories | code, name, priorityWeight |
| **Dealer Category** | md43DealerCategory | Categories of agro-dealers | code, name, commissionRatePct |
| **Input** | md44Input | Agricultural inputs catalog | code, name, categoryCode, unitOfMeasure |
| **Distribution Point** | md45DistribPoint | Physical distribution locations | code, name, districtCode, pointType |
| **Input Package** | md46InputPackage | Pre-defined input packages | code, name, packageValue |
| **Package Content** | md47PackageContent | Contents of input packages | packageCode, inputCode, quantity |

---

## 5. Process Flows

### 5.1 End-to-End Process

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         END-TO-END INPUT DISTRIBUTION                       │
└─────────────────────────────────────────────────────────────────────────────┘

  SUBSIDY PROGRAM MODULE                      IMM MODULE
  ═════════════════════                       ══════════════════════════════

  ┌───────────────────┐
  │ 1. Design Program │
  │    with Eligibility│
  │    Rules          │
  └─────────┬─────────┘
            │
            ▼
  ┌───────────────────┐
  │ 2. Farmers Apply  │
  │    for Program    │
  └─────────┬─────────┘
            │
            ▼
  ┌───────────────────┐
  │ 3. Evaluate       │
  │    Eligibility    │
  │    (Rules Engine) │
  └─────────┬─────────┘
            │
            ▼
  ┌───────────────────┐
  │ 4. Approve/Reject │
  │    Applications   │
  └─────────┬─────────┘
            │
            │ Approved Applications
            │ (status='APPROVED')
            │
════════════════════════════════════════════════════════════════════════════════
                              ELIGIBILITY BOUNDARY
════════════════════════════════════════════════════════════════════════════════
            │
            │                             ┌───────────────────┐
            │                             │ 5. Create Campaign│
            │                             │    - Link to      │
            │                             │      Program      │
            │                             │    - Set Timeline │
            │                             │    - Set Budget   │
            │                             └─────────┬─────────┘
            │                                       │
            │                                       ▼
            │                             ┌───────────────────┐
            │                             │ 6. Configure      │
            │                             │    Campaign       │
            │                             │    - Add Inputs   │
            │                             │    - Add Dist Pts │
            │                             └─────────┬─────────┘
            │                                       │
            │                                       ▼
            │                             ┌───────────────────┐
            └────────────────────────────►│ 7. Generate       │
                                          │    Entitlements   │
                                          │    (FROM approved │
                                          │    applications)  │
                                          └─────────┬─────────┘
                                                    │
                                                    ▼
                                          ┌───────────────────┐
                                          │ 8. Issue Vouchers │
                                          │    (if e-voucher  │
                                          │    model)         │
                                          └─────────┬─────────┘
                                                    │
                                                    ▼
                                          ┌───────────────────┐
                                          │ 9. Notify Farmers │
                                          │    (SMS/email)    │
                                          └─────────┬─────────┘
                                                    │
                                                    ▼
                                          ┌───────────────────┐
                                          │ 10. Execute       │
                                          │     Distribution  │
                                          │     - Verify ID   │
                                          │     - Record Items│
                                          │     - Capture     │
                                          │       Evidence    │
                                          └─────────┬─────────┘
                                                    │
                                                    ▼
                                          ┌───────────────────┐
                                          │ 11. Reconcile &   │
                                          │     Report        │
                                          └───────────────────┘
```

### 5.2 Campaign Creation Process

```
┌──────────────────────────────────────────────────────────────────────────┐
│                       CAMPAIGN CREATION PROCESS                          │
└──────────────────────────────────────────────────────────────────────────┘

  Program Officer                          System
  ═══════════════                          ══════════════════════════════

  ┌───────────────────┐
  │ Select "Create    │
  │ New Campaign"     │
  └─────────┬─────────┘
            │
            ▼                              ┌───────────────────────────────┐
  ┌───────────────────┐                    │ Validate: Only ACTIVE        │
  │ Select Linked     │───────────────────►│ programs available           │
  │ Subsidy Program   │                    │                               │
  │ (MANDATORY)       │◄───────────────────│ Display: Program details      │
  └─────────┬─────────┘                    │          Budget available     │
            │                              │          Approved applicants  │
            │                              └───────────────────────────────┘
            ▼
  ┌───────────────────┐
  │ Enter Campaign    │
  │ Basic Info        │
  │ - Name            │
  │ - Type            │
  │ - Description     │
  └─────────┬─────────┘
            │
            ▼
  ┌───────────────────┐
  │ Set Timeline      │
  │ - Start/End Date  │
  │ - Registration    │
  │ - Distribution    │
  └─────────┬─────────┘
            │
            ▼
  ┌───────────────────┐
  │ Set Budget &      │
  │ Distribution Model│
  │ - Total Budget    │
  │ - Model Type      │
  │ - Verification    │
  └─────────┬─────────┘
            │
            ▼
  ┌───────────────────┐
  │ Add Campaign      │                    ┌───────────────────────────────┐
  │ Inputs            │───────────────────►│ Validate: Input exists in     │
  │ (via FormGrid)    │                    │ md44Input, calculate totals   │
  └─────────┬─────────┘                    └───────────────────────────────┘
            │
            ▼
  ┌───────────────────┐
  │ Save Campaign     │                    ┌───────────────────────────────┐
  │ (Status: DRAFT)   │───────────────────►│ Campaign created with         │
  └─────────┬─────────┘                    │ status = DRAFT                │
            │                              └───────────────────────────────┘
            ▼
  ┌───────────────────┐
  │ Add Distribution  │                    ┌───────────────────────────────┐
  │ Points            │───────────────────►│ Managed via separate          │
  │ (Linked form)     │                    │ imCampaignDistPt form/list    │
  └─────────┬─────────┘                    └───────────────────────────────┘
            │
            ▼
  ┌───────────────────┐                    ┌───────────────────────────────┐
  │ Submit for        │───────────────────►│ Status → PENDING_APPROVAL     │
  │ Approval          │                    │ Workflow triggered            │
  └───────────────────┘                    └───────────────────────────────┘
```

### 5.3 Entitlement Generation Process

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    ENTITLEMENT GENERATION PROCESS                        │
│         (Executed after Campaign is APPROVED and ACTIVE)                 │
└──────────────────────────────────────────────────────────────────────────┘

  Trigger: Campaign status changes to ACTIVE
           OR Manual batch generation initiated

                    ┌───────────────────────────────────────────────────┐
                    │              BATCH GENERATION LOGIC               │
                    └───────────────────────────────────────────────────┘
                                          │
                                          ▼
                    ┌─────────────────────────────────────────────────┐
                    │ 1. Get Campaign Details                         │
                    │    - campaignId                                 │
                    │    - programId (linked program)                 │
                    │    - distributionModel                          │
                    │    - campaign inputs (imCampaignInput)          │
                    └─────────────────────────────────────────────────┘
                                          │
                                          ▼
                    ┌─────────────────────────────────────────────────┐
                    │ 2. Query Approved Applications                  │
                    │                                                 │
                    │    SELECT * FROM application                    │
                    │    WHERE programId = :campaignProgramId         │
                    │      AND status = 'APPROVED'                    │
                    │      AND NOT EXISTS (                           │
                    │        SELECT 1 FROM imEntitlement              │
                    │        WHERE applicationId = application.id     │
                    │          AND campaignId = :campaignId           │
                    │      )                                          │
                    │                                                 │
                    │    NOTE: Only approved applications!            │
                    │          No eligibility re-evaluation!          │
                    └─────────────────────────────────────────────────┘
                                          │
                                          ▼
                    ┌─────────────────────────────────────────────────┐
                    │ 3. For Each Approved Application:               │
                    └─────────────────────────────────────────────────┘
                                          │
          ┌───────────────────────────────┼───────────────────────────────┐
          │                               │                               │
          ▼                               ▼                               ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│ 3a. Create          │     │ 3b. Assign          │     │ 3c. Calculate       │
│     imEntitlement   │     │     Distribution    │     │     Input           │
│                     │     │     Point           │     │     Quantities      │
│ - Copy farmerId     │     │                     │     │                     │
│ - Copy farmer       │     │ - Based on farmer   │     │ - Based on          │
│   details           │     │   location          │     │   allocation basis  │
│ - Link applicationId│     │ - Or nearest point  │     │ - And campaign      │
│ - Generate codes    │     │ - Or farmer choice  │     │   input rules       │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
          │                               │                               │
          └───────────────────────────────┼───────────────────────────────┘
                                          │
                                          ▼
                    ┌─────────────────────────────────────────────────┐
                    │ 4. Create imEntitlementItem Records             │
                    │    (one per input type in package/allocation)   │
                    │                                                 │
                    │    - inputCode                                  │
                    │    - qtyEntitled (based on allocation rules)    │
                    │    - subsidyAmount (calculated)                 │
                    │    - farmerContrib (calculated)                 │
                    │    - itemStatus = 'PENDING'                     │
                    └─────────────────────────────────────────────────┘
                                          │
                                          ▼
                    ┌─────────────────────────────────────────────────┐
                    │ 5. If E-Voucher Model:                          │
                    │    - Generate unique voucherCode                │
                    │    - Generate voucherPin                        │
                    │    - Set voucherExpiry                          │
                    │    - Status = 'VOUCHER_ISSUED'                  │
                    └─────────────────────────────────────────────────┘
                                          │
                                          ▼
                    ┌─────────────────────────────────────────────────┐
                    │ 6. Send Notification to Farmer                  │
                    │    - SMS with collection details                │
                    │    - Include voucher code (if applicable)       │
                    │    - Distribution point and schedule            │
                    └─────────────────────────────────────────────────┘
```

### 5.4 Distribution Execution Process

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     DISTRIBUTION EXECUTION PROCESS                       │
└──────────────────────────────────────────────────────────────────────────┘

  Distribution Officer                     System
  ════════════════════                     ═══════════════════════════════

  ┌───────────────────┐
  │ Open Distribution │
  │ Form              │
  └─────────┬─────────┘
            │
            ▼
  ┌───────────────────┐
  │ Select Active     │                    ┌───────────────────────────────┐
  │ Campaign          │───────────────────►│ Filter: status = 'ACTIVE'     │
  └─────────┬─────────┘                    │ AND current date within       │
            │                              │ distribution period           │
            │                              └───────────────────────────────┘
            ▼
  ┌───────────────────┐                    ┌───────────────────────────────┐
  │ Search Farmer     │                    │ VALIDATION 1:                 │
  │ - By National ID  │───────────────────►│ Check entitlement exists      │
  │ - By Voucher Code │                    │ for this farmer + campaign    │
  │ - By Name         │◄───────────────────│                               │
  └─────────┬─────────┘                    │ If NO entitlement:            │
            │                              │ → STOP: "No entitlement found.│
            │                              │   Farmer may not have approved│
            │                              │   application for linked      │
            │                              │   program."                   │
            │                              └───────────────────────────────┘
            ▼
  ┌───────────────────┐                    ┌───────────────────────────────┐
  │ System displays   │◄───────────────────│ VALIDATION 2:                 │
  │ - Farmer details  │                    │ Check entitlement status      │
  │ - Entitlement     │                    │ is not COMPLETE, EXPIRED,     │
  │   items           │                    │ or CANCELLED                  │
  │ - Remaining       │                    │                               │
  │   quantities      │                    │ If invalid status:            │
  └─────────┬─────────┘                    │ → STOP with reason            │
            │                              └───────────────────────────────┘
            ▼
  ┌───────────────────┐                    ┌───────────────────────────────┐
  │ Verify Farmer     │                    │ VALIDATION 3:                 │
  │ Identity          │───────────────────►│ Match verification method     │
  │ - National ID     │                    │ to campaign requirements      │
  │ - Biometric       │                    │                               │
  │ - Voucher + PIN   │◄───────────────────│ Record verification result    │
  └─────────┬─────────┘                    └───────────────────────────────┘
            │
            ▼
  ┌───────────────────┐
  │ If Proxy:         │                    ┌───────────────────────────────┐
  │ - Record proxy    │───────────────────►│ VALIDATION 4:                 │
  │   details         │                    │ Check campaign allows proxy   │
  │ - Capture auth    │                    │ collection                    │
  │   document        │                    └───────────────────────────────┘
  └─────────┬─────────┘
            │
            ▼
  ┌───────────────────┐                    ┌───────────────────────────────┐
  │ Enter Items       │                    │ VALIDATION 5:                 │
  │ Distributed       │───────────────────►│ - Quantity ≤ remaining        │
  │ (FormGrid)        │                    │   entitlement                 │
  │ - Input           │◄───────────────────│ - Input available in          │
  │ - Quantity        │                    │   campaign                    │
  │ - Batch Number    │                    │ - Calculate subsidy/payment   │
  └─────────┬─────────┘                    └───────────────────────────────┘
            │
            ▼
  ┌───────────────────┐
  │ Record Payment    │
  │ (if applicable)   │
  │ - Method          │
  │ - Amount          │
  │ - Reference       │
  └─────────┬─────────┘
            │
            ▼
  ┌───────────────────┐
  │ Capture Evidence  │
  │ - Signature       │
  │ - Photo           │
  │ - GPS coordinates │
  └─────────┬─────────┘
            │
            ▼
  ┌───────────────────┐                    ┌───────────────────────────────┐
  │ Submit            │───────────────────►│ - Create imDistribution       │
  │ Distribution      │                    │ - Create imDistribItem(s)     │
  │                   │                    │ - Update imEntitlementItem    │
  │                   │                    │   quantities redeemed         │
  │                   │                    │ - Update imEntitlement status │
  │                   │◄───────────────────│ - Generate receipt            │
  └───────────────────┘                    └───────────────────────────────┘
```

---

## 6. Validation Rules

### 6.1 What IMM Validates (Operational Checks)

| # | Validation | When | Error Message |
|---|------------|------|---------------|
| V1 | Farmer has entitlement for campaign | Distribution | "No entitlement found. Farmer may not have an approved application for the linked program." |
| V2 | Entitlement status is valid | Distribution | "Entitlement is [COMPLETE/EXPIRED/CANCELLED] and cannot be used." |
| V3 | Voucher not expired | Distribution (e-voucher) | "Voucher expired on [date]. Please contact program office." |
| V4 | Remaining quantity available | Distribution | "Insufficient entitlement. Requested: X, Available: Y" |
| V5 | Distribution point valid for campaign | Distribution | "This distribution point is not activated for this campaign." |
| V6 | Campaign is active | Distribution | "Campaign is not active. Current status: [status]" |
| V7 | Within distribution period | Distribution | "Distribution period is [start] to [end]. Current date outside range." |
| V8 | Input available in campaign | Distribution | "Input [code] is not available in this campaign." |
| V9 | Proxy allowed (if proxy collection) | Distribution | "This campaign does not allow proxy collection." |
| V10 | Campaign linked to active program | Campaign creation | "Selected program is not active." |

### 6.2 What IMM Does NOT Validate (Eligibility - Subsidy Program Responsibility)

| # | NOT Validated by IMM | Responsibility |
|---|----------------------|----------------|
| ❌ | Farmer meets land size criteria | Subsidy Program |
| ❌ | Farmer meets income threshold | Subsidy Program |
| ❌ | Farmer is in target district | Subsidy Program |
| ❌ | Farmer is in target category | Subsidy Program |
| ❌ | Farmer has required crops/livestock | Subsidy Program |
| ❌ | Farmer passes any eligibility rule | Subsidy Program |
| ❌ | Farmer should receive support | Subsidy Program |

**The IMM principle is simple**: If the farmer has an approved application for the linked program, they are entitled to participate in the campaign. The approval decision was already made by the Subsidy Program Module.

---

## 7. Form Specifications Summary

### 7.1 Transactional Forms

| Form ID | Name | Table | Parent | Embedded Grid | Notes |
|---------|------|-------|--------|---------------|-------|
| imCampaign | Campaign Management | imCampaign | - | imCampaignInput | Main campaign form, 7 pages |
| imCampaignInput | Campaign Input | imCampaignInput | imCampaign | - | Embedded in imCampaign |
| imCampaignDistPt | Campaign Distribution Point | imCampaignDistPt | imCampaign | - | Linked form (separate CRUD) |
| imEntitlement | Farmer Entitlement | imEntitlement | - | imEntitlementItem | Readonly grid |
| imEntitlementItem | Entitlement Item | imEntitlementItem | imEntitlement | - | Embedded readonly |
| imDistribution | Input Distribution | imDistribution | - | imDistribItem | Distribution transaction |
| imDistribItem | Distribution Item | imDistribItem | imDistribution | - | Embedded in imDistribution |
| imAgroDealer | Agro-Dealer Registration | imAgroDealer | - | - | Standalone |

### 7.2 MDM Forms

| Form ID | Name | Table | Key Columns |
|---------|------|-------|-------------|
| md38InputCategory | Input Category | md38InputCategory | code, name |
| md39CampaignType | Campaign Type | md39CampaignType | code, name |
| md40DistribModel | Distribution Model | md40DistribModel | code, name |
| md41AllocBasis | Allocation Basis | md41AllocBasis | code, name, formula |
| md42TargetCategory | Target Category | md42TargetCategory | code, name |
| md43DealerCategory | Dealer Category | md43DealerCategory | code, name |
| md44Input | Input | md44Input | code, name, categoryCode |
| md45DistribPoint | Distribution Point | md45DistribPoint | code, name, districtCode |
| md46InputPackage | Input Package | md46InputPackage | code, name |
| md47PackageContent | Package Content | md47PackageContent | packageCode, inputCode |

---

## 8. Integration Points

### 8.1 Upstream Dependencies (IMM Consumes)

| Source Module | Entity | Usage in IMM | Integration Type |
|---------------|--------|--------------|------------------|
| Subsidy Program | program | Link campaign to program | FK reference |
| Subsidy Program | application | Generate entitlements from approved | Query |
| Farmer Registration | farmer | Copy farmer details to entitlement | FK + copy |
| MDM | mdDistrict | Filter distribution points | Lookup |
| MDM | All md* tables | Lookups throughout IMM | Lookup |

### 8.2 Downstream Consumers (IMM Provides)

| Consumer Module | Entity | Purpose |
|-----------------|--------|---------|
| Reporting | imDistribution | Distribution reports |
| Finance | imDistribution | Payment reconciliation |
| Inventory | imDistribItem | Stock management |
| Notifications | imEntitlement | SMS/email triggers |

### 8.3 Key SQL Queries

#### Query 1: Get Eligible Farmers for Entitlement Generation

```sql
-- Farmers with approved applications who don't yet have entitlements
SELECT 
    a.id AS applicationId,
    a.farmerId,
    f.nationalId,
    f.fullName,
    f.districtCode,
    f.phone
FROM application a
JOIN farmer f ON a.farmerId = f.id
WHERE a.programId = :campaignProgramId
  AND a.status = 'APPROVED'
  AND NOT EXISTS (
    SELECT 1 FROM imEntitlement e 
    WHERE e.applicationId = a.id 
      AND e.campaignId = :campaignId
  )
```

#### Query 2: Validate Farmer Can Receive Distribution

```sql
-- Check farmer has valid entitlement for distribution
SELECT 
    e.id AS entitlementId,
    e.entitlementCode,
    e.status,
    e.voucherCode,
    e.voucherExpiry,
    e.distPointCode,
    c.campaignName,
    c.status AS campaignStatus,
    c.distributionStart,
    c.distributionEnd
FROM imEntitlement e
JOIN imCampaign c ON e.campaignId = c.id
WHERE e.farmerId = :farmerId
  AND e.campaignId = :campaignId
  AND e.status IN ('APPROVED', 'VOUCHER_ISSUED', 'READY', 'PARTIAL')
  AND c.status = 'ACTIVE'
  AND CURRENT_DATE BETWEEN c.distributionStart AND c.distributionEnd
```

---

## 9. Status Workflows

### 9.1 Campaign Status

```
    ┌────────┐
    │ DRAFT  │ ───────► Created, being configured
    └────┬───┘
         │ Submit
         ▼
┌─────────────────┐
│PENDING_APPROVAL │ ───────► Awaiting approval
└────────┬────────┘
         │ Approve          │ Reject
         ▼                  ▼
    ┌─────────┐        ┌──────────┐
    │APPROVED │        │ REJECTED │
    └────┬────┘        └──────────┘
         │ Activate (start date reached)
         ▼
    ┌─────────┐
    │ ACTIVE  │ ───────► Distribution ongoing
    └────┬────┘
         │ End date reached OR Manual close
         ▼
    ┌──────────┐
    │ COMPLETE │ ───────► No more distributions
    └────┬─────┘
         │
         ▼
    ┌──────────┐
    │ ARCHIVED │ ───────► Historical record
    └──────────┘
```

### 9.2 Entitlement Status

```
    ┌────────────┐
    │ CALCULATED │ ───────► Generated from approved application
    └─────┬──────┘
          │ Batch approval
          ▼
    ┌────────────┐
    │  APPROVED  │ ───────► Ready for voucher/distribution
    └─────┬──────┘
          │ (If e-voucher model)
          ▼
┌─────────────────┐
│ VOUCHER_ISSUED  │ ───────► Voucher generated
└────────┬────────┘
         │ Voucher sent to farmer
         ▼
    ┌─────────┐
    │  READY  │ ───────► Ready for collection
    └────┬────┘
         │ First partial redemption
         ▼
    ┌─────────┐
    │ PARTIAL │ ───────► Some items collected
    └────┬────┘
         │ All items collected
         ▼
    ┌──────────┐
    │ COMPLETE │ ───────► Fully redeemed
    └──────────┘

Alternative end states:
    ┌─────────┐
    │ EXPIRED │ ───────► Voucher/entitlement expired
    └─────────┘
    ┌───────────┐
    │ CANCELLED │ ───────► Manually cancelled
    └───────────┘
```

### 9.3 Distribution Status

```
    ┌───────────┐
    │ COMPLETED │ ───────► Normal completion
    └───────────┘

    ┌──────────┐
    │ REVERSED │ ───────► Transaction reversed (stock returned)
    └──────────┘

    ┌──────────┐
    │ DISPUTED │ ───────► Under investigation
    └──────────┘
```

---

## 10. Key Design Decisions

### 10.1 Campaign-Program Linkage is Mandatory

**Decision**: Every campaign MUST be linked to a subsidy program.

**Rationale**: 
- Ensures all distributions are tied to an approved program
- Eligibility has been pre-determined by the program
- Budget accountability is maintained
- Prevents orphan distributions

**Implementation**: `programId` field in `imCampaign` is required.

### 10.2 Entitlements Generated from Approved Applications Only

**Decision**: Entitlements can ONLY be created for farmers with approved applications for the linked program.

**Rationale**:
- Maintains separation of concerns
- Eligibility decision already made
- Prevents bypassing program rules
- Clear audit trail

**Implementation**: Entitlement generation queries `application` table filtering on `status = 'APPROVED'` and matching `programId`.

### 10.3 No Eligibility Rules in IMM

**Decision**: IMM contains NO eligibility rule definitions, evaluation logic, or eligibility checking.

**Rationale**:
- Single source of truth (Subsidy Program Module)
- Avoid rule duplication and drift
- Clear responsibility boundaries
- Align with WFP SCOPE model

**Implementation**: 
- Remove `targetCategories`, `eligibilityRules` fields from `imCampaign`
- Remove any eligibility-related validation from IMM
- Replace with simple "has approved application" check

### 10.4 Distribution Points Managed Separately

**Decision**: `imCampaignDistPt` is a linked form, not embedded in `imCampaign`.

**Rationale**:
- Campaign may have many distribution points
- FormGrid unsuitable for long lists
- Need advanced filtering/searching
- Points can be added/modified after campaign creation

**Implementation**: Separate CRUD form with `campaignId` FK, managed via datalist.

---

## 11. Glossary

| Term | Definition |
|------|------------|
| **Campaign** | A time-bound distribution initiative linked to a subsidy program |
| **Entitlement** | A farmer's calculated right to receive specific inputs from a campaign |
| **Distribution** | The actual transaction of providing inputs to a farmer |
| **Redemption** | The act of collecting entitled inputs (full or partial) |
| **Voucher** | An electronic or physical token representing entitlement value |
| **Allocation Basis** | The method used to calculate input quantities (per hectare, per farmer, etc.) |
| **Distribution Point** | A physical location where farmers collect inputs |
| **Agro-Dealer** | A private sector partner selling subsidized inputs to farmers |

---

## 12. Appendices

### Appendix A: Field Reference for imCampaign (Revised)

The following fields should be **REMOVED** from `imCampaign.yaml` as they belong to Subsidy Program:

```yaml
# REMOVE these fields - eligibility is Subsidy Program responsibility
- id: targetCategories      # REMOVE
- id: eligibilityRules      # REMOVE  
- id: excludeRepeatBenef    # REMOVE
- id: repeatLimitCampaigns  # REMOVE
```

The `programId` field should be made **REQUIRED**:

```yaml
- id: programId
  label: Linked Subsidy Program
  type: selectBox
  required: true  # CHANGED from optional to required
  optionsSource:
    type: formData
    formId: program
    valueColumn: id
    labelColumn: programName
    extraCondition: "c_status = 'ACTIVE'"
    addEmptyOption: true
    emptyLabel: "-- Select Program --"
```

### Appendix B: Revised imEntitlement Fields

Add `applicationId` as mandatory link to approved application:

```yaml
- id: applicationId
  label: Approved Application
  type: hiddenField
  required: true
  # Populated during entitlement generation
  # Links to application.id where status = 'APPROVED'
```

### Appendix C: Sample Entitlement Generation Process (Pseudocode)

```java
public void generateEntitlements(String campaignId) {
    // 1. Get campaign details
    Campaign campaign = campaignDao.findById(campaignId);
    String programId = campaign.getProgramId();
    
    if (programId == null) {
        throw new BusinessException("Campaign must be linked to a program");
    }
    
    // 2. Get approved applications for the linked program
    // NOTE: Only approved applications - no eligibility re-evaluation!
    List<Application> approvedApps = applicationDao.findByProgramAndStatus(
        programId, 
        ApplicationStatus.APPROVED
    );
    
    // 3. Filter out those who already have entitlements
    List<Application> pendingApps = approvedApps.stream()
        .filter(app -> !entitlementDao.existsByCampaignAndApplication(
            campaignId, app.getId()))
        .collect(Collectors.toList());
    
    // 4. Generate entitlements
    for (Application app : pendingApps) {
        Entitlement entitlement = new Entitlement();
        entitlement.setCampaignId(campaignId);
        entitlement.setApplicationId(app.getId());  // Link to approved app
        entitlement.setFarmerId(app.getFarmerId());
        entitlement.setStatus(EntitlementStatus.CALCULATED);
        
        // Copy farmer details for denormalization
        Farmer farmer = farmerDao.findById(app.getFarmerId());
        entitlement.setFarmerNationalId(farmer.getNationalId());
        entitlement.setFarmerName(farmer.getFullName());
        
        // Assign distribution point
        entitlement.setDistPointCode(
            assignDistributionPoint(farmer, campaign));
        
        // Calculate entitlement items
        List<EntitlementItem> items = calculateItems(campaign, farmer);
        entitlement.setItems(items);
        
        // Calculate totals
        entitlement.setTotalEntitleValue(sumItemValues(items));
        entitlement.setTotalSubsidyValue(sumSubsidies(items));
        
        // Generate voucher if e-voucher model
        if (campaign.getDistributionModel().equals("EVOUCHER")) {
            generateVoucher(entitlement, campaign);
        }
        
        entitlementDao.save(entitlement);
        
        // Notify farmer
        notificationService.sendEntitlementNotification(entitlement);
    }
}
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2024 | FRS Team | Initial version |

---

*End of Document*
