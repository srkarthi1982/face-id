from datetime import datetime

from pydantic import BaseModel


class CallbackConfigCreate(BaseModel):
    device_id: int
    config_type: str
    callback_url: str | None = None
    enabled: bool = True


class CallbackConfigUpdate(BaseModel):
    callback_url: str | None = None
    enabled: bool | None = None


class CallbackConfigResponse(BaseModel):
    id: int
    device_id: int
    config_type: str
    callback_url: str | None = None
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
