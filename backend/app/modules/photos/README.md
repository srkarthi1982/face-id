# Photos Module

## Purpose

Manages face photo registrations for personnel — stores face data, feature codes, and image data.

## Key Files

- `models.py` — PhotoRegistration model
- `schemas.py` — Pydantic schemas for photo CRUD
- `service.py` — Database operations for photos
- `router.py` — Photo management endpoints

## API Endpoints

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET | `/` | `list_photos()` | List photos with optional person_id filter |
| POST | `/upload` | `upload_photo()` | Upload image file (multipart/form-data) for a person |
| GET | `/{photo_id}` | `get_photo()` | Get photo metadata by ID |
| GET | `/{photo_id}/image` | `get_photo_image()` | Serve the stored image binary |
| POST | `/` | `create_photo()` | Register new face photo (JSON, img_data as base64) |
| PUT | `/{photo_id}` | `update_photo()` | Update photo record |
| DELETE | `/{photo_id}` | `delete_photo()` | Delete photo |

## Data Conventions

- `img_data` in JSON payloads is **base64**; it is stored as raw bytes and never returned in responses — responses expose `has_image` plus `GET /{photo_id}/image` instead.
- `img_content_type` records the MIME type (`image/jpeg` / `image/png`) used when serving the image.
- `device_id` is nullable: `NULL` means the person's **master photo** (uploaded via the UI, source for device sync); one row per (person, device) pair otherwise. `/upload` replaces the existing row for the same pair.
- Upload constraints: JPEG or PNG, max 5 MB.

## End-to-End Flow

```
1. Admin uploads face photo (Personnel page → Photo button):
   POST /api/v1/photo/upload (multipart) → Upserts master photo_registration (device_id NULL)

2. Photo pushed to device (Phase 2):
   Backend → DeviceHttpClient → POST /device/face/create

3. Device confirms registration (Phase 2):
   POST /api/v1/callbacks/photo_registration → Updates photo with device face_id

4. Personnel deleted:
   DELETE /api/v1/personnel/{id} → Cascade deletes photos
```

## Related Modules

- `personnel` — Personnel linked to photos
- `person_mapping` — Device-person photo mappings
