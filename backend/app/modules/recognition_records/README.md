# Recognition Records Module

## Purpose

Stores face recognition event logs received from devices — access attempts, alarms, and recognition data.

## Key Files

- `models.py` — RecognitionRecord model
- `schemas.py` — Pydantic schemas for record CRUD
- `service.py` — Database operations for records
- `router.py` — Record management endpoints

## API Endpoints

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET | `/` | `list_records()` | List records with optional device_id filter |
| GET | `/{record_id}` | `get_record()` | Get record by ID |
| POST | `/` | `create_record()` | Create record (usually via callback) |
| PUT | `/{record_id}` | `update_record()` | Update record |
| DELETE | `/{record_id}` | `delete_record()` | Delete record |

## End-to-End Flow

```
1. Device recognizes face:
   POST /api/v1/callbacks/identify
   → Creates RecognitionRecord with person_id, event_time, img_data

2. Admin views records:
   GET /api/v1/record/ → Lists records with pagination

3. Record deleted:
   DELETE /api/v1/record/{id} → Removes record from DB
```

## Record Data

- `device_id` — Device that captured the event
- `person_id_internal` — Internal personnel UUID
- `person_id_device` — Device-specific person ID
- `record_type` — face / card / face&card
- `event_type` — normal / alarm
- `event_name` — identify / illegal_access / etc.
- `event_time` — Timestamp of recognition
- `img_data` — Base64 on-site photo

## Related Modules

- `device` — Source device for records
- `personnel` — Personnel recognized in records
