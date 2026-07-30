from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from .models import UnitType, LocationType


class LocationCreate(BaseModel):
    name: str
    type: LocationType = LocationType.LOCATION
    parent_id: Optional[int] = None
    unit_id: Optional[int] = None
    sort_order: int = 0


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[LocationType] = None
    parent_id: Optional[int] = None
    unit_id: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class LocationResponse(BaseModel):
    id: int
    name: str
    type: LocationType
    parent_id: Optional[int] = None
    unit_id: Optional[int] = None
    unit_name: Optional[str] = None
    path: str
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LocationTreeItem(BaseModel):
    id: int
    name: str
    type: LocationType
    path: str
    is_active: bool
    sort_order: int
    parent_id: Optional[int] = None
    unit_id: Optional[int] = None
    unit_name: Optional[str] = None
    children: list["LocationTreeItem"] = []


class UnitCreate(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    type: UnitType = UnitType.UNIT
    parent_id: Optional[int] = None
    sort_order: int = 0


class UnitUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    type: Optional[UnitType] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class UnitResponse(BaseModel):
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    type: UnitType
    parent_id: Optional[int]
    path: str
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UnitTreeItem(BaseModel):
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    type: UnitType
    path: str
    is_active: bool
    sort_order: int
    children: list["UnitTreeItem"] = []


class LocationChainItem(BaseModel):
    type: LocationType
    name: str
    id: Optional[int] = None
    sort_order: int = 0


class LocationChainCreate(BaseModel):
    chain: List[LocationChainItem]
    skip_indices: List[int] = []
    unit_id: Optional[int] = None
    
    @field_validator("skip_indices")
    @classmethod
    def validate_skip_indices(cls, v: List[int], info) -> List[int]:
        if 0 in v or 1 in v:
            raise ValueError("Emirate (level 1) and Base (level 2) cannot be skipped")
        return v


class LocationChainResponse(BaseModel):
    created_locations: List[LocationResponse]
    leaf_location: LocationResponse


class UnitChainItem(BaseModel):
    type: UnitType
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 0
    id: Optional[int] = None


class UnitChainCreate(BaseModel):
    chain: List[UnitChainItem]


class UnitChainResponse(BaseModel):
    created_units: List[UnitResponse]
    leaf_unit: UnitResponse
