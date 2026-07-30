from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.callbacks.models import CallbackConfig
from app.modules.callbacks.schemas import (
    CallbackConfigCreate,
    CallbackConfigResponse,
    CallbackConfigUpdate,
)


def get_all(db: Session, page: int = 1, page_size: int = 20, device_id: int | None = None) -> tuple[list[CallbackConfigResponse], int]:
    query = select(CallbackConfig)
    if device_id:
        query = query.where(CallbackConfig.device_id == device_id)
    total = db.execute(select(db.func.count()).select_from(query.subquery())).scalar()
    items = db.execute(
        query.order_by(CallbackConfig.id).offset((page - 1) * page_size).limit(page_size)
    ).scalars().all()
    return [CallbackConfigResponse.model_validate(i) for i in items], total


def get_one(db: Session, id: int) -> CallbackConfig | None:
    return db.get(CallbackConfig, id)


def create(db: Session, payload: CallbackConfigCreate) -> CallbackConfigResponse:
    config = CallbackConfig(
        device_id=payload.device_id,
        config_type=payload.config_type,
        callback_url=payload.callback_url,
        enabled=payload.enabled,
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return CallbackConfigResponse.model_validate(config)


def update(db: Session, id: int, payload: CallbackConfigUpdate) -> CallbackConfigResponse | None:
    config = get_one(db, id)
    if not config:
        return None
    data = payload.model_dump(exclude_none=True)
    for key, value in data.items():
        setattr(config, key, value)
    db.commit()
    db.refresh(config)
    return CallbackConfigResponse.model_validate(config)


def delete(db: Session, id: int) -> CallbackConfigResponse | None:
    config = get_one(db, id)
    if not config:
        return None
    db.delete(config)
    db.commit()
    return CallbackConfigResponse.model_validate(config)
