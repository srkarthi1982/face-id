import base64
import threading
from datetime import datetime, timezone

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session
from typing import Optional, Tuple, List
from uuid import uuid4

from app.modules.personnel.models import Personnel
from app.modules.personnel.schemas import (
    PersonnelCreate,
    PersonnelUpdate,
    PersonnelResponse,
    PersonnelStats,
    PersonnelSearchFilters,
    PersonnelPushRequest,
    PersonnelPushResponse,
    DevicePushResult,
    PersonPushJobResult,
    PushJobError,
)
from app.modules.master.models import Location
from app.modules.device.client import DeviceHttpClient
from app.modules.device.models import Device
from app.modules.person_mapping.models import DevicePersonMapping
from app.modules.photos.models import PhotoRegistration


def _validate_gender(gender: int) -> None:
    """Validate gender code (0=Unknown, 1=Male, 2=Female)."""
    if gender not in (0, 1, 2):
        raise ValueError(f"Invalid gender code: {gender}. Must be 0, 1, or 2.")


def _check_emp_no_unique(db: Session, emp_no: str, org_id: Optional[int], exclude_id: Optional[int] = None) -> None:
    """Check if employee number is unique within organization."""
    query = select(Personnel).where(Personnel.emp_no == emp_no)
    
    if org_id is not None:
        query = query.where(Personnel.org_id == org_id)
    else:
        # If org_id is None, check for records with NULL org_id
        query = query.where(Personnel.org_id.is_(None))
    
    if exclude_id is not None:
        query = query.where(Personnel.id != exclude_id)
    
    existing = db.execute(query).scalar_one_or_none()
    if existing:
        raise ValueError(f"Employee number '{emp_no}' already exists in this organization.")


def _validate_org_exists(db: Session, org_id: Optional[int]) -> None:
    """Validate that organization (location) exists if provided."""
    if org_id is not None:
        location = db.get(Location, org_id)
        if not location:
            raise ValueError(f"Organization with ID {org_id} does not exist.")


def _validate_department_exists(db: Session, department_id: Optional[int]) -> None:
    """Validate that department (location) exists if provided."""
    if department_id is not None:
        location = db.get(Location, department_id)
        if not location:
            raise ValueError(f"Department with ID {department_id} does not exist.")


def create_personnel(db: Session, payload: PersonnelCreate) -> Personnel:
    """
    Create a new personnel record.
    
    Args:
        db: Database session
        payload: PersonnelCreate schema with data
        
    Returns:
        Created Personnel instance
        
    Raises:
        ValueError: If emp_no is duplicate or org_id doesn't exist
    """
    # Validate gender
    _validate_gender(payload.gender)
    
    # Validate organization exists
    _validate_org_exists(db, payload.org_id)
    
    # Validate department exists if provided
    _validate_department_exists(db, payload.department_id)
    
    # Check emp_no uniqueness
    _check_emp_no_unique(db, payload.emp_no, payload.org_id)
    
    # Generate person_id_internal if not provided
    person_id_internal = payload.person_id_internal or uuid4().hex
    
    personnel = Personnel(
        org_id=payload.org_id,
        emp_no=payload.emp_no,
        person_id_internal=person_id_internal,
        person_id_device=payload.person_id_device,
        full_name=payload.full_name,
        gender=payload.gender,
        email=payload.email,
        phone=payload.phone,
        date_of_birth=payload.date_of_birth,
        nationality=payload.nationality,
        idcard_num=payload.idcard_num,
        id_number=payload.id_number,
        card_no=payload.card_no,
        department_id=payload.department_id,
        position=payload.position,
        hire_date=payload.hire_date,
        permissions=payload.permissions or {},
        pass_time=payload.pass_time,
        push_to_device=payload.push_to_device,
        is_active=payload.is_active,
    )
    
    db.add(personnel)
    db.commit()
    db.refresh(personnel)
    
    return personnel


def get_personnel(db: Session, personnel_id: int) -> Optional[Personnel]:
    """
    Get a single personnel record by ID.
    
    Args:
        db: Database session
        personnel_id: Personnel ID
        
    Returns:
        Personnel instance or None if not found
    """
    return db.get(Personnel, personnel_id)


def update_personnel(db: Session, personnel_id: int, payload: PersonnelUpdate) -> Optional[Personnel]:
    """
    Update a personnel record.
    
    Args:
        db: Database session
        personnel_id: Personnel ID
        payload: PersonnelUpdate schema with updates
        
    Returns:
        Updated Personnel instance or None if not found
        
    Raises:
        ValueError: If emp_no is duplicate or org_id doesn't exist
    """
    personnel = get_personnel(db, personnel_id)
    if not personnel:
        return None
    
    update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
    
    if not update_data:
        return personnel
    
    # Validate gender if being updated
    if "gender" in update_data:
        _validate_gender(update_data["gender"])
    
    # Validate organization if being updated
    if "org_id" in update_data:
        _validate_org_exists(db, update_data["org_id"])
        # Re-check emp_no uniqueness with new org_id
        _check_emp_no_unique(db, personnel.emp_no, update_data["org_id"], exclude_id=personnel_id)
    
    # Validate department if being updated
    if "department_id" in update_data:
        _validate_department_exists(db, update_data["department_id"])
    
    # Check emp_no uniqueness if being updated
    if "emp_no" in update_data:
        _check_emp_no_unique(db, update_data["emp_no"], personnel.org_id, exclude_id=personnel_id)
    
    # Update fields
    for key, value in update_data.items():
        setattr(personnel, key, value)
    
    db.commit()
    db.refresh(personnel)
    
    return personnel


def delete_personnel(db: Session, personnel_id: int) -> Optional[Personnel]:
    """
    Soft delete a personnel record (set is_active=False).
    
    Args:
        db: Database session
        personnel_id: Personnel ID
        
    Returns:
        Deleted Personnel instance or None if not found
    """
    personnel = get_personnel(db, personnel_id)
    if not personnel:
        return None
    
    personnel.is_active = False
    db.commit()
    db.refresh(personnel)
    
    return personnel


def restore_personnel(db: Session, personnel_id: int) -> Optional[Personnel]:
    """
    Restore a soft-deleted personnel record (set is_active=True).
    
    Args:
        db: Database session
        personnel_id: Personnel ID
        
    Returns:
        Restored Personnel instance or None if not found
    """
    personnel = get_personnel(db, personnel_id)
    if not personnel:
        return None
    
    personnel.is_active = True
    db.commit()
    db.refresh(personnel)
    
    return personnel


def list_personnel(
    db: Session,
    org_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "emp_no",
    order: str = "asc",
    filters: Optional[PersonnelSearchFilters] = None,
) -> Tuple[List[Personnel], int]:
    """
    List personnel records with pagination, sorting, and filtering.
    
    Args:
        db: Database session
        org_id: Filter by organization ID
        page: Page number (1-indexed)
        page_size: Number of items per page
        sort_by: Field to sort by (emp_no, full_name, hire_date, created_at)
        order: Sort order (asc, desc)
        filters: Additional search filters
        
    Returns:
        Tuple of (list of Personnel instances, total count)
    """
    # Build base query
    query = select(Personnel)
    
    # Apply org_id filter
    if org_id is not None:
        query = query.where(Personnel.org_id == org_id)
    
    # Apply additional filters
    if filters:
        if filters.emp_no:
            query = query.where(Personnel.emp_no.ilike(f"%{filters.emp_no}%"))
        if filters.full_name:
            query = query.where(Personnel.full_name.ilike(f"%{filters.full_name}%"))
        if filters.email:
            query = query.where(Personnel.email.ilike(f"%{filters.email}%"))
        if filters.gender is not None:
            query = query.where(Personnel.gender == filters.gender)
        if filters.is_active is not None:
            query = query.where(Personnel.is_active == filters.is_active)
        if filters.department_id is not None:
            query = query.where(Personnel.department_id == filters.department_id)
        if filters.search:
            # Search across multiple fields
            search_filter = or_(
                Personnel.emp_no.ilike(f"%{filters.search}%"),
                Personnel.full_name.ilike(f"%{filters.search}%"),
                Personnel.email.ilike(f"%{filters.search}%"),
                Personnel.phone.ilike(f"%{filters.search}%"),
            )
            query = query.where(search_filter)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar_one()
    
    # Apply sorting
    sort_column = getattr(Personnel, sort_by, Personnel.emp_no)
    if order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    results = db.execute(query).scalars().all()
    
    return list(results), total


def get_personnel_stats(db: Session, org_id: Optional[int] = None) -> PersonnelStats:
    """
    Get personnel statistics.
    
    Args:
        db: Database session
        org_id: Filter by organization ID (optional)
        
    Returns:
        PersonnelStats instance with counts
    """
    # Build base query
    base_filters = []
    if org_id is not None:
        base_filters.append(Personnel.org_id == org_id)
    
    # Total count
    total_query = select(func.count()).where(*base_filters).select_from(Personnel)
    total = db.execute(total_query).scalar_one()
    
    # Active count
    active_query = select(func.count()).where(
        *base_filters,
        Personnel.is_active == True
    ).select_from(Personnel)
    active = db.execute(active_query).scalar_one()
    
    # Inactive count
    inactive = total - active
    
    # Count by gender
    gender_query = select(Personnel.gender, func.count()).where(*base_filters).group_by(Personnel.gender)
    gender_results = db.execute(gender_query).all()
    by_gender = {0: 0, 1: 0, 2: 0}
    for gender, count in gender_results:
        by_gender[gender] = count
    
    return PersonnelStats(
        total=total,
        active=active,
        inactive=inactive,
        by_gender=by_gender,
    )


# Permission keys accepted by the device /person/create endpoint (values: 1=Off, 2=On)
_DEVICE_PERMISSION_KEYS = (
    "facePermission",
    "idCardPermission",
    "iDNumberPermission",
    "passwordPermission",
    "fingerPermission",
    "qrCodePermission",
    "faceAndCardPermission",
    "cardAndPasswordPermission",
    "faceAndQrCodePermission",
    "faceAndFingerPermission",
    "faceAndPasswordPermission",
    "fingerAndPasswordPermission",
)


def _build_device_person(personnel: Personnel, person_id_device: str) -> dict:
    """Build the `person` JSON payload for the device /person/create endpoint."""
    person = {
        "id": person_id_device,
        "name": personnel.full_name,
        "facePermission": 2,
    }
    if personnel.idcard_num:
        person["idcardNum"] = personnel.idcard_num
    if personnel.id_number:
        person["iDNumber"] = personnel.id_number
    if personnel.phone:
        # Device accepts digits only
        phone_digits = "".join(c for c in personnel.phone if c.isdigit())
        if phone_digits:
            person["phone"] = phone_digits
    if personnel.position:
        # tag (remarks) is limited to 60 characters
        person["tag"] = personnel.position[:60]

    for key in _DEVICE_PERMISSION_KEYS:
        value = (personnel.permissions or {}).get(key)
        if value in (1, 2):
            person[key] = value

    return person


def _get_push_photo(db: Session, person_id_internal: str, device_id: int) -> Optional[PhotoRegistration]:
    """Pick the registration photo to push: device-specific first, then master (device_id NULL)."""
    photos = db.execute(
        select(PhotoRegistration)
        .where(
            PhotoRegistration.person_id_internal == person_id_internal,
            or_(
                PhotoRegistration.device_id == device_id,
                PhotoRegistration.device_id.is_(None),
            ),
        )
        .order_by(PhotoRegistration.device_id.isnot(None).desc(), PhotoRegistration.id.desc())
    ).scalars().all()
    for photo in photos:
        if photo.img_data is not None or photo.img_url:
            return photo
    return None


def _build_face_payload(photo: PhotoRegistration) -> dict:
    """Build the `face1` JSON payload for the device /person/create endpoint."""
    if not photo.face_id:
        photo.face_id = uuid4().hex
    face = {"faceId": photo.face_id}
    if photo.img_data is not None:
        face["base64"] = base64.b64encode(photo.img_data).decode()
    elif photo.img_url:
        face["url"] = photo.img_url
    return face


def _upsert_device_mapping(
    db: Session,
    personnel: Personnel,
    device_id: int,
    person_id_device: str,
    photo: Optional[PhotoRegistration],
) -> None:
    mapping = db.execute(
        select(DevicePersonMapping).where(
            DevicePersonMapping.person_id_internal == personnel.person_id_internal,
            DevicePersonMapping.device_id == device_id,
        )
    ).scalars().first()
    if not mapping:
        mapping = DevicePersonMapping(
            person_id_internal=personnel.person_id_internal,
            device_id=device_id,
            photo_ids={},
        )
        db.add(mapping)
    mapping.person_id_device = person_id_device
    if photo:
        photo_ids = dict(mapping.photo_ids or {})
        photo_ids["face1"] = photo.id
        mapping.photo_ids = photo_ids
    mapping.synced_at = datetime.now(timezone.utc)


def _prepare_push(db: Session, personnel_id: int) -> Optional[Tuple[Personnel, str, dict]]:
    """
    Validate a personnel record for pushing and build the device payload.

    Returns (personnel, person_id_device, person_payload), or None if not found.

    Raises:
        ValueError: If the personnel record cannot be pushed
    """
    personnel = get_personnel(db, personnel_id)
    if not personnel:
        return None
    if not personnel.is_active:
        raise ValueError("Cannot push inactive personnel to devices.")
    if not personnel.person_id_internal:
        raise ValueError("Personnel has no person_id_internal; cannot push to devices.")

    # Device person id allows numbers and English letters only
    person_id_device = personnel.person_id_device or personnel.person_id_internal
    if not person_id_device.isalnum():
        raise ValueError(f"Person ID '{person_id_device}' is not valid for devices (alphanumeric only).")

    person = _build_device_person(personnel, person_id_device)
    return personnel, person_id_device, person


def _push_person_to_device(
    db: Session,
    personnel: Personnel,
    person: dict,
    person_id_device: str,
    device: Device,
    include_photo: bool,
) -> DevicePushResult:
    """Push one personnel record to one device, staging the mapping on success."""
    photo = None
    faces = []
    if include_photo:
        photo = _get_push_photo(db, personnel.person_id_internal, device.id)
        if photo:
            faces.append(_build_face_payload(photo))

    client = DeviceHttpClient(device.ip_address, device.port, device.api_password)
    response = client.create_person(person, faces)

    success = bool(response.get("success"))
    if success:
        _upsert_device_mapping(db, personnel, device.id, person_id_device, photo)

    return DevicePushResult(
        device_id=device.id,
        device_name=device.device_name,
        success=success,
        code=response.get("code"),
        msg=response.get("msg"),
    )


def _finalize_push(
    db: Session,
    personnel: Personnel,
    person_id_device: str,
    results: List[DevicePushResult],
) -> None:
    """Commit if at least one device succeeded, else roll everything back."""
    if any(r.success for r in results):
        if not personnel.person_id_device:
            personnel.person_id_device = person_id_device
        personnel.push_to_device = True
        db.commit()
    else:
        db.rollback()


def push_personnel_to_devices(
    db: Session,
    personnel_id: int,
    payload: PersonnelPushRequest,
) -> Optional[PersonnelPushResponse]:
    """
    Push a personnel record to one or more devices via the device
    /person/create endpoint, recording a device_person_mapping per success.

    Args:
        db: Database session
        personnel_id: Personnel ID
        payload: Target device IDs and push options

    Returns:
        PersonnelPushResponse with per-device results, or None if personnel not found

    Raises:
        ValueError: If the personnel record cannot be pushed
    """
    prepared = _prepare_push(db, personnel_id)
    if prepared is None:
        return None
    personnel, person_id_device, person = prepared

    devices = db.execute(
        select(Device).where(Device.id.in_(payload.device_ids))
    ).scalars().all()
    devices_by_id = {d.id: d for d in devices}

    results: List[DevicePushResult] = []
    for device_id in payload.device_ids:
        device = devices_by_id.get(device_id)
        if not device:
            results.append(DevicePushResult(
                device_id=device_id,
                success=False,
                code="DEVICE_NOT_FOUND",
                msg=f"Device with ID {device_id} does not exist",
            ))
            continue
        results.append(_push_person_to_device(
            db, personnel, person, person_id_device, device, payload.include_photo,
        ))

    _finalize_push(db, personnel, person_id_device, results)

    pushed = sum(1 for r in results if r.success)
    return PersonnelPushResponse(
        personnel_id=personnel_id,
        person_id_device=person_id_device,
        pushed=pushed,
        failed=len(results) - pushed,
        results=results,
    )


def push_one_for_job(
    db: Session,
    personnel_id: int,
    device_ids: List[int],
    include_photo: bool,
    cancel_event: threading.Event,
) -> PersonPushJobResult:
    """
    Push one personnel record to devices for a bulk push job.

    Unlike push_personnel_to_devices, this never raises: validation failures
    and unexpected errors become per-person results so the job always drains.
    The cancel_event is checked between devices; work already done is still
    committed via the normal per-person boundary.
    """
    try:
        try:
            prepared = _prepare_push(db, personnel_id)
        except ValueError as e:
            return PersonPushJobResult(
                personnel_id=personnel_id, ok=False, pushed=0, failed=0, results=[],
                error=PushJobError(code="PERSON_INVALID", message=str(e)),
            )
        if prepared is None:
            return PersonPushJobResult(
                personnel_id=personnel_id, ok=False, pushed=0, failed=0, results=[],
                error=PushJobError(code="PERSON_NOT_FOUND", message="Personnel not found"),
            )
        personnel, person_id_device, person = prepared

        devices = db.execute(
            select(Device).where(Device.id.in_(device_ids))
        ).scalars().all()
        devices_by_id = {d.id: d for d in devices}

        results: List[DevicePushResult] = []
        for device_id in device_ids:
            if cancel_event.is_set():
                break
            device = devices_by_id.get(device_id)
            if not device:
                results.append(DevicePushResult(
                    device_id=device_id,
                    success=False,
                    code="DEVICE_NOT_FOUND",
                    msg=f"Device with ID {device_id} does not exist",
                ))
                continue
            results.append(_push_person_to_device(
                db, personnel, person, person_id_device, device, include_photo,
            ))

        _finalize_push(db, personnel, person_id_device, results)

        pushed = sum(1 for r in results if r.success)
        failed = len(results) - pushed
        return PersonPushJobResult(
            personnel_id=personnel_id,
            ok=failed == 0 and len(results) == len(device_ids),
            pushed=pushed,
            failed=failed,
            results=results,
        )
    except Exception as e:  # noqa: BLE001 — a worker exception must never vanish into the executor
        db.rollback()
        return PersonPushJobResult(
            personnel_id=personnel_id, ok=False, pushed=0, failed=0, results=[],
            error=PushJobError(code="INTERNAL_ERROR", message=str(e)),
        )


def search_personnel(
    db: Session,
    search_term: str,
    org_id: Optional[int] = None,
    limit: int = 50,
) -> List[Personnel]:
    """
    Search personnel by term across multiple fields.
    
    Args:
        db: Database session
        search_term: Search term
        org_id: Filter by organization ID
        limit: Maximum number of results
        
    Returns:
        List of matching Personnel instances
    """
    query = select(Personnel).where(
        or_(
            Personnel.emp_no.ilike(f"%{search_term}%"),
            Personnel.full_name.ilike(f"%{search_term}%"),
            Personnel.email.ilike(f"%{search_term}%"),
            Personnel.phone.ilike(f"%{search_term}%"),
            Personnel.nationality.ilike(f"%{search_term}%"),
        )
    )
    
    if org_id is not None:
        query = query.where(Personnel.org_id == org_id)
    
    query = query.limit(limit)
    
    results = db.execute(query).scalars().all()
    return list(results)
