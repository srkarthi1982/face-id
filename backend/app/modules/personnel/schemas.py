from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from datetime import date, datetime


class PersonnelBase(BaseModel):
    """Base schema for Personnel with common fields."""
    emp_no: str = Field(..., min_length=1, max_length=64, description="Employee number (unique per organization)")
    full_name: str = Field(..., min_length=1, max_length=200, description="Full name")
    gender: int = Field(default=0, ge=0, le=2, description="Gender: 0=Unknown, 1=Male, 2=Female")
    email: Optional[str] = Field(None, max_length=255, description="Email address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    nationality: Optional[str] = Field(None, max_length=100, description="Nationality")
    idcard_num: Optional[str] = Field(None, max_length=50, description="ID card number")
    id_number: Optional[str] = Field(None, max_length=50, description="National ID number")
    card_no: Optional[str] = Field(None, max_length=100, description="Card number")
    department_id: Optional[int] = Field(None, description="Department ID (FK to locations)")
    position: Optional[str] = Field(None, max_length=200, description="Job position")
    hire_date: Optional[str] = Field(None, description="Hire date (YYYY-MM-DD)")
    push_to_device: bool = Field(default=False, description="Push to device flag")


class PersonnelCreate(PersonnelBase):
    """Schema for creating a new personnel record."""
    org_id: Optional[int] = Field(None, description="Organization ID (FK to locations)")
    person_id_internal: Optional[str] = Field(None, max_length=64, description="Internal person ID")
    person_id_device: Optional[str] = Field(None, max_length=64, description="Device person ID")
    permissions: dict = Field(default={}, description="Access permissions")
    pass_time: Optional[dict] = Field(None, description="Pass time configuration")
    is_active: bool = Field(default=True, description="Active status")


class PersonnelUpdate(BaseModel):
    """Schema for updating personnel record (all fields optional)."""
    emp_no: Optional[str] = Field(None, min_length=1, max_length=64)
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    gender: Optional[int] = Field(None, ge=0, le=2)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = Field(None, max_length=100)
    idcard_num: Optional[str] = Field(None, max_length=50)
    id_number: Optional[str] = Field(None, max_length=50)
    card_no: Optional[str] = Field(None, max_length=100)
    department_id: Optional[int] = None
    position: Optional[str] = Field(None, max_length=200)
    hire_date: Optional[str] = None
    push_to_device: Optional[bool] = None
    person_id_internal: Optional[str] = Field(None, max_length=64)
    person_id_device: Optional[str] = Field(None, max_length=64)
    permissions: Optional[dict] = None
    pass_time: Optional[dict] = None
    is_active: Optional[bool] = None


class PersonnelResponse(PersonnelBase):
    """Schema for personnel response."""
    id: int
    org_id: Optional[int]
    person_id_internal: Optional[str]
    person_id_device: Optional[str]
    permissions: dict
    pass_time: Optional[dict]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PersonnelStats(BaseModel):
    """Schema for personnel statistics."""
    total: int
    active: int
    inactive: int
    by_gender: dict  # {0: count, 1: count, 2: count}


class PersonnelPushRequest(BaseModel):
    """Schema for pushing a personnel record to one or more devices."""
    device_ids: list[int] = Field(..., min_length=1, description="Target device IDs")
    include_photo: bool = Field(default=True, description="Send registration photo (face1) if available")


class DevicePushResult(BaseModel):
    """Result of pushing a personnel record to a single device."""
    device_id: int
    device_name: Optional[str] = None
    success: bool
    code: Optional[str] = None
    msg: Optional[str] = None


class PersonnelPushResponse(BaseModel):
    """Aggregated result of a push-to-devices operation."""
    personnel_id: int
    person_id_device: str
    pushed: int
    failed: int
    results: list[DevicePushResult]


class BulkPushRequest(BaseModel):
    """Schema for pushing multiple personnel records to devices as a background job."""
    personnel_ids: list[int] = Field(..., min_length=1, description="Personnel IDs to push")
    device_ids: list[int] = Field(..., min_length=1, description="Target device IDs")
    include_photo: bool = Field(default=True, description="Send registration photo (face1) if available")

    @field_validator("personnel_ids", "device_ids")
    @classmethod
    def _dedupe_preserving_order(cls, v: list[int]) -> list[int]:
        # The same Personnel row processed by two workers at once would raise
        # StaleDataError from the optimistic version lock.
        return list(dict.fromkeys(v))


class PushJobError(BaseModel):
    """Person-level failure inside a bulk push job."""
    code: Literal["PERSON_NOT_FOUND", "PERSON_INVALID", "INTERNAL_ERROR"]
    message: str


class PersonPushJobResult(BaseModel):
    """Per-person outcome inside a bulk push job."""
    personnel_id: int
    ok: bool
    pushed: int
    failed: int
    results: list[DevicePushResult]
    error: Optional[PushJobError] = None


class PushJobSnapshot(BaseModel):
    """Full state of a bulk push job; served by polling and as each SSE event."""
    job_id: str
    status: Literal["running", "completed", "cancelled"]
    total: int
    done: int
    results: list[PersonPushJobResult]
    skipped_personnel_ids: list[int]


class BulkPushJobResponse(BaseModel):
    """Returned immediately when a bulk push job is accepted."""
    job_id: str
    total: int


class PersonnelSearchFilters(BaseModel):
    """Schema for advanced search filters."""
    org_id: Optional[int] = None
    emp_no: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[int] = None
    is_active: Optional[bool] = None
    department_id: Optional[int] = None
    search: Optional[str] = None  # Search across multiple fields
