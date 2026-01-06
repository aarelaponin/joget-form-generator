# FRS - Form Model

**Module:** Farmer Registration System
**Last Updated:** 2026-01-06

## Entities

| Form ID | Form Name | Component | Description |
|---------|-----------|-----------|-------------|
| frFarmer | Farmer Registration | farm | Core farmer entity with personal data |
| frParcel | Land Parcel | parcel | Farmer's land holdings |

## Relationships

| Parent | Child | Type | FK Field | Description |
|--------|-------|------|----------|-------------|
| frFarmer | frParcel | 1:N | farmerId | One farmer owns multiple parcels |
| md03district | frFarmer | N:1 | districtId | Farmer's district (lookup) |
| md03district | frParcel | N:1 | districtId | Parcel's district (lookup) |

## MDM Dependencies

| MDM Form | Used By | Field | Purpose |
|----------|---------|-------|---------|
| md01maritalStatus | frFarmer | maritalStatusId | Marital status lookup |
| md02language | frFarmer | languageId | Preferred language |
| md03district | frFarmer, frParcel | districtId | Administrative district |
| md08educationLevel | frFarmer | educationLevelId | Education level |
| md19crops | frParcel | cropIds | Crops grown on parcel |
| md16livestockType | frFarmer | livestockTypeIds | Livestock owned |

## Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         MDM (Lookups)                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │md03      │ │md19crops │ │md16      │ │md01-08   │           │
│  │district  │ │          │ │livestock │ │(other)   │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
        ▼            │            │            ▼
┌───────────────┐    │            │    ┌───────────────┐
│   frFarmer    │◄───┼────────────┘    │   (lookups)   │
│               │    │                 └───────────────┘
│ - farmerId(PK)│    │
│ - nrc         │    │
│ - firstName   │    │
│ - lastName    │    │
│ - districtId  │    │
│ - ...         │    │
└───────┬───────┘    │
        │            │
        │ 1:N        │
        ▼            ▼
┌───────────────────────┐
│      frParcel         │
│                       │
│ - parcelId (PK)       │
│ - farmerId (FK)       │◄─── Links to frFarmer
│ - parcelName          │
│ - districtId          │
│ - size                │
│ - cropIds             │◄─── Links to md19crops
│ - gisCoordinates      │◄─── From GIS integration
│ - ...                 │
└───────────────────────┘
```

## GIS Integration Points

| Form | Field | GIS Feature | Description |
|------|-------|-------------|-------------|
| frParcel | gisCoordinates | Point/Polygon capture | Parcel boundary or centroid |
| frParcel | gisArea | Calculated | Area from polygon (if available) |

## Notes

- The old farmer form (archived in `_archive/`) embedded land data directly
- New design separates farmer and parcel for 1:N support
- GIS integration is optional; forms work without it
