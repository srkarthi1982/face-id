# Callbacks Module

## Purpose

Manages callback configurations for devices — defines which callback URLs are registered on each device.

## Key Files

- `models.py` — CallbackConfig model
- `schemas.py` — Pydantic schemas for config CRUD
- `service.py` — Database operations for configs
- `router.py` — Callback config endpoints

## API Endpoints

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET | `/` | `list_configs()` | List configs with optional device_id filter |
| GET | `/{config_id}` | `get_config()` | Get config by ID |
| POST | `/` | `create_config()` | Create callback config |
| PUT | `/{config_id}` | `update_config()` | Update callback config |
| DELETE | `/{config_id}` | `delete_config()` | Delete callback config |

## Callback Types

| Type | Device API | Description |
|------|------------|-------------|
| heartbeat | `/device/setDeviceHeartBeat` | Device online status |
| identify | `/device/setIdentifyCallBack` | Face/card recognition |
| photo_registration | `/device/setImgRegCallBack` | Photo registered on device |
| card_registration | `/device/setCardRegCallBack` | Card registered on device |
| event | `/device/setEvent` | Alarm/event triggered |
| qrcode | `/device/setQRCodeCallback` | QR code scanned |
| registration_info | `/device/setRegistCallback` | Registration completed |
| finger_reg | `/device/setFingerRegCallback` | Fingerprint enrolled |
| task_result | `setTaskInterfaceAddress` | Async task completed |

## End-to-End Flow

```
1. Admin creates callback config:
   POST /api/v1/callback/ → Creates CallbackConfig

2. Device pushes callback (Phase 2):
   POST /api/v1/callbacks/{type} → Validates deviceKey → Routes to handler

3. Handler processes callback:
   → Updates device status (heartbeat)
   → Creates recognition record (identify)
   → Updates photo with face_id (photo_reg)
```

## Related Modules

- `device` — Devices sending callbacks
- `recognition_records` — Created from identify callbacks
- `photos` — Updated from photo_reg callbacks
