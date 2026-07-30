from sqlalchemy.orm import Session, joinedload
from sqlalchemy import event, cast
from app.modules.master.models import Location, Unit, UnitType, LocationType
from app.modules.master.schemas import LocationCreate, LocationUpdate, UnitCreate, UnitUpdate
from fastapi import HTTPException, status
from typing import List, Dict, Optional

LOCATION_VALID_PARENTS: Dict[LocationType, List[LocationType]] = {
    LocationType.EMIRATE: [],
    LocationType.BASE: [LocationType.EMIRATE],
    LocationType.LOCATION: [LocationType.BASE],
    LocationType.BUILDING: [LocationType.BASE, LocationType.LOCATION],
    LocationType.AREA: [LocationType.BASE, LocationType.LOCATION, LocationType.BUILDING],
}

UNIT_VALID_PARENTS: Dict[UnitType, List[UnitType]] = {
    UnitType.FORCE: [],
    UnitType.COMMAND: [UnitType.FORCE],
    UnitType.BATTALION: [UnitType.COMMAND],
    UnitType.UNIT: [UnitType.BATTALION],
}


def validate_location_parent(child_type: LocationType, parent_type: Optional[LocationType]) -> bool:
    """Validate that parent type is valid for child type."""
    valid_parents = LOCATION_VALID_PARENTS.get(child_type, [])
    if not valid_parents:
        return parent_type is None
    return parent_type in valid_parents


def validate_unit_parent(child_type: UnitType, parent_type: Optional[UnitType]) -> bool:
    """Validate that parent type is valid for child type."""
    valid_parents = UNIT_VALID_PARENTS.get(child_type, [])
    if not valid_parents:
        return parent_type is None
    return parent_type in valid_parents


def get_valid_location_parents(child_type: LocationType) -> List[LocationType]:
    """Get list of valid parent types for a child type."""
    return LOCATION_VALID_PARENTS.get(child_type, [])


def get_valid_unit_parents(child_type: UnitType) -> List[UnitType]:
    """Get list of valid parent types for a child type."""
    return UNIT_VALID_PARENTS.get(child_type, [])


def _compute_location_path(db: Session, location: Location) -> str:
    """Compute path string for location."""
    if location.parent_id is None:
        return f"/{location.name}"
    parent = db.query(Location).filter(Location.id == location.parent_id).first()
    if not parent:
        return f"/{location.name}"
    return f"{parent.path}/{location.name}"


def get_location_tree(db: Session, unit_id: Optional[int] = None):
    """Get full nested location tree.
    
    Unit filtering behavior (when unit_id is provided):
    1. Find all locations with matching unit_id (exact match only)
    2. Collect all ancestors of matching locations up to root level
    3. Also include descendants of matching locations (even if they have unit_id=None)
    4. Build tree including only: ancestors + matching locations + their descendants
    
    This ensures:
    - Organizational hierarchy (Emirate/Base) is preserved for matching locations
    - Non-matching branches are pruned from the tree
    - Locations without unit_id under a matching location are shown (inherit from parent)
    
    When unit_id is None, returns full unfiltered tree.
    """
    from app.modules.master.schemas import LocationTreeItem
    
    if unit_id is None:
        # No filter - return full tree with eager loading
        query = db.query(Location).options(
            joinedload(Location.children).joinedload(Location.unit)
        ).filter(Location.parent_id.is_(None)).order_by(Location.name)
        
        locations = query.all()
        
        def build_tree_full(loc: Location) -> LocationTreeItem:
            return LocationTreeItem(
                id=loc.id,
                name=loc.name,
                type=loc.type,
                path=loc.path,
                is_active=loc.is_active,
                sort_order=loc.sort_order,
                parent_id=loc.parent_id,
                unit_id=loc.unit_id,
                unit_name=loc.unit.name if loc.unit else None,
                children=[build_tree_full(child) for child in sorted(loc.children, key=lambda x: x.name)]
            )
        
        return [build_tree_full(loc) for loc in sorted(locations, key=lambda x: x.name)]
    
    # Unit filter provided - use ancestor collection approach
    
    # Step 1: Find all locations with exact unit_id match
    matching_locs = db.query(Location).filter(
        Location.unit_id == unit_id
    ).all()
    
    if not matching_locs:
        return []
    
    # Step 2: Collect all ancestor IDs up to root level
    ancestor_ids = set()
    for loc in matching_locs:
        current_id = loc.parent_id
        while current_id is not None:
            ancestor_ids.add(current_id)
            # Fetch parent to continue up the chain
            parent = db.query(Location).filter(Location.id == current_id).first()
            if parent:
                current_id = parent.parent_id
            else:
                break
    
    # Step 3: Collect all descendants of matching locations
    descendant_ids = set()
    def collect_descendants(parent_id: int):
        children = db.query(Location).filter(
            Location.parent_id == parent_id
        ).all()
        for child in children:
            descendant_ids.add(child.id)
            collect_descendants(child.id)
    
    for loc in matching_locs:
        collect_descendants(loc.id)
    
    # Step 4: Build set of all relevant location IDs
    relevant_ids = ancestor_ids | {loc.id for loc in matching_locs} | descendant_ids
    
    # Step 5: Fetch all relevant locations with eager loading
    relevant_locs = db.query(Location).options(
        joinedload(Location.unit)
    ).filter(Location.id.in_(relevant_ids)).all()
    
    # Step 6: Build tree structure from relevant locations
    loc_dict = {loc.id: loc for loc in relevant_locs}
    
    # Find root nodes (no parent or parent not in relevant set)
    roots = [
        loc for loc in relevant_locs 
        if loc.parent_id is None or loc.parent_id not in relevant_ids
    ]
    
    # Group children by parent_id for efficient lookup
    children_by_parent: Dict[int, List[Location]] = {}
    for loc in relevant_locs:
        if loc.parent_id is not None:
            if loc.parent_id not in children_by_parent:
                children_by_parent[loc.parent_id] = []
            children_by_parent[loc.parent_id].append(loc)
    
    def build_tree(loc: Location) -> LocationTreeItem:
        children = children_by_parent.get(loc.id, [])
        return LocationTreeItem(
            id=loc.id,
            name=loc.name,
            type=loc.type,
            path=loc.path,
            is_active=loc.is_active,
            sort_order=loc.sort_order,
            parent_id=loc.parent_id,
            unit_id=loc.unit_id,
            unit_name=loc.unit.name if loc.unit else None,
            children=[build_tree(child) for child in sorted(children, key=lambda x: x.name)]
        )
    
    return [build_tree(root) for root in sorted(roots, key=lambda x: x.name)]


def get_locations_flat(db: Session):
    """Get flat list of all locations."""
    from app.modules.master.schemas import LocationResponse
    locations = db.query(Location).options(
        joinedload(Location.unit)
    ).order_by(Location.name).all()
    return locations


def get_locations_by_type(db: Session, location_type: LocationType):
    """Get all locations of a specific type."""
    from app.modules.master.schemas import LocationResponse
    # Convert enum member to its string value for PostgreSQL compatibility
    locations = db.query(Location).options(
        joinedload(Location.unit)
    ).filter(Location.type == location_type.value).order_by(Location.name).all()
    return locations


def get_valid_parent_locations(db: Session, child_type: LocationType):
    """Get all valid parent locations for a given child type."""
    valid_parent_types = get_valid_location_parents(child_type)
    if not valid_parent_types:
        return []
    # Use enum members directly - SQLAlchemy will handle the conversion
    locations = db.query(Location).filter(
        Location.type.in_(valid_parent_types)
    ).options(
        joinedload(Location.unit)
    ).order_by(Location.name).all()
    return locations


def get_location_by_id(db: Session, location_id: int) -> Location:
    """Get single location by ID."""
    location = db.query(Location).options(
        joinedload(Location.unit)
    ).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


def create_location(db: Session, location: LocationCreate) -> Location:
    """Create new location."""
    db_location = Location(
        name=location.name,
        parent_id=location.parent_id,
        unit_id=location.unit_id,
        sort_order=location.sort_order,
    )
    db.add(db_location)
    db.flush()
    db_location.path = _compute_location_path(db, db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def update_location(db: Session, location_id: int, location: LocationUpdate) -> Location:
    """Update location."""
    db_location = get_location_by_id(db, location_id)
    
    update_data = location.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_location, field, value)
    
    if location.parent_id is not None or location.name is not None:
        db_location.path = _compute_location_path(db, db_location)
        _update_children_paths(db, db_location.id)
    
    db.commit()
    db.refresh(db_location)
    return db_location


def _update_children_paths(db: Session, parent_id: int):
    """Recursively update paths for all children."""
    children = db.query(Location).filter(Location.parent_id == parent_id).all()
    for child in children:
        child.path = _compute_location_path(db, child)
        db.add(child)
    db.commit()
    for child in children:
        _update_children_paths(db, child.id)


def create_location_with_full_chain(
    db: Session,
    chain: List[Dict],
    skip_indices: Optional[List[int]] = None,
    unit_id: Optional[int] = None
) -> Location:
    """
    Create full hierarchy chain atomically.
    
    Args:
        db: Database session
        chain: List of dicts with keys: type, name, code (optional)
               Example: [
                   {"type": "emirate", "name": "Dubai"},
                   {"type": "base", "name": "Base A"},
                   {"type": "location", "name": "Location B"},
                   {"type": "building", "name": "Building C"},
                   {"type": "area", "name": "Area D"}
               ]
        skip_indices: List of indices to skip (0-based, emirate cannot be skipped)
        unit_id: Optional unit ID to assign to Location level and below
    
    Returns:
        The leaf location created
    
    Raises:
        HTTPException: If validation fails or chain is invalid
    """
    if skip_indices is None:
        skip_indices = []
    
    if len(chain) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chain must have at least 1 level"
        )
    
    if 0 in skip_indices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Emirate (level 1) cannot be skipped"
        )
    
    created_locations = []
    parent_location = None
    
    for i, item in enumerate(chain):
        if i in skip_indices:
            continue
        
        location_type = LocationType(item["type"])
        
        # Check if using existing location
        existing_id = item.get("id")
        if existing_id is not None:
            # Use existing location
            db_location = db.query(Location).filter(Location.id == existing_id).first()
            if not db_location:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Location with id {existing_id} not found"
                )
            # Update parent if needed
            if parent_location is not None and db_location.parent_id != parent_location.id:
                db_location.parent_id = parent_location.id
            # Validate parent type
            if i > 0 and parent_location is not None:
                if not validate_location_parent(location_type, parent_location.type):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid parent type {parent_location.type} for child type {location_type}"
                    )
        else:
            # Create new location
            if i > 0 and parent_location is not None:
                if not validate_location_parent(location_type, parent_location.type):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid parent type {parent_location.type} for child type {location_type}"
                    )
                
                # Check for duplicate name under the same parent
                existing_location = db.query(Location).filter(
                    Location.name == item["name"],
                    Location.type == location_type,
                    Location.parent_id == parent_location.id
                ).first()
                
                if existing_location:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{location_type.value.capitalize()} '{item['name']}' already exists under this parent"
                    )
            
            # unit_id applies only to Location level and below (not Emirate/Base)
            unit_id_for_level = None
            if unit_id is not None and location_type in [LocationType.LOCATION, LocationType.BUILDING, LocationType.AREA]:
                unit_id_for_level = unit_id
            
            db_location = Location(
                name=item["name"],
                type=location_type,
                parent_id=parent_location.id if parent_location else None,
                unit_id=unit_id_for_level,
                sort_order=item.get("sort_order", 0),
            )
            db.add(db_location)
            db.flush()
            db_location.path = _compute_location_path(db, db_location)
            created_locations.append(db_location)
        
        parent_location = db_location
    
    db.commit()
    
    if not created_locations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No locations created (all levels skipped?)"
        )
    
    return created_locations[-1]


def create_unit_with_full_chain(
    db: Session,
    chain: List[Dict],
) -> Unit:
    """
    Create or update full hierarchy chain atomically for units.
    
    Args:
        db: Database session
        chain: List of dicts with keys: type, name, code (optional), description (optional), id (optional)
               Example: [
                   {"type": "force", "name": "Force Alpha", "code": "F001"},
                   {"type": "command", "name": "Command Beta", "code": "C001", "id": 5},
                   {"type": "battalion", "name": "Battalion Gamma", "code": "B001"},
                   {"type": "unit", "name": "Unit Delta", "code": "U001"}
               ]
    
    Returns:
        The leaf unit created/updated
    
    Raises:
        HTTPException: If validation fails or chain is invalid
    """
    if len(chain) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chain must have at least 1 level"
        )
    
    created_units = []
    parent_unit = None
    
    for i, item in enumerate(chain):
        unit_type = UnitType(item["type"])
        
        if i > 0 and parent_unit is not None:
            if not validate_unit_parent(unit_type, parent_unit.type):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid parent type {parent_unit.type} for child type {unit_type}"
                )
        
        # Check if updating existing unit
        if "id" in item and item["id"] is not None:
            db_unit = db.query(Unit).filter(Unit.id == item["id"]).first()
            if not db_unit:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Unit with id {item['id']} not found"
                )
            # Update existing unit
            db_unit.name = item["name"]
            db_unit.code = item.get("code")
            db_unit.description = item.get("description")
            db_unit.parent_id = parent_unit.id if parent_unit else None
            db_unit.sort_order = item.get("sort_order", 0)
        else:
            # Create new unit
            db_unit = Unit(
                name=item["name"],
                code=item.get("code"),
                description=item.get("description"),
                type=unit_type,
                parent_id=parent_unit.id if parent_unit else None,
                sort_order=item.get("sort_order", 0),
            )
            db.add(db_unit)
        
        db.flush()
        db_unit.path = _compute_unit_path(db, db_unit)
        created_units.append(db_unit)
        parent_unit = db_unit
    
    db.commit()
    
    if not created_units:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No units created"
        )
    
    return created_units[-1]


def delete_location(db: Session, location_id: int) -> None:
    """Delete location if not referenced."""
    location = get_location_by_id(db, location_id)
    
    if location.children:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete location with children"
        )
    
    db.delete(location)
    db.commit()


def _compute_unit_path(db: Session, unit: Unit) -> str:
    """Compute path string for unit."""
    if unit.parent_id is None:
        return f"/{unit.name}"
    parent = db.query(Unit).filter(Unit.id == unit.parent_id).first()
    if not parent:
        return f"/{unit.name}"
    return f"{parent.path}/{unit.name}"


def get_unit_tree(db: Session):
    """Get full nested unit tree."""
    from app.modules.master.schemas import UnitTreeItem
    
    units = db.query(Unit).options(
        joinedload(Unit.children)
    ).filter(Unit.parent_id.is_(None)).order_by(Unit.code).all()
    
    def build_tree(unit: Unit) -> UnitTreeItem:
        return UnitTreeItem(
            id=unit.id,
            name=unit.name,
            code=unit.code,
            description=unit.description,
            type=unit.type,
            path=unit.path,
            is_active=unit.is_active,
            sort_order=unit.sort_order,
            children=[build_tree(child) for child in sorted(unit.children, key=lambda x: (x.code or '', x.name))]
        )
    
    return [build_tree(unit) for unit in units]


def get_units_flat(db: Session):
    """Get flat list of all units."""
    from app.modules.master.schemas import UnitResponse
    return db.query(Unit).order_by(Unit.name).all()


def get_units_by_type(db: Session, unit_type: UnitType):
    """Get all units of a specific type."""
    from app.modules.master.schemas import UnitResponse
    # Convert enum member to its string value for PostgreSQL compatibility
    units = db.query(Unit).filter(Unit.type == unit_type.value).order_by(Unit.name).all()
    return units


def get_valid_parent_units(db: Session, child_type: UnitType):
    """Get all valid parent units for a given child type."""
    valid_parent_types = get_valid_unit_parents(child_type)
    if not valid_parent_types:
        return []
    # Convert enum members to their string values for PostgreSQL compatibility
    valid_type_values = [t.value for t in valid_parent_types]
    units = db.query(Unit).filter(
        Unit.type.in_(valid_type_values)
    ).order_by(Unit.name).all()
    return units


def get_unit_by_id(db: Session, unit_id: int) -> Unit:
    """Get single unit by ID."""
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


def create_unit(db: Session, unit: UnitCreate) -> Unit:
    """Create new unit."""
    db_unit = Unit(
        name=unit.name,
        code=unit.code,
        description=unit.description,
        type=unit.type,
        parent_id=unit.parent_id,
        sort_order=unit.sort_order,
    )
    db.add(db_unit)
    db.flush()
    db_unit.path = _compute_unit_path(db, db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit


def update_unit(db: Session, unit_id: int, unit: UnitUpdate) -> Unit:
    """Update unit."""
    db_unit = get_unit_by_id(db, unit_id)
    
    update_data = unit.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_unit, field, value)
    
    if unit.parent_id is not None or unit.name is not None:
        db_unit.path = _compute_unit_path(db, db_unit)
        _update_unit_children_paths(db, db_unit.id)
    
    db.commit()
    db.refresh(db_unit)
    return db_unit


def _update_unit_children_paths(db: Session, parent_id: int):
    """Recursively update paths for all unit children."""
    children = db.query(Unit).filter(Unit.parent_id == parent_id).all()
    for child in children:
        child.path = _compute_unit_path(db, child)
        db.add(child)
    db.commit()
    for child in children:
        _update_unit_children_paths(db, child.id)


def get_command_units(db: Session) -> List[Unit]:
    """Get only Command-level units for location assignment dropdown."""
    return db.query(Unit).filter(Unit.type == UnitType.COMMAND).order_by(Unit.name).all()


def delete_unit(db: Session, unit_id: int) -> None:
    """Delete unit if not referenced."""
    unit = get_unit_by_id(db, unit_id)
    
    if unit.children:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete unit with children"
        )
    
    location_count = db.query(Location).filter(Location.unit_id == unit_id).count()
    if location_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete unit referenced by {location_count} location(s)"
        )
    
    # Device unit_id check removed - not yet implemented
    # from app.modules.device.models import Device
    # device_count = db.query(Device).filter(Device.unit_id == unit_id).count()
    # if device_count > 0:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail=f"Cannot delete unit referenced by {device_count} device(s)"
    #     )
    
    db.delete(unit)
    db.commit()
