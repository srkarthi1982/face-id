# Face ID Device Integration — Project Plan

## Objective

Integrate face ID hardware devices into the existing device management platform. Connect 100+ face recognition devices (supporting face, QR code, card, and fingerprint recognition) to the backend system via LAN API. Devices act as HTTP servers with inbound requests from the backend; devices push recognition events and status updates to backend callbacks for real-time reporting.

**Key principles:**
- Store user data (personnel, photos, records) in backend DB for reporting/dashboard
- Push personnel data to devices on demand (not pull)
- Device keeps its own recognition records; backend stores copies received via callbacks
- Validate device identity using `deviceKey` in callback payloads
- Use subnet-based LAN discovery for auto-detecting new devices

---

## Architecture

### High-Level Data Flow

```
┌─────────────┐    REST/HTTP    ┌──────────────────┐
│   Frontend   │◄──────────────►│                  │
│  (React/TS)  │   CRUD API     │  Backend API     │
│              │                │  (FastAPI)       │
└─────────────┘                └────────┬─────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
              │              INBOUND (device → backend)         │
              │                        │                        │
              │                        ▼                        │
              │              ┌──────────────────┐               │
              │              │ Callback Router   │ ← deviceKey │
              │              │ (auth validation) │ validation  │
              │              └────────┬─────────┘               │
              │                       │                         │
              │                       ▼                         │
              │              ┌──────────────────┐               │
              │              │ Service Layer     │ ← business   │
              │              │ + Mapping Logic   │   logic       │
              │              └────────┬─────────┘               │
              │                       │                         │
              │                       ▼                         │
              │              ┌──────────────────┐               │
              │              │   PostgreSQL      │               │
              │              └──────────────────┘               │
              │                                                 │
              │              OUTBOUND (backend → device)        │
              │              ┌──────────────────┐               │
              └─────────────►│ DeviceHttpClient  │ ─────────────┘
                             │ (device comms)   │   HTTP calls
                             └────────┬─────────┘           to :8090
                                      │                      │
                                      ▼                      ▼
                                ┌──────────────────────────────┐
                                │    Device (HTTP Server)       │
                                │        Port 8090              │
                                └──────────────────────────────┘

  Callback Routes:  /api/v1/callbacks/heartbeat | identify | photo_reg | card_reg
                    | event | qrcode | registration_info | finger_reg | task_result
```

All data flows strictly through backend layers — no direct device-to-DB connections.

### Module Structure

```
backend/
├── app/modules/device/                      # Device CRUD module
│   ├── models.py                            # SQLAlchemy models
│   ├── schemas.py                           # Pydantic schemas (NEW)
│   ├── crud.py                              # CRUD operations (NEW)
│   ├── router.py                            # REST API endpoints
│   └── services.py                          # Business logic (NEW)
│
├── app/modules/callbacks/                   # Callback config module (NEW)
│   ├── models.py
│   ├── schemas.py
│   ├── router.py
│   └── services.py
│
└── app/devices/                             # Device communication service (NEW)
    ├── client.py                            # HTTP client for device APIs (all 109 endpoints)
    ├── services.py                          # Sync & task orchestration
    ├── router.py                            # /api/v1/callbacks/ receivers
    └── handlers.py                          # Callback payload processors

frontend/
├── src/modules/device/                      # Device management UI
│   ├── api.ts                               # API calls (extended)
│   ├── manifest.ts                          # Module registration
│   └── pages/                               # NEW — list, detail, discovery, settings
│
├── src/modules/personnel/                   # Personnel management UI (updated)
├── src/modules/records/                     # Recognition records viewer (NEW)
└── openapi-ts.config.ts                     # OpenAPI codegen config
```

---

## Device API Summary

Devices expose an HTTP API on port 8090. 109 endpoints across 6 categories:

| Category | Count | Description |
|----------|-------|-------------|
| Device Management | 65 | Info, settings, status, network, config, operation control |
| Personnel Management | 15 | CRUD personnel, permissions, pass times |
| Face/Photo Management | 12 | Face registration, update, delete, query, feature extract |
| Recognition Records | 9 | Query/delete face + card records (multiple APIs for legacy/new) |
| Rule Management | 5 | Schedules, access groups, time zones |
| Callback Configuration | 8 | Register callback URLs on device for various events |

### Device Communication Pattern

```
Backend → Device (outbound calls from backend service):
  DeviceHttpClient(device_id)
    ├── device_info()       → GET /device/info
    ├── get_personnel()     → GET /person
    ├── register_personnel()→ POST /person/create
    ├── register_face()     → POST /face/create
    ├── query_records()     → POST /newFindRecords
    └── ... (all 109 endpoints)

Device → Backend (callback pushes):
  All callbacks POST to /api/v1/callbacks/{type}
  Auth validated via deviceKey parameter in payload
  
  Payload includes: deviceKey, time, plus type-specific fields
  (see Callback section below for full field details)
```

### Callbacks (Device → Backend)

| Callback | Configure via Device API | Backend Route |
|----------|-------------------------|---------------|
| Heartbeat | `POST /device/setDeviceHeartBeat` | `POST /callbacks/heartbeat` |
| Face/ID Recognition | `POST /device/setIdentifyCallBack` | `POST /callbacks/identify` |
| Photo Registration | `POST /device/setImgRegCallBack` | `POST /callbacks/photo_registration` |
| Card Registration | `POST /device/setCardRegCallBack` | `POST /callbacks/card_registration` |
| Alarm Events | `POST /device/setEvent` | `POST /callbacks/event` |
| QR Code Scan | `POST /device/setQRCodeCallback` | `POST /callbacks/qrcode` |
| Registration Info | `POST /device/setRegistCallback` | `POST /callbacks/registration_info` |
| Fingerprint Enroll | `POST /device/setFingerRegCallback` | `POST /callbacks/finger_reg` |
| Task Results | Backend sets `setTaskInterfaceAddress` URL → device POSTs results | `POST /callbacks/task_result` |

---

## Database Schema

### devices (enhanced)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| device_id | UUID (unique) | Maps to deviceKey sent by device |
| device_name | VARCHAR | Device display name |
| ip_address | INET | Device LAN IP |
| port | INTEGER (default 8090) | Device API port |
| api_password | VARCHAR | Password for device API auth |
| serial_number | VARCHAR | From device handshake |
| firmware_version | VARCHAR | Device firmware version |
| sdk_version | VARCHAR | Algorithm SDK version |
| status | VARCHAR (online/offline/unknown) | Runtime status |
| last_seen_at | TIMESTAMP | Last heartbeat/callback timestamp |
| settings | JSONB | Recognition mode, thresholds, etc. |
| callback_urls | JSONB | Registered callback URL set on device |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | Auto-updated |

### personnel (enhanced)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| user_id | UUID (FK → users) | Existing FK for owner reference |
| person_id_internal | UUID | Internal person identifier |
| person_id_device | VARCHAR | Device-side personId |
| name | VARCHAR | Name label shown on device |
| card_no | VARCHAR | Card number |
| idcard_num | VARCHAR | ID card number |
| id_number | VARCHAR | National ID number |
| permissions | JSONB | Access permissions |
| pass_time | JSONB | Allowed pass time windows |
| push_to_device | BOOLEAN | Flag for push-to-device |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | Auto-updated |

### photo_registrations (new)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| person_id_internal | UUID (FK → personnel.id) | |
| person_id_device | VARCHAR | Device's personId |
| device_id | UUID (FK → devices.id) | Device where photo registered |
| face_id | VARCHAR | Device's faceId |
| feature | VARCHAR | Feature code from callback |
| feature_key | VARCHAR | Feature secret key |
| img_url | VARCHAR | Local path or S3 URL |
| img_data | BYTEA | Cached base64 image |
| source | VARCHAR (manual/device/callback) | |
| created_at | TIMESTAMP | |

### recognition_records (enhanced)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| device_id | UUID (FK → devices.id) | Device that recorded |
| person_id_internal | UUID (FK → personnel.id) | |
| person_id_device | VARCHAR | Device personId |
| record_type | VARCHAR (face/card/face&card) | |
| mode | VARCHAR | Recognition mode |
| event_type | VARCHAR (normal/alarm) | |
| event_name | VARCHAR (identify/illegal_access/...) | |
| event_time | TIMESTAMP | Recognition timestamp |
| img_data | BYTEA | Base64 on-site photo |
| source | VARCHAR (callback/sync) | How record was obtained |
| created_at | TIMESTAMP | Auto-updated |

### callback_configs (new)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| device_id | UUID (FK → devices.id) | |
| config_type | VARCHAR | heartbeat/identify/photo_reg/card_reg/event/qrcode/registration_info/finger_reg/task_result |
| callback_url | VARCHAR | URL registered on device |
| enabled | BOOLEAN (default true) | |

### device_person_mapping (new)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| person_id_internal | UUID (FK → personnel.id) | |
| device_id | UUID (FK → devices.id) | |
| person_id_device | VARCHAR | Device's personId |
| photo_ids | JSONB | Array of faceIds on this device |
| synced_at | TIMESTAMP | Last sync time |

### device_task_logs (new)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Primary key |
| device_id | UUID (FK → devices.id) | |
| task_no | VARCHAR | Async task identifier |
| interface_name | VARCHAR | identifyCallback, person/create, face, etc. |
| result | VARCHAR (ok/error) | |
| response_data | JSONB | Full device response |

---

## Execution Phases

### Phase 1 — CRUD Endpoints (current step)

**Goal:** Full backend CRUD for devices, personnel, photos, and records without device communication.

1. Create Alembic migration with all 7 tables
2. Implement device CRUD (list, get, create, update, delete, status)
3. Implement personnel CRUD (extended with device fields)
4. Implement photo registration CRUD
5. Implement recognition record CRUD (device-aware via mapping)
6. Implement callback_config CRUD
7. Implement person_mapping CRUD

**New schemas to generate:** All Pydantic schemas for 7 tables including request/response validation.

### Phase 2 — Device Communication Service

**Goal:** Connect backend to real devices.

1. `DeviceHttpClient` wrapper class — all 109 device API endpoints
2. Callback receiver endpoints (/api/v1/callbacks/*) — 9 callback handlers
3. Task dispatch service (setTaskInterfaceAddress pattern)
4. Periodic sync worker (fetch records, check status)
5. Device registration flow (auto-fill serial/firmware from handshake)
6. LAN discovery service (subnet scanning with timeout-per-host)
7. Settings sync API (push config to device)

### Phase 3 — Frontend Integration

1. Device management pages (list, detail panel, settings, discover)
2. Personnel pages (extended CRUD, photo upload, device assignment)
3. Recognition records viewer (filter by device/date/type)
4. Dashboard (device status overview, recent activity, stats)
5. Update permission codes to match actual access matrix

### Phase 4 — Polish

1. Background workers for periodic record sync from devices
2. Real-time device status updates (server-sent events or polling)
3. Bulk operations (sync all devices, batch enroll personnel)
4. Performance tuning (image storage migration to S3 if needed)

---

## Permission Matrix

| Permission Code | Scope |
|----------------|-------|
| `device:read` | View device list, status, settings, records |
| `device:write` | Add/remove/update devices, sync, manage settings |
| `personnel:read` | View personnel list and details |
| `personnel:write` | Add/update/delete personnel and sync to devices |
| `record:read` | View recognition records |
| `record:write` | Delete recognition records |

---

## Key Design Decisions

1. **Device auth:** Validate `deviceKey` in callback payloads against `devices.device_id`. No separate `pass` field for callbacks.

2. **Record strategy:** Device keeps its own records. Backend stores copies from callbacks for reporting. Records can be fetched live from device on-demand.

3. **Person ID mapping:** Internal UUID (`person_id_internal` in personnel table) + separate `device_person_mapping` table per device. `person_id_device` varies per person per device.

4. **Image storage:** Base64 images stored as `BYTEA` in DB. Acceptable for current scale; plan to migrate to S3/disk storage later.

5. **LAN discovery:** User selects subnet range (e.g., `192.168.1.0/24`), backend sequentially pings `http://<ip>:8090/device/info` with timeout. Auto-discovers unregistered devices.

6. **Push vs fetch:** Backend pushes personnel/photos to devices (not pull). Records pushed by device via callbacks (not polled).
