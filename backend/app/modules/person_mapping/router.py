from app.modules.person_mapping import service
from app.modules.person_mapping.schemas import (
    DevicePersonMappingCreate,
    DevicePersonMappingResponse,
    DevicePersonMappingUpdate,
)
from app.core.database import get_db
from app.core.deps import require_permission
from app.core.permissions import PermissionCode
from app.core.response import ok, Meta, SuccessResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/person-mapping", tags=["PersonMapping"])


@router.get("/", response_model=SuccessResponse[list[DevicePersonMappingResponse]])
def list_mappings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    device_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_READ)),
):
    items, total = service.get_all(db, page, page_size, device_id)
    pages = max(1, -(-total // page_size))
    return ok(items, meta=Meta(page=page, page_size=page_size, total=total, pages=pages))


@router.get("/{mapping_id}", response_model=SuccessResponse[DevicePersonMappingResponse])
def get_mapping(mapping_id: int, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.PERSONNEL_READ))):
    mapping = service.get_one(db, mapping_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return ok(mapping)


@router.post("/", status_code=201, response_model=SuccessResponse[DevicePersonMappingResponse])
def create_mapping(payload: DevicePersonMappingCreate, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.PERSONNEL_WRITE))):
    mapping = service.create(db, payload)
    return ok(mapping)


@router.put("/{mapping_id}", response_model=SuccessResponse[DevicePersonMappingResponse])
def update_mapping(mapping_id: int, payload: DevicePersonMappingUpdate, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.PERSONNEL_WRITE))):
    mapping = service.update(db, mapping_id, payload)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return ok(mapping)


@router.delete("/{mapping_id}", status_code=204)
def delete_mapping(mapping_id: int, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.PERSONNEL_WRITE))):
    mapping = service.delete(db, mapping_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
