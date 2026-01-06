# FRS Changelog

All notable changes to the Farmer Registration System module are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/).
This module follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Module structure with `farm/` and `parcel/` components
- FRS_OVERVIEW.md - system specification
- FRS_FORM_MODEL.md - entity relationships

### Changed
- Restructured from single `farmer/` folder to `frs/` module with components
- Farmer-land relationship changed from embedded to 1:N (farmer → parcels)

### Archived
- Previous farmer forms moved to `_archive/` for reference

## [0.1.0] - 2025-12-17

### Added
- Initial farmer registration forms (f01-main through f01.07)
- Multi-page wizard structure
- Basic MDM lookups

---

## Migration Notes

### From farmer/ to frs/

The original `farmer/` implementation embedded land data directly in the farmer form.
The new `frs/` structure separates concerns:

| Old (farmer/) | New (frs/) |
|---------------|------------|
| Single form with land fields | frFarmer (personal) + frParcel (land) |
| 1:1 farmer:land | 1:N farmer:parcels |
| No GIS | GIS integration planned |

Archived forms in `_archive/output/` can be referenced for field mappings during migration.
