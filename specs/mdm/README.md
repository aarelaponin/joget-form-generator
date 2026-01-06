# Existing MDM Forms Reference

This folder contains MDM (Master Data Management) form definitions exported from the **jdx4/farmersPortal** Joget instance.

## Structure

```
existing-mdm/
├── output/           # 50 MDM form JSON definitions
│   └── archive/      # Old files with deprecated naming conventions
├── data/             # CSV data files for MDM forms
└── input/            # Input specifications (if any)
```

## Forms Index (md01-md47)

| ID | Form ID | Name |
|----|---------|------|
| 01 | md01maritalStatus | Marital Status |
| 02 | md02language | Language |
| 03 | md03district | District |
| 04 | md04agroEcologicalZo | Agro Ecological Zone |
| 05 | md05residencyType | Residency Type |
| 06 | md06farmLabourSource | Farm Labour Source |
| 07 | md07livelihoodSource | Livelihood Source |
| 08 | md08educationLevel | Education Level |
| 09 | md09infoSource | Info Source |
| 10 | md10conservationPrac | Conservation Practice |
| 11 | md11hazard | Hazard |
| 12 | md12relationship | Relationship |
| 13 | md13orphanhoodStatus | Orphanhood Status |
| 14 | md14disabilityStatus | Disability Status |
| 15 | md15areaUnits | Area Units |
| 16 | md16livestockType | Livestock Type |
| 16.1 | md161livestockCategory | Livestock Category |
| 17 | md17incomeSource | Income Source |
| 18 | md18registrationChan | Registration Channel |
| 19 | md19crops | Crops |
| 19.1 | md191cropCategory | Crop Category |
| 20 | md20supportProgram | Support Program |
| 21 | md21programType | Program Type |
| 22 | md22applicationStatu | Application Status |
| 23 | md23documentType | Document Type |
| 24 | md24paymentMethod | Payment Method |
| 25 | md25equipCategory | Equipment Category |
| 25 | md25equipment | Equipment |
| 26 | md26trainingTopic | Training Topic |
| 27 | md27inputCategory | Input Category |
| 27 | md27input | Input |
| 28 | md28benefitModel | Benefit Model |
| 30 | md30targetGroup | Target Group |
| 31 | md31decisionType | Decision Type |
| 32 | md32rejectionReason | Rejection Reason |
| 33 | md33requestType | Request Type |
| 34 | md34notificationType | Notification Type |
| 35 | md35foodSecurityStat | Food Security Status |
| 36 | md36eligibilityOpera | Eligibility Operator |
| 37 | md37collectionPoint | Collection Point |
| 38 | md38InputCategory | Input Category (IMM) |
| 39 | md39CampaignType | Campaign Type |
| 40 | md40DistribModel | Distribution Model |
| 41 | md41AllocBasis | Allocation Basis |
| 42 | md42TargetCategory | Target Farmer Category |
| 43 | md43DealerCategory | Dealer Category |
| 44 | md44Input | Input Catalogue |
| 45 | md45DistribPoint | Distribution Point |
| 46 | md46InputPackage | Input Package |
| 47 | md47PackageContent | Package Content |

## Usage

These forms serve as reference implementations for:
- Understanding Joget DX form structure
- Validating form generator output
- Analyzing field patterns and configurations

## Source

Exported from: `jdx4` instance, `farmersPortal` application (v1)
Last updated: 2024-12-22
