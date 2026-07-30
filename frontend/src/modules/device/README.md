# Device Module

## Purpose

Face ID device management — register, configure, discover, and monitor devices on the network.

## Key Files

- `manifest.ts` — Module manifest
- `api.ts` — API functions for device operations
- `device-management/DeviceManagementPage.tsx` — Device list page
- `device-management/manifest.ts` — Feature manifest

## Store

None — uses local state and API functions directly from `api.ts`.

## Pages

| Page | Path | Description |
|------|------|-------------|
| RegisteredPage | `/device/registered` | Device list with CRUD operations |

## API Functions (from api.ts)

| Function | Purpose |
|----------|---------|
| `listDevices` | List registered devices |
| `addDevice` | Add new device |
| `editDevice` | Update device |
| `removeDevice` | Delete device |
| `refreshDevice` | Refresh device status |
| `saveDevice` | Connect/save device setup |
| `scanDevices` | Discover devices on subnet |

## Features

- Device list with sorting and filtering
- Add device manually or via subnet discovery
- Edit/delete devices
- Refresh device status
- Bulk connect discovered devices
- Pagination

## End-to-End Flow

```
1. Admin views device list:
   GET /api/v1/device/endpoint/ → Lists devices

2. Admin adds device manually:
   POST /api/v1/device/endpoint/ → Creates device

3. Admin discovers devices:
   POST /api/v1/device/setup/discover → Scans subnet
   → Returns discovered devices

4. Admin connects device:
   POST /api/v1/device/setup/connect → Registers device

5. Device heartbeat (Phase 2):
   POST /api/v1/callbacks/heartbeat → Updates device status
```

## Related Modules

- `callbacks` — Receives device callbacks
- `personnel` — Personnel registered on devices
