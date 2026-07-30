from datetime import datetime

from pydantic import BaseModel, field_validator

from app.core.config import settings


class DeviceCreate(BaseModel):
    device_name: str
    ip_address: str
    port: int = 8090
    api_password: str = ""
    location_id: int | None = None
    serial_number: str | None = None
    firmware_version: str | None = None

    @field_validator("port")
    @classmethod
    def port_range(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("api_password")
    @classmethod
    def default_password(cls, v: str) -> str:
        if not v:
            return settings.DEVICE_API_PASSWORD
        return v


class DeviceUpdate(BaseModel):
    device_name: str | None = None
    ip_address: str | None = None
    port: int | None = None
    api_password: str | None = None
    location_id: int | None = None
    serial_number: str | None = None
    firmware_version: str | None = None
    sdk_version: str | None = None
    status: str | None = None
    settings: dict | None = None
    callback_urls: dict | None = None


class DeviceResponse(BaseModel):
    id: int
    device_id: str
    device_name: str
    ip_address: str
    port: int
    api_password: str
    location_id: int | None = None
    location_name: str | None = None
    serial_number: str | None = None
    firmware_version: str | None = None
    sdk_version: str | None = None
    status: str
    last_seen_at: datetime | None = None
    settings: dict
    callback_urls: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DeviceStatusResponse(BaseModel):
    id: int
    device_name: str
    ip_address: str
    status: str
    last_seen_at: str | None = None

    model_config = {"from_attributes": True}


class ConnectMessage(BaseModel):
    message: str


class ConnectResponse(BaseModel):
    success: bool = True
    data: ConnectMessage


class DiscoveredDevice(BaseModel):
    device_name: str
    ip_address: str
    location: str
    state: str
    serial_number: str | None = None
    firmware_version: str | None = None


class DiscoverRequest(BaseModel):
    subnet: str = "192.168.1.0/24"


class DiscoverResponse(BaseModel):
    success: bool = True
    data: list[DiscoveredDevice]
