from datetime import datetime

from pydantic import BaseModel


class RecognitionRecordCreate(BaseModel):
    device_id: int
    person_id_internal: str | None = None
    person_id_device: str | None = None
    record_type: str
    mode: str | None = None
    event_type: str | None = None
    event_name: str | None = None
    event_time: str | None = None
    img_data: str | None = None
    source: str = "callback"


class RecognitionRecordUpdate(BaseModel):
    person_id_internal: str | None = None
    person_id_device: str | None = None
    record_type: str | None = None
    mode: str | None = None
    event_type: str | None = None
    event_name: str | None = None
    event_time: str | None = None
    img_data: str | None = None
    source: str | None = None


class RecognitionRecordResponse(BaseModel):
    id: int
    device_id: int
    person_id_internal: str | None = None
    person_id_device: str | None = None
    record_type: str
    mode: str | None = None
    event_type: str | None = None
    event_name: str | None = None
    event_time: str | None = None
    img_data: str | None = None
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
