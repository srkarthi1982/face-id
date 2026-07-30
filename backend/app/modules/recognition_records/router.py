from app.modules.recognition_records import service
from app.modules.recognition_records.schemas import (
    RecognitionRecordCreate,
    RecognitionRecordResponse,
    RecognitionRecordUpdate,
)
from app.core.database import get_db
from app.core.deps import require_permission
from app.core.permissions import PermissionCode
from app.core.response import ok, Meta, SuccessResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/record", tags=["Records"])


@router.get("/", response_model=SuccessResponse[list[RecognitionRecordResponse]])
def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    device_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.RECORD_READ)),
):
    items, total = service.get_all(db, page, page_size, device_id)
    pages = max(1, -(-total // page_size))
    return ok(items, meta=Meta(page=page, page_size=page_size, total=total, pages=pages))


@router.get("/{record_id}", response_model=SuccessResponse[RecognitionRecordResponse])
def get_record(record_id: int, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.RECORD_READ))):
    record = service.get_one(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return ok(record)


@router.post("/", status_code=201, response_model=SuccessResponse[RecognitionRecordResponse])
def create_record(payload: RecognitionRecordCreate, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.RECORD_WRITE))):
    record = service.create(db, payload)
    return ok(record)


@router.put("/{record_id}", response_model=SuccessResponse[RecognitionRecordResponse])
def update_record(record_id: int, payload: RecognitionRecordUpdate, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.RECORD_WRITE))):
    record = service.update(db, record_id, payload)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return ok(record)


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.RECORD_WRITE))):
    record = service.delete(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
