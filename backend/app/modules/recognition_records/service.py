from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.recognition_records.models import RecognitionRecord
from app.modules.recognition_records.schemas import (
    RecognitionRecordCreate,
    RecognitionRecordResponse,
    RecognitionRecordUpdate,
)


def get_all(db: Session, page: int = 1, page_size: int = 20, device_id: int | None = None) -> tuple[list[RecognitionRecordResponse], int]:
    query = select(RecognitionRecord)
    if device_id:
        query = query.where(RecognitionRecord.device_id == device_id)
    total = db.execute(select(db.func.count()).select_from(query.subquery())).scalar()
    items = db.execute(
        query.order_by(RecognitionRecord.id).offset((page - 1) * page_size).limit(page_size)
    ).scalars().all()
    return [RecognitionRecordResponse.model_validate(i) for i in items], total


def get_one(db: Session, id: int) -> RecognitionRecord | None:
    return db.get(RecognitionRecord, id)


def create(db: Session, payload: RecognitionRecordCreate) -> RecognitionRecordResponse:
    record = RecognitionRecord(
        device_id=payload.device_id,
        person_id_internal=payload.person_id_internal,
        person_id_device=payload.person_id_device,
        record_type=payload.record_type,
        mode=payload.mode,
        event_type=payload.event_type,
        event_name=payload.event_name,
        event_time=payload.event_time,
        img_data=bytes.fromhex(payload.img_data) if payload.img_data else None,
        source=payload.source,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return RecognitionRecordResponse.model_validate(record)


def update(db: Session, id: int, payload: RecognitionRecordUpdate) -> RecognitionRecordResponse | None:
    record = get_one(db, id)
    if not record:
        return None
    data = payload.model_dump(exclude_none=True)
    for key, value in data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return RecognitionRecordResponse.model_validate(record)


def delete(db: Session, id: int) -> RecognitionRecordResponse | None:
    record = get_one(db, id)
    if not record:
        return None
    db.delete(record)
    db.commit()
    return RecognitionRecordResponse.model_validate(record)
