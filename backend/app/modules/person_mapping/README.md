# Person Mapping Module

## Purpose

Manages device-person mappings — tracks which personnel are registered on which devices and their device-specific IDs.

## Key Files

- `models.py` — DevicePersonMapping model
- `schemas.py` — Pydantic schemas for mapping CRUD
- `service.py` — Database operations for mappings
- `router.py` — Mapping management endpoints

## API Endpoints

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET | `/` | `list_mappings()` | List mappings with optional device_id filter |
| GET | `/{mapping_id}` | `get_mapping()` | Get mapping by ID |
| POST | `/` | `create_mapping()` | Create device-person mapping |
| PUT | `/{mapping_id}` | `update_mapping()` | Update mapping |
| DELETE | `/{mapping_id}` | `delete_mapping()` | Delete mapping |

## End-to-End Flow

```
1. Personnel pushed to device (Phase 2):
   Backend → DeviceHttpClient → POST /device/person/create
   → Creates device_person_mapping with device-specific person_id

2. Recognition event received:
   POST /api/v1/callbacks/identify
   → Uses person_mapping to map device person_id to internal personnel.id

3. Personnel removed from device:
   Backend → DeviceHttpClient → POST /device/person/delete
   → Deletes device_person_mapping
```

## Mapping Strategy

- Internal UUID (`person_id_internal`) is constant across all devices
- Device-specific ID (`person_id_device`) varies per device
- `photo_ids` JSON array stores face IDs registered on each device

## Related Modules

- `device` — Devices that have person mappings
- `personnel` — Personnel linked via mapping
- `photos` — Photos tracked in mapping
