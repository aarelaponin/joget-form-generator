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

The parcel form uses the GIS Polygon Capture plugin for boundary capture.

**Reference:** `sample-forms/07_GIS/ui-form.json`

**Component:** `global.govstack.gisui.element.GisPolygonCaptureElement`

### GIS Fields in frParcel

| Field ID | Type | Description |
|----------|------|-------------|
| `geometry` | GisPolygonCapture | Polygon boundary (GeoJSON format) |
| `perimeter` | hiddenField | Auto-calculated perimeter (meters) |
| `centroid` | hiddenField | Auto-calculated center point |
| `vertexCount` | hiddenField | Auto-calculated vertex count |

### Key GIS Properties

| Property | Value | Description |
|----------|-------|-------------|
| `captureMode` | `BOTH` | Allow GPS walking or manual drawing |
| `gpsHighAccuracy` | `true` | Use high-accuracy GPS mode |
| `gpsMinAccuracy` | `10` | Minimum 10m GPS accuracy |
| `minAreaHectares` | `0.1` | Minimum parcel size |
| `maxAreaHectares` | `1000` | Maximum parcel size |
| `enableOverlapCheck` | `true` | Check for overlapping parcels |
| `overlapFormId` | `frParcel` | Form to check for overlaps |
| `overlapGeometryField` | `geometry` | Field containing geometry |

### Derived Fields Pattern

The GIS component auto-populates hidden fields:
```
GisPolygonCaptureElement
    │
    ├──► perimeter (hiddenField) - boundary length in meters
    ├──► centroid (hiddenField) - center point coordinates
    └──► vertexCount (hiddenField) - number of polygon points
```

## Notes

- The old farmer form (archived in `_archive/`) embedded land data directly
- New design separates farmer and parcel for 1:N support
- GIS integration is optional; forms work without it
- GIS plugin requires `joget-gis-ui` plugin to be installed in Joget
