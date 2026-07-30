# Device Module

## Purpose

Manages Face ID hardware devices — registration, configuration, status tracking, LAN discovery, and connectivity.

## Key Files

- `models.py` — Device model
- `schemas.py` — Pydantic schemas for device CRUD
- `service.py` — Database operations for devices
- `router.py` — Device management endpoints

## API Endpoints

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET | `/endpoint/` | `list_endpoints()` | List devices with filters |
| GET | `/endpoint/{device_id}` | `get_endpoint()` | Get device by ID |
| POST | `/endpoint/` | `create_endpoint()` | Register new device |
| PUT | `/endpoint/{device_id}` | `update_endpoint()` | Update device settings |
| DELETE | `/endpoint/{device_id}` | `delete_endpoint()` | Remove device |
| POST | `/endpoint/{device_id}/refresh` | `refresh_endpoint()` | Refresh device status |
| POST | `/setup/connect` | `connect_device()` | Connect new device |
| POST | `/setup/discover` | `discover_devices_endpoint()` | Discover devices on subnet |

## End-to-End Flow

```
1. Admin registers device:
   POST /api/v1/device/endpoint/ → Creates device record

2. Device sends heartbeat (Phase 2):
   POST /api/v1/callbacks/heartbeat → Updates device status to "online"

3. Admin refreshes device status:
   POST /api/v1/device/endpoint/{id}/refresh → Pings device via DeviceHttpClient

4. LAN discovery (Phase 2):
   POST /api/v1/device/setup/discover → Scans subnet for devices

5. Personnel sync to device (Phase 2):
   Backend → DeviceHttpClient → POST /device/person/create
```

## Device Communication (Phase 2)

- Backend communicates with devices on port 8090
- 109 device API endpoints via `DeviceHttpClient`
- Callbacks received at `/api/v1/callbacks/{type}`

## Related Modules

- `callbacks` — Receives device callbacks
- `person_mapping` — Device-person mappings
- `recognition_records` — Access logs from devices
