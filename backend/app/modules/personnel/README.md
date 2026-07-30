# Personnel Module

## Purpose

Manages personnel/employee records — stores person information, card numbers, ID numbers, and access permissions.

## Key Files

- `models.py` — Personnel model
- `schemas.py` — Pydantic schemas for personnel CRUD
- `service.py` — Database operations for personnel
- `router.py` — Personnel management endpoints

## API Endpoints

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET | `/` | `list_personnel()` | List personnel with filters |
| GET | `/{personnel_id}` | `get_personnel()` | Get personnel by ID |
| POST | `/` | `create_personnel()` | Create personnel record |
| PUT | `/{personnel_id}` | `update_personnel()` | Update personnel record |
| DELETE | `/{personnel_id}` | `delete_personnel()` | Delete personnel |
| PATCH | `/{personnel_id}/deactivate` | `deactivate_personnel()` | Deactivate personnel |
| PATCH | `/{personnel_id}/activate` | `activate_personnel()` | Activate personnel |
| POST | `/{personnel_id}/push` | `push_personnel_to_devices()` | Push personnel to devices via device `/person/create` |

## End-to-End Flow

```
1. Admin creates personnel:
   POST /api/v1/personnel/ → Creates personnel record

2. Personnel photo registered:
   POST /api/v1/photo/ → Creates photo_registration linked to personnel

3. Personnel pushed to device:
   POST /api/v1/personnel/{id}/push → DeviceHttpClient → device POST /person/create
   → Upserts device_person_mapping (synced_at, person_id_device, photo_ids)

4. Recognition event received:
   POST /api/v1/callbacks/identify → RecognitionRecord created

5. Personnel deactivated:
   PATCH /api/v1/personnel/{id}/deactivate → is_active=false
```

## Related Modules

- `photos` — Face photo registrations
- `person_mapping` — Device-person mappings
- `device` — Devices that recognize personnel
