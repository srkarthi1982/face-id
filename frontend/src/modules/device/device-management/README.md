# Device / Device Management Feature

## Purpose

Device management view — displays all Face ID devices with management actions.

## Key Files

- `DeviceManagementPage.tsx` — Device list component
- `manifest.ts` — Feature manifest

## Store

None — uses `api.ts` functions from parent module.

## Pages

| Page | Path | Description |
|------|------|-------------|
| DeviceManagementPage | `/device/device-management` | Device list with CRUD |

## End-to-End Flow

```
1. Admin views devices:
   → DeviceManagementPage loads
   → listDevices() → GET /api/v1/device/endpoint/

2. Admin adds device:
   → Opens add modal
   → addDevice() → POST /api/v1/device/endpoint/

3. Admin edits device:
   → Opens edit modal
   → editDevice() → PUT /api/v1/device/endpoint/{id}/

4. Admin deletes device:
   → Opens delete confirmation
   → removeDevice() → DELETE /api/v1/device/endpoint/{id}/

5. Admin refreshes device:
   → refreshDevice() → POST /api/v1/device/endpoint/{id}/refresh

6. Admin discovers devices:
   → Opens discover modal
   → scanDevices() → POST /api/v1/device/setup/discover
   → saveDevice() → POST /api/v1/device/setup/connect
```

## Related Features

- Parent module: `device`
