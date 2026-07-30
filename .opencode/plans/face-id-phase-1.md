# Phase 1: Backend CRUD Endpoints

**Goal:** Full backend CRUD for devices, personnel, photos, and records without device communication.

**Scope:** Database models, schemas, CRUD operations, routers, Alembic migration, permission codes.

---

## Files to Create/Modify

### 1. Permissions (modify)
| File | Change |
|------|--------|
| `backend/app/core/permissions.py` | Add DEVICE_READ, DEVICE_WRITE, PERSONNEL_READ, PERSONNEL_WRITE, RECORD_READ, RECORD_WRITE to PERMISSION_REGISTRY |

### 2. Device module (enhance — replace stubs)
| File | Change |
|------|--------|
| `backend/app/modules/device/models.py` | Replace with enhanced model (id, device_id, device_name, ip_address, port, api_password, serial_number, firmware_version, sdk_version, status, last_seen_at, settings, callback_urls, created_at, updated_at) |
| `backend/app/modules/device/schemas.py` | Create full schemas file: DeviceCreate, DeviceUpdate, DeviceResponse, DeviceStatusResponse, PaginatedDevices, DiscoverRequest/Response, ConnectResponse |
| `backend/app/modules/device/crud.py` | Create: get_all, get_one, create, update, delete, update_status |
| `backend/app/modules/device/router.py` | Replace dummy endpoints with DB-backed CRUD endpoints |
| `backend/app/modules/device/__init__.py` | No change (already exports router) |

### 3. Personnel module (enhance — add CRUD)
| File | Change |
|------|--------|
| `backend/app/modules/personnel/models.py` | Add: person_id_internal, person_id_device, card_no, idcard_num, id_number, permissions(JSONB), pass_time(JSONB), push_to_device |
| `backend/app/modules/personnel/schemas.py` | Expand with all new fields, add: PersonnelCreate, PersonnelUpdate, PersonnelResponse, PaginatedPersonnel |
| `backend/app/modules/personnel/router.py` | Replace stub with full CRUD: list, get, create, update, delete, deactivate/activate |

### 4. Photo registrations module (new)
| Filename | Purpose |
|----------|---------|
| `backend/app/modules/photos/__init__.py` | `from .router import router` |
| `backend/app/modules/photos/models.py` | SQLAlchemy model |
| `backend/app/modules/photos/schemas.py` | Pydantic schemas |
| `backend/app/modules/photos/crud.py` | CRUD operations |
| `backend/app/modules/photos/router.py` | Full CRUD endpoints |

### 5. Recognition records module (new)
| Filename | Purpose |
|----------|---------|
| `backend/app/modules/recognition_records/__init__.py` | `from .router import router` |
| `backend/app/modules/recognition_records/models.py` | SQLAlchemy model |
| `backend/app/modules/recognition_records/schemas.py` | Pydantic schemas |
| `backend/app/modules/recognition_records/crud.py` | CRUD operations |
| `backend/app/modules/recognition_records/router.py` | Full CRUD endpoints |

### 6. Callback configs module (new)
| Filename | Purpose |
|----------|---------|
| `backend/app/modules/callbacks/__init__.py` | `from .router import router` |
| `backend/app/modules/callbacks/models.py` | SQLAlchemy model |
| `backend/app/modules/callbacks/schemas.py` | Pydantic schemas |
| `backend/app/modules/callbacks/crud.py` | CRUD operations |
| `backend/app/modules/callbacks/router.py` | Full CRUD endpoints |

### 7. Person mapping module (new)
| Filename | Purpose |
|----------|---------|
| `backend/app/modules/person_mapping/__init__.py` | `from .router import router` |
| `backend/app/modules/person_mapping/models.py` | SQLAlchemy model |
| `backend/app/modules/person_mapping/schemas.py` | Pydantic schemas |
| `backend/app/modules/person_mapping/crud.py` | CRUD operations |
| `backend/app/modules/person_mapping/router.py` | Full CRUD endpoints |

### 8. Alembic migration (new)
| Filename | Purpose |
|----------|---------|
| `backend/alembic/versions/xxx_phase1_devices.py` | Create all 7 tables + alter existing ones |

### 9. App registration (modify)
| File | Change |
|------|--------|
| `backend/app/modules/__init__.py` | Add new module names to MODULE_NAMES list |

---

## Detailed Step-by-Step

### Step 1: Add permission codes
Add to `PermissionCode` and `PERMISSION_REGISTRY`:
- `DEVICE_READ = "device:read"` — View device list, status, settings, records
- `DEVICE_WRITE = "device:write"` — Add/remove/update devices, sync, manage settings
- `PERSONNEL_READ = "personnel:read"` — View personnel list and details
- `PERSONNEL_WRITE = "personnel:write"` — Add/update/delete personnel and sync to devices
- `RECORD_READ = "record:read"` — View recognition records
- `RECORD_WRITE = "record:write"` — Delete recognition records

### Step 2: Update device model
Replace `Device` model with:

```python
class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)  # deviceKey
    device_name: Mapped[str] = mapped_column(String(200), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=8090)
    api_password: Mapped[str] = mapped_column(String(255), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(200), nullable=True)
    firmware_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sdk_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="unknown", nullable=False)  # online|offline|unknown
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    callback_urls: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
```

### Step 3: Add personnel model fields
Add these columns to `Personnel` model:
- `person_id_internal: Mapped[uuid]` — internal UUID
- `person_id_device: Mapped[str | None]` — device-side personId
- `card_no: Mapped[str | None]` — card number
- `idcard_num: Mapped[str | None]` — ID card number
- `id_number: Mapped[str | None]` — national ID
- `permissions: Mapped[dict]` — JSONB access permissions
- `pass_time: Mapped[dict | None]` — JSONB time windows
- `push_to_device: Mapped[bool]` — flag for push

### Step 4: Create all new models (same structure, one each)
Each model follows:
```python
class NewModel(Base):
    __tablename__ = "new_models"
    id: Mapped[int] = mapped_column(primary_key=True)
    # ... fields ...
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=...)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=..., onupdate=...)
```

### Step 5: Create all schemas
Follow existing pattern:
- `XxxCreate` — full required fields
- `XxxUpdate` — all optional with `| None = None`
- `XxxResponse` — inherits from base + `model_config = {"from_attributes": True}`
- `PaginatedXxx` — wrapper with `data: list[XxxResponse], meta: dict`
- Request models for special operations (discover, connect, etc.)

### Step 6: Create CRUD files
Standard CRUD pattern per module:
```python
from sqlalchemy.orm import Session
from app.core.database import get_db

def get_all(db: Session, page: int = 1, page_size: int = 20, **filters):
    query = db.query(Model)
    # apply filters
    total = query.count()
    items = query.offset((page-1)*page_size).limit(page_size).all()
    pages = max(1, -(-total // page_size))  # ceil div
    return {"data": items, "meta": {"page": page, "page_size": page_size, "total": total, "pages": pages}}

def get_one(db, id):
    item = db.query(Model).filter(Model.id == id).first()
    return item

def create(db, payload):
    item = Model(**payload.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def update(db, id, payload):
    item = get_one(db, id)
    for key, value in payload.dict(exclude_none=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

def delete(db, id):
    item = get_one(db, id)
    db.delete(item)
    db.commit()
    return item
```

### Step 7: Create routers
Each router:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_permission
from app.core.response import ok
from .crud import get_all, get_one, create, update, delete
from .schemas import ...

router = APIRouter(prefix="/xxx", tags=["Xxx"])

@router.get("/xxx/", response_model=SuccessResponse)
@require_permission(PermissionCode.XXX_READ)
def list_xxx(db: Session = Depends(get_db), page: int = 1, page_size: int = 20):
    result = get_all(db, page, page_size)
    return ok(result["data"], meta=result["meta"])

@router.get("/xxx/{id}", response_model=SuccessResponse)
@require_permission(PermissionCode.XXX_READ)
def get_xxx(id: int, db: Session = Depends(get_db)):
    item = get_one(db, id)
    if not item:
        raise HTTPException(404, "Not found")
    return ok(item)

@router.post("/xxx/", status_code=201)
@require_permission(PermissionCode.XXX_WRITE)
def create_xxx(payload: XxxCreate, db: Session = Depends(get_db)):
    item = create(db, payload)
    return ok(item)

@router.put("/xxx/{id}")
@require_permission(PermissionCode.XXX_WRITE)
def update_xxx(id: int, payload: XxxUpdate, db: Session = Depends(get_db)):
    item = update(db, id, payload)
    return ok(item)

@router.delete("/xxx/{id}")
@require_permission(PermissionCode.XXX_WRITE)
def delete_xxx(id: int, db: Session = Depends(get_db)):
    item = delete(db, id)
    return ok(item)
```

### Step 8: Create Alembic migration
Create a new migration that:
1. Drops existing `devices` and `personnel` tables (they're not in the migration — need to create them)
   - Actually: since the tables are not in the migration yet, just CREATE them fresh
2. Creates: `photo_registrations`, `recognition_records`, `callback_configs`, `device_person_mapping`, `device_task_logs`
3. Adds foreign keys between tables

### Step 9: Register modules
Add to `MODULE_NAMES` in `backend/app/modules/__init__.py`:
- Keep: device, personnel (already there)
- Add: photos, recognition_records, callbacks, person_mapping

### Step 10: Test
Start server with `python -m uvicorn app.main:app --reload` and verify:
- All routers are registered
- No import errors
- OpenAPI schema includes all endpoints
- Database migration runs cleanly

---

## Route Summary (Phase 1)

| Route | Methods | Permissions | Module |
|-------|---------|-------------|--------|
| `/device/endpoint/` | GET, POST | device:read, device:write | device |
| `/device/endpoint/{id}` | GET, PUT, DELETE | device:read, device:write | device |
| `/device/setup/connect` | POST | device:write | device |
| `/device/setup/discover` | POST | device:read | device |
| `/personnel/` | GET, POST | personnel:read, personnel:write | personnel |
| `/personnel/{id}` | GET, PUT, DELETE | personnel:read, personnel:write | personnel |
| `/photo/` | GET, POST | personnel:read (or dedicated) | photos |
| `/photo/{id}` | GET, PUT, DELETE | personnel:read (or dedicated) | photos |
| `/records/` | GET, POST | record:read, record:write | recognition_records |
| `/records/{id}` | GET, PUT, DELETE | record:read, record:write | recognition_records |
| `/callbacks/` | GET, POST | device:write | callbacks |
| `/callbacks/{id}` | GET, PUT, DELETE | device:write | callbacks |
| `/person-mapping/` | GET, POST | personnel:write | person_mapping |
| `/person-mapping/{id}` | GET, PUT, DELETE | personnel:write | person_mapping |

---

## Success Criteria

1. All 7 tables created by migration
2. All 5 modules (device, personnel, photos, recognition_records, callbacks, person_mapping) have their router mounted under `/api/v1/`
3. OpenAPI spec shows all CRUD endpoints
4. Authentication works (401 without token)
5. Authorization works (403 without permission)
6. DB operations work (CRUD tested against live database)
