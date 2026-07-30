from app.modules.photos import service
from app.modules.photos.schemas import (
    PhotoCreate,
    PhotoResponse,
    PhotoUpdate,
)
from app.core.database import get_db
from app.core.deps import require_permission
from app.core.permissions import PermissionCode
from app.core.response import ok, Meta, SuccessResponse
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/photo", tags=["Photos"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


@router.get("/", response_model=SuccessResponse[list[PhotoResponse]])
def list_photos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    person_id: Optional[str] = None,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_READ)),
):
    items, total = service.get_all(db, page, page_size, person_id)
    pages = max(1, -(-total // page_size))
    return ok(items, meta=Meta(page=page, page_size=page_size, total=total, pages=pages))


@router.post("/upload", status_code=201, response_model=SuccessResponse[PhotoResponse])
async def upload_photo(
    file: UploadFile = File(..., description="JPEG or PNG image"),
    person_id_internal: str = Form(...),
    device_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_WRITE)),
):
    """
    Upload a photo for a person (multipart/form-data).

    Replaces the existing photo for the same (person, device) pair.
    Omit device_id to store the person's master photo.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG or PNG images are allowed")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Image must be smaller than 5 MB")

    try:
        photo = service.upload(db, person_id_internal, content, file.content_type, device_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ok(photo)


@router.get("/{photo_id}", response_model=SuccessResponse[PhotoResponse])
def get_photo(photo_id: int, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.PERSONNEL_READ))):
    photo = service.get_one(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return ok(PhotoResponse.model_validate(photo))


@router.get("/{photo_id}/image")
def get_photo_image(
    photo_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.PERSONNEL_READ)),
):
    """Return the stored image binary for a photo registration."""
    photo = service.get_one(db, photo_id)
    if not photo or photo.img_data is None:
        raise HTTPException(status_code=404, detail="Photo image not found")
    return Response(content=photo.img_data, media_type=photo.img_content_type or "image/jpeg")


@router.post("/", status_code=201, response_model=SuccessResponse[PhotoResponse])
def create_photo(payload: PhotoCreate, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.PERSONNEL_WRITE))):
    try:
        photo = service.create(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ok(photo)


@router.put("/{photo_id}", response_model=SuccessResponse[PhotoResponse])
def update_photo(photo_id: int, payload: PhotoUpdate, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.PERSONNEL_WRITE))):
    try:
        photo = service.update(db, photo_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return ok(photo)


@router.delete("/{photo_id}", status_code=204)
def delete_photo(photo_id: int, db: Session = Depends(get_db), _ = Depends(require_permission(PermissionCode.PERSONNEL_WRITE))):
    photo = service.delete(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
