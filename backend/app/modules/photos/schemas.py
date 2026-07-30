from datetime import datetime

from pydantic import BaseModel, Field


class PhotoCreate(BaseModel):
    person_id_internal: str
    person_id_device: str | None = None
    device_id: int | None = None
    face_id: str | None = None
    feature: str | None = None
    feature_key: str | None = None
    img_url: str | None = None
    img_data: str | None = Field(None, description="Base64-encoded image bytes")
    img_content_type: str | None = None
    source: str = "manual"


class PhotoUpdate(BaseModel):
    face_id: str | None = None
    feature: str | None = None
    feature_key: str | None = None
    img_url: str | None = None
    img_data: str | None = Field(None, description="Base64-encoded image bytes")
    img_content_type: str | None = None
    source: str | None = None


class PhotoResponse(BaseModel):
    id: int
    person_id_internal: str
    person_id_device: str | None = None
    device_id: int | None = None
    face_id: str | None = None
    feature: str | None = None
    feature_key: str | None = None
    img_url: str | None = None
    img_content_type: str | None = None
    has_image: bool
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
