import base64
import binascii

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.photos.models import PhotoRegistration
from app.modules.photos.schemas import (
    PhotoCreate,
    PhotoResponse,
    PhotoUpdate,
)
from app.modules.personnel.models import Personnel
from app.modules.device.models import Device


def _decode_img_data(img_data: str) -> bytes:
    try:
        return base64.b64decode(img_data, validate=True)
    except (binascii.Error, ValueError):
        raise ValueError("img_data must be valid base64")


def get_all(db: Session, page: int = 1, page_size: int = 20, person_id: str | None = None) -> tuple[list[PhotoResponse], int]:
    query = select(PhotoRegistration)
    if person_id:
        query = query.where(PhotoRegistration.person_id_internal == person_id)
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    items = db.execute(
        query.order_by(PhotoRegistration.id).offset((page - 1) * page_size).limit(page_size)
    ).scalars().all()
    return [PhotoResponse.model_validate(i) for i in items], total


def get_one(db: Session, id: int) -> PhotoRegistration | None:
    return db.get(PhotoRegistration, id)


def create(db: Session, payload: PhotoCreate) -> PhotoResponse:
    photo = PhotoRegistration(
        person_id_internal=payload.person_id_internal,
        person_id_device=payload.person_id_device,
        device_id=payload.device_id,
        face_id=payload.face_id,
        feature=payload.feature,
        feature_key=payload.feature_key,
        img_url=payload.img_url,
        img_data=_decode_img_data(payload.img_data) if payload.img_data else None,
        img_content_type=payload.img_content_type,
        source=payload.source,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return PhotoResponse.model_validate(photo)


def update(db: Session, id: int, payload: PhotoUpdate) -> PhotoResponse | None:
    photo = get_one(db, id)
    if not photo:
        return None
    data = payload.model_dump(exclude_none=True)
    if "img_data" in data:
        data["img_data"] = _decode_img_data(data["img_data"])
    for key, value in data.items():
        setattr(photo, key, value)
    db.commit()
    db.refresh(photo)
    return PhotoResponse.model_validate(photo)


def delete(db: Session, id: int) -> PhotoResponse | None:
    photo = get_one(db, id)
    if not photo:
        return None
    db.delete(photo)
    db.commit()
    return PhotoResponse.model_validate(photo)


def upload(
    db: Session,
    person_id_internal: str,
    content: bytes,
    content_type: str,
    device_id: int | None = None,
) -> PhotoResponse:
    """
    Upload an image for a person, replacing any existing photo for the same
    (person, device) pair. device_id=None stores the master photo used as the
    source for device sync.

    Raises:
        ValueError: If the personnel or device does not exist.
    """
    personnel = db.execute(
        select(Personnel).where(Personnel.person_id_internal == person_id_internal)
    ).scalar_one_or_none()
    if not personnel:
        raise ValueError(f"Personnel with internal ID '{person_id_internal}' does not exist.")

    if device_id is not None and not db.get(Device, device_id):
        raise ValueError(f"Device with ID {device_id} does not exist.")

    photo = db.execute(
        select(PhotoRegistration).where(
            PhotoRegistration.person_id_internal == person_id_internal,
            PhotoRegistration.device_id == device_id
            if device_id is not None
            else PhotoRegistration.device_id.is_(None),
        )
    ).scalars().first()

    if photo:
        photo.img_data = content
        photo.img_content_type = content_type
        photo.img_url = None
        photo.source = "manual"
    else:
        photo = PhotoRegistration(
            person_id_internal=person_id_internal,
            person_id_device=personnel.person_id_device,
            device_id=device_id,
            img_data=content,
            img_content_type=content_type,
            source="manual",
        )
        db.add(photo)

    db.commit()
    db.refresh(photo)
    return PhotoResponse.model_validate(photo)
