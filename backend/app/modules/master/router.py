from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_db, require_permission
from app.core.permissions import PermissionCode
from app.modules.master import service
from app.modules.master.models import LocationType, UnitType
from app.modules.master.schemas import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse, DepartmentTreeItem,
    LocationCreate, LocationUpdate, LocationResponse, LocationTreeItem,
    TimingCreate, TimingUpdate, TimingResponse,
    UnitCreate, UnitUpdate, UnitResponse, UnitTreeItem,
    LocationChainCreate, LocationChainResponse, UnitChainCreate, UnitChainResponse
)

router = APIRouter(prefix="/master-data", tags=["master-data"])


@router.get("/locations/tree", response_model=List[LocationTreeItem])
def get_locations_tree_endpoint(
    unit_id: Optional[int] = Query(None, description="Filter by unit ID (Command level)"),
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.LOCATION_READ))
):
    """Get full nested location tree."""
    return service.get_location_tree(db, unit_id)


@router.get("/locations", response_model=List[LocationResponse])
def get_locations_endpoint(
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.LOCATION_READ))
):
    """Get flat list of all locations."""
    return service.get_locations_flat(db)


@router.get("/locations/by-type/{location_type}", response_model=List[LocationResponse])
def get_locations_by_type_endpoint(
    location_type: LocationType,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.LOCATION_READ))
):
    """Get all locations of a specific type."""
    return service.get_locations_by_type(db, location_type)


@router.get("/locations/valid-parents/{child_type}", response_model=List[LocationResponse])
def get_valid_parent_locations_endpoint(
    child_type: LocationType,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.LOCATION_READ))
):
    """Get all valid parent locations for a given child type."""
    return service.get_valid_parent_locations(db, child_type)


@router.get("/locations/{location_id}", response_model=LocationResponse)
def get_location_endpoint(
    location_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.LOCATION_READ))
):
    """Get single location by ID."""
    return service.get_location_by_id(db, location_id)


@router.post("/locations", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location_endpoint(
    location: LocationCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.LOCATION_WRITE))
):
    """Create new location."""
    if location.parent_id is not None:
        parent = service.get_location_by_id(db, location.parent_id)
        if not service.validate_location_parent(location.type, parent.type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid parent type {parent.type} for location type {location.type}"
            )
    return service.create_location(db, location)


@router.post("/locations/with-full-chain", response_model=LocationChainResponse, status_code=status.HTTP_201_CREATED)
def create_location_with_full_chain_endpoint(
    chain_data: LocationChainCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.LOCATION_WRITE))
):
    """Create full location hierarchy chain atomically."""
    leaf_location = service.create_location_with_full_chain(
        db,
        [item.model_dump() for item in chain_data.chain],
        chain_data.skip_indices,
        chain_data.unit_id
    )
    
    created_locations = [
        LocationResponse(
            id=loc.id,
            name=loc.name,
            type=loc.type,
            parent_id=loc.parent_id,
            unit_id=loc.unit_id,
            unit_name=loc.unit.name if loc.unit else None,
            path=loc.path,
            is_active=loc.is_active,
            sort_order=loc.sort_order,
            created_at=loc.created_at,
            updated_at=loc.updated_at,
        )
        for loc in [leaf_location]
    ]
    
    return LocationChainResponse(
        created_locations=created_locations,
        leaf_location=created_locations[0]
    )


@router.put("/locations/{location_id}", response_model=LocationResponse)
def update_location_endpoint(
    location_id: int,
    location: LocationUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(PermissionCode.LOCATION_WRITE))
):
    """Update location."""
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is required"
        )
    return service.update_location(db, location_id, location)


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location_endpoint(
    location_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.LOCATION_WRITE))
):
    """Delete location."""
    service.delete_location(db, location_id)


@router.get("/departments/tree", response_model=List[DepartmentTreeItem])
def get_departments_tree_endpoint(
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.DEPARTMENT_READ, PermissionCode.PERSONNEL_READ))
):
    """Get full nested department tree."""
    return service.get_department_tree(db)


@router.get("/departments", response_model=List[DepartmentResponse])
def get_departments_endpoint(
    active_only: bool = Query(False, description="Only return active departments"),
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.DEPARTMENT_READ, PermissionCode.PERSONNEL_READ))
):
    """Get flat list of departments."""
    return service.get_departments(db, active_only)


@router.get("/departments/{department_id}", response_model=DepartmentResponse)
def get_department_endpoint(
    department_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.DEPARTMENT_READ, PermissionCode.PERSONNEL_READ))
):
    """Get single department by ID."""
    return service.get_department_by_id(db, department_id)


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department_endpoint(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.DEPARTMENT_WRITE))
):
    """Create department."""
    return service.create_department(db, department)


@router.put("/departments/{department_id}", response_model=DepartmentResponse)
def update_department_endpoint(
    department_id: int,
    department: DepartmentUpdate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.DEPARTMENT_WRITE))
):
    """Update department."""
    return service.update_department(db, department_id, department)


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department_endpoint(
    department_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.DEPARTMENT_WRITE))
):
    """Delete department."""
    service.delete_department(db, department_id)


@router.get("/timings", response_model=List[TimingResponse])
def get_timings_endpoint(
    active_only: bool = Query(False, description="Only return active timings"),
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.TIMING_READ))
):
    """Get department timings."""
    return service.get_timings(db, active_only)


@router.get("/timings/{timing_id}", response_model=TimingResponse)
def get_timing_endpoint(
    timing_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.TIMING_READ))
):
    """Get timing by ID."""
    return service._timing_response(service.get_timing_by_id(db, timing_id))


@router.post("/timings", response_model=TimingResponse, status_code=status.HTTP_201_CREATED)
def create_timing_endpoint(
    timing: TimingCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.TIMING_WRITE))
):
    """Create department timing."""
    return service.create_timing(db, timing)


@router.put("/timings/{timing_id}", response_model=TimingResponse)
def update_timing_endpoint(
    timing_id: int,
    timing: TimingUpdate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.TIMING_WRITE))
):
    """Update department timing."""
    return service.update_timing(db, timing_id, timing)


@router.delete("/timings/{timing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timing_endpoint(
    timing_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.TIMING_WRITE))
):
    """Delete department timing."""
    service.delete_timing(db, timing_id)


@router.get("/units/tree", response_model=List[UnitTreeItem])
def get_units_tree_endpoint(
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.UNIT_READ))
):
    """Get full nested unit tree."""
    return service.get_unit_tree(db)


@router.get("/units", response_model=List[UnitResponse])
def get_units_endpoint(
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.UNIT_READ))
):
    """Get flat list of all units."""
    return service.get_units_flat(db)


@router.get("/units/by-type/{unit_type}", response_model=List[UnitResponse])
def get_units_by_type_endpoint(
    unit_type: UnitType,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.UNIT_READ))
):
    """Get all units of a specific type."""
    return service.get_units_by_type(db, unit_type)


@router.get("/units/valid-parents/{child_type}", response_model=List[UnitResponse])
def get_valid_parent_units_endpoint(
    child_type: UnitType,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.UNIT_READ))
):
    """Get all valid parent units for a given child type."""
    return service.get_valid_parent_units(db, child_type)


@router.get("/units/commands", response_model=List[UnitResponse])
def get_command_units_endpoint(
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.UNIT_READ))
):
    """Get only Command-level units for location assignment dropdown."""
    return service.get_command_units(db)


@router.get("/units/{unit_id}", response_model=UnitResponse)
def get_unit_endpoint(
    unit_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.UNIT_READ))
):
    """Get single unit by ID."""
    return service.get_unit_by_id(db, unit_id)


@router.post("/units", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit_endpoint(
    unit: UnitCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.UNIT_WRITE))
):
    """Create new unit."""
    if unit.parent_id is not None:
        parent = service.get_unit_by_id(db, unit.parent_id)
        if not service.validate_unit_parent(unit.type, parent.type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid parent type {parent.type} for unit type {unit.type}"
            )
    return service.create_unit(db, unit)


@router.post("/units/with-full-chain", response_model=UnitChainResponse, status_code=status.HTTP_201_CREATED)
def create_unit_with_full_chain_endpoint(
    chain_data: UnitChainCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.UNIT_WRITE))
):
    """Create full unit hierarchy chain atomically."""
    leaf_unit = service.create_unit_with_full_chain(
        db,
        [item.model_dump() for item in chain_data.chain]
    )
    
    created_units = [
        UnitResponse(
            id=unit.id,
            name=unit.name,
            code=unit.code,
            description=unit.description,
            type=unit.type,
            parent_id=unit.parent_id,
            path=unit.path,
            is_active=unit.is_active,
            sort_order=unit.sort_order,
            created_at=unit.created_at,
            updated_at=unit.updated_at,
        )
        for unit in [leaf_unit]
    ]
    
    return UnitChainResponse(
        created_units=created_units,
        leaf_unit=created_units[0]
    )


@router.put("/units/{unit_id}", response_model=UnitResponse)
def update_unit_endpoint(
    unit_id: int,
    unit: UnitUpdate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.UNIT_WRITE))
):
    """Update unit."""
    return service.update_unit(db, unit_id, unit)


@router.delete("/units/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit_endpoint(
    unit_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(PermissionCode.UNIT_WRITE))
):
    """Delete unit."""
    service.delete_unit(db, unit_id)
