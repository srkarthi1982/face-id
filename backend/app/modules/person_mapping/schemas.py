from datetime import datetime

from pydantic import BaseModel


class DevicePersonMappingCreate(BaseModel):
    person_id_internal: str
    device_id: int
    person_id_device: str | None = None
    photo_ids: dict = {}


class DevicePersonMappingUpdate(BaseModel):
    person_id_device: str | None = None
    photo_ids: dict | None = None
    synced_at: str | None = None


class DevicePersonMappingResponse(BaseModel):
    id: int
    person_id_internal: str
    device_id: int
    person_id_device: str | None = None
    photo_ids: dict
    synced_at: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
