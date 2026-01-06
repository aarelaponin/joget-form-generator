# FRS - Farmer Registration System

**Module:** Farmer Registration System
**Last Updated:** 2026-01-06

## 1. Scope

The Farmer Registration System (FRS) manages the registration and profiling of farmers, including:
- Farmer personal and demographic information
- Land parcel registration (multiple parcels per farmer)
- GIS integration for parcel boundary capture
- Linkage to master data (districts, crops, livestock, etc.)

## 2. Actors

| Actor | Description |
|-------|-------------|
| Extension Officer | Registers farmers and captures land parcel data in the field |
| Farmer | Provides information, may view own registration status |
| Data Clerk | Back-office data entry and verification |
| System Administrator | Manages MDM, user access |

## 3. Business Rules

- BR-001: One farmer can own multiple land parcels (1:N relationship)
- BR-002: Each parcel must be linked to exactly one farmer
- BR-003: Parcel boundaries should be captured via GIS when available
- BR-004: Farmer NRC/ID number must be unique across the system
- BR-005: All farmers must have at least one registered parcel

## 4. Components

| Component | Description |
|-----------|-------------|
| `farm/` | Farmer personal data, demographics, contact information |
| `parcel/` | Land parcel data, location, size, GIS coordinates |

## 5. Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| `mdm/` | MDM Lookup | Districts, crops, livestock types, etc. |
| `gis/` | Integration | Parcel boundary capture, map display |

## 6. Out of Scope

- Farmer financial transactions (handled by SPM)
- Input distribution tracking (handled by IMM)
- Eligibility determination (handled by SPM)
