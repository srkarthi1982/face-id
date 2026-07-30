from app.modules.device.service import get_all, get_one, create as create_device, update as update_device, delete as delete_device, discover_devices, refresh_device
from app.modules.device.schemas import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DiscoverRequest,
    DiscoveredDevice,
)
from app.core.database import get_db
from app.core.deps import require_permission
from app.core.permissions import PermissionCode
from app.core.response import ok, Meta, SuccessResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/device", tags=["Device"])


@router.get("/endpoint/", response_model=SuccessResponse[list[DeviceResponse]])
def list_endpoints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search_text: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.DEVICE_READ)),
):
    devices, total = get_all(db, page, page_size, search_text, status)
    pages = max(1, -(-total // page_size))
    return ok(devices, meta=Meta(page=page, page_size=page_size, total=total, pages=pages))


@router.get("/endpoint/{device_id}", response_model=SuccessResponse[DeviceResponse])
def get_endpoint(device_id: int, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.DEVICE_READ))):
    device = get_one(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return ok(device)


@router.post("/endpoint/", status_code=201, response_model=SuccessResponse[DeviceResponse])
def create_endpoint(payload: DeviceCreate, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.DEVICE_WRITE))):
    device = create_device(db, payload)
    return ok(device)


@router.put("/endpoint/{device_id}", response_model=SuccessResponse[DeviceResponse])
def update_endpoint(device_id: int, payload: DeviceUpdate, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.DEVICE_WRITE))):
    device = update_device(db, device_id, payload)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return ok(device)


@router.delete("/endpoint/{device_id}", status_code=204)
def delete_endpoint(device_id: int, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.DEVICE_WRITE))):
    device = delete_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")


@router.post("/endpoint/{device_id}/refresh", response_model=SuccessResponse[DeviceResponse])
def refresh_endpoint(device_id: int, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.DEVICE_READ))):
    device = refresh_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return ok(device)


@router.post("/setup/connect", status_code=201, response_model=SuccessResponse[dict])
def connect_device(payload: DeviceCreate, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.DEVICE_WRITE))):
    create_device(db, payload)
    return ok({"message": f"Device '{payload.device_name}' connected successfully"})


@router.post("/setup/discover", status_code=200, response_model=SuccessResponse[list[DiscoveredDevice]])
def discover_devices_endpoint(payload: DiscoverRequest, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.DEVICE_READ))):
    result = discover_devices(db, payload.subnet)
    return ok(result["data"])
