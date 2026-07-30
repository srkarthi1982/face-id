from app.modules.callbacks import service
from app.modules.callbacks.schemas import (
    CallbackConfigCreate,
    CallbackConfigResponse,
    CallbackConfigUpdate,
)
from app.core.database import get_db
from app.core.deps import require_permission
from app.core.permissions import PermissionCode
from app.core.response import ok, Meta, SuccessResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/callback", tags=["Callback"])


@router.get("/", response_model=SuccessResponse[list[CallbackConfigResponse]])
def list_configs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    device_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.DEVICE_READ)),
):
    items, total = service.get_all(db, page, page_size, device_id)
    pages = max(1, -(-total // page_size))
    return ok(items, meta=Meta(page=page, page_size=page_size, total=total, pages=pages))


@router.get("/{config_id}", response_model=SuccessResponse[CallbackConfigResponse])
def get_config(config_id: int, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.DEVICE_READ))):
    config = service.get_one(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return ok(config)


@router.post("/", status_code=201, response_model=SuccessResponse[CallbackConfigResponse])
def create_config(payload: CallbackConfigCreate, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.DEVICE_WRITE))):
    config = service.create(db, payload)
    return ok(config)


@router.put("/{config_id}", response_model=SuccessResponse[CallbackConfigResponse])
def update_config(config_id: int, payload: CallbackConfigUpdate, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.DEVICE_WRITE))):
    config = service.update(db, config_id, payload)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return ok(config)


@router.delete("/{config_id}", status_code=204)
def delete_config(config_id: int, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.DEVICE_WRITE))):
    config = service.delete(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
