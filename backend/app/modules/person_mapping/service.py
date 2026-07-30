from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.person_mapping.models import DevicePersonMapping
from app.modules.person_mapping.schemas import (
    DevicePersonMappingCreate,
    DevicePersonMappingResponse,
    DevicePersonMappingUpdate,
)


def get_all(db: Session, page: int = 1, page_size: int = 20, device_id: int | None = None) -> tuple[list[DevicePersonMappingResponse], int]:
    query = select(DevicePersonMapping)
    if device_id:
        query = query.where(DevicePersonMapping.device_id == device_id)
    total = db.execute(select(db.func.count()).select_from(query.subquery())).scalar()
    items = db.execute(
        query.order_by(DevicePersonMapping.id).offset((page - 1) * page_size).limit(page_size)
    ).scalars().all()
    return [DevicePersonMappingResponse.model_validate(i) for i in items], total


def get_one(db: Session, id: int) -> DevicePersonMapping | None:
    return db.get(DevicePersonMapping, id)


def create(db: Session, payload: DevicePersonMappingCreate) -> DevicePersonMappingResponse:
    mapping = DevicePersonMapping(
        person_id_internal=payload.person_id_internal,
        device_id=payload.device_id,
        person_id_device=payload.person_id_device,
        photo_ids=payload.photo_ids,
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return DevicePersonMappingResponse.model_validate(mapping)


def update(db: Session, id: int, payload: DevicePersonMappingUpdate) -> DevicePersonMappingResponse | None:
    mapping = get_one(db, id)
    if not mapping:
        return None
    data = payload.model_dump(exclude_none=True)
    for key, value in data.items():
        setattr(mapping, key, value)
    db.commit()
    db.refresh(mapping)
    return DevicePersonMappingResponse.model_validate(mapping)


def delete(db: Session, id: int) -> DevicePersonMappingResponse | None:
    mapping = get_one(db, id)
    if not mapping:
        return None
    db.delete(mapping)
    db.commit()
    return DevicePersonMappingResponse.model_validate(mapping)
