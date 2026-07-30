import ipaddress
import logging
import socket
import httpx
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select, or_, and_
from sqlalchemy.orm import Session

from app.modules.device.models import Device
from app.modules.device.schemas import (
    DeviceCreate,
    DeviceResponse,
    DeviceUpdate,
    DiscoveredDevice,
)

logger = logging.getLogger(__name__)


def get_all(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search_text: str | None = None,
    status: str | None = None,
) -> tuple[list[DeviceResponse], int]:
    from app.modules.master.models import Location

    query = select(Device)
    search_conditions: list = []
    status_conditions: list = []

    # --- Search across all visible columns (OR logic) ---
    if search_text:
        # device_name, ip_address, serial_number, sdk_version (always available on Device)
        search_conditions.append(Device.device_name.ilike(f"%{search_text}%"))
        search_conditions.append(Device.ip_address.ilike(f"%{search_text}%"))
        search_conditions.append(Device.serial_number.ilike(f"%{search_text}%"))
        search_conditions.append(
            Device.sdk_version.ilike(f"%{search_text}%")
        )
        # location — outer join so devices without location still appear
        query = query.outerjoin(Location, Location.id == Device.location_id)
        # Match location path OR no location (NULL)
        search_conditions.append(Location.path.ilike(f"%{search_text}%"))

    # --- Status filter (AND logic — applies on top of search) ---
    if status:
        status_conditions.append(Device.status == status)

    # Combine: (any search column MATCH) AND (status match if given)
    all_conditions: list = []
    if search_conditions:
        all_conditions.append(or_(*search_conditions))
    all_conditions.extend(status_conditions)

    if all_conditions:
        query = query.where(and_(*all_conditions))

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    devices = (
        db.execute(
            query.order_by(Device.device_name)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .scalars()
        .all()
    )
    return [_device_to_response(d) for d in devices], total


def get_one(db: Session, id: int) -> Device | None:
    return db.get(Device, id)


def refresh_device(db: Session, id: int) -> DeviceResponse | None:
    device = get_one(db, id)
    if not device:
        return None
    
    port_open = _check_port(device.ip_address, device.port, timeout=2)
    device.status = "online" if port_open else "offline"
    device.last_seen_at = datetime.now(timezone.utc)
    
    if port_open:
        try:
            device_info = _fetch_device_info(device.ip_address, device.port, device.api_password)
            if device_info:
                device.serial_number = device_info.get("serial_number") or device.serial_number
                device.firmware_version = device_info.get("firmware_version") or device.firmware_version
                device.sdk_version = device_info.get("sdk_version") or device.sdk_version
        except Exception as e:
            logger.warning(f"Failed to fetch device info from {device.ip_address}: {e}")
    
    db.commit()
    db.refresh(device)
    return DeviceResponse.model_validate(device)


def create(db: Session, payload: DeviceCreate) -> DeviceResponse:
    existing = db.execute(
        select(Device).where(
            (func.lower(Device.device_name) == func.lower(payload.device_name))
        )
    ).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Device name already exists")

    device = Device(
        device_id=str(uuid4()),
        device_name=payload.device_name,
        ip_address=payload.ip_address,
        port=payload.port,
        api_password=payload.api_password,
        location_id=payload.location_id,
        serial_number=payload.serial_number,
        firmware_version=payload.firmware_version,
        status="unknown",
        last_seen_at=None,
        settings={},
        callback_urls={},
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return _device_to_response(device)


def update(db: Session, id: int, payload: DeviceUpdate) -> DeviceResponse | None:
    device = get_one(db, id)
    if not device:
        return None
    update_data = payload.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(device, key, value)
    db.commit()
    db.refresh(device)
    return DeviceResponse.model_validate(device)


def delete(db: Session, id: int) -> DeviceResponse | None:
    device = get_one(db, id)
    if not device:
        return None
    db.delete(device)
    db.commit()
    return DeviceResponse.model_validate(device)


def _check_port(host: str, port: int = 8090, timeout: float = 2) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def _fetch_device_info(host: str, port: int = 8090, api_password: str = "", timeout: float = 3) -> dict | None:
    """Fetch device information including serial number and firmware version."""
    try:
        if not api_password:
            api_password = "admin123"
        url = f"http://{host}:{port}/device/information?pass={api_password}"
        
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json().get('data', {})
            
            return {
                "serial_number": data.get("deviceKey"),
                "firmware_version": data.get("version"),
                "sdk_version": data.get("sdkVersion"),
            }
    except Exception as e:
        logger.debug(f"Error fetching device info: {e}")
        return None


def _build_location_name(location: "Location") -> str:
    """Build hierarchical location name from location.path field.
    
    The path field already contains the full hierarchical path.
    Format: /Emirate/Base/Location/Building/Area
    Output: Base - Location - Building - Area (emirate filtered out)
    """
    if not location.path or location.path == '/':
        return location.name
    
    # Split path and filter out empty strings
    path_parts = [p for p in location.path.split('/') if p]
    
    # Skip emirate (first element) if we have more than 1 level
    if len(path_parts) > 1:
        path_parts = path_parts[1:]
    
    return ' - '.join(path_parts) if path_parts else location.name


def _device_to_response(device: Device) -> DeviceResponse:
    """Convert Device model to DeviceResponse."""
    from sqlalchemy.orm import Session
    
    location_name = None
    if device.location_id and device.location:
        location_name = _build_location_name(device.location)
    
    return DeviceResponse(
        id=device.id,
        device_id=device.device_id,
        device_name=device.device_name,
        ip_address=device.ip_address,
        port=device.port,
        api_password=device.api_password,
        location_id=device.location_id,
        location_name=location_name,
        serial_number=device.serial_number,
        firmware_version=device.firmware_version,
        sdk_version=device.sdk_version,
        status=device.status,
        last_seen_at=device.last_seen_at,
        settings=device.settings,
        callback_urls=device.callback_urls,
        created_at=device.created_at,
        updated_at=device.updated_at,
    )


def discover_devices(db: Session, subnet: str = "192.168.1.0/24") -> dict:
    network = ipaddress.ip_network(subnet, strict=False)
    results = []
    
    for host_ip in network.hosts():
        ip_str = str(host_ip)
        if _check_port(ip_str, 8090, timeout=1.5):
            existing = db.execute(
                select(Device).where(Device.ip_address == ip_str)
            ).scalars().first()
            if existing:
                continue
            
            device_info = _fetch_device_info(ip_str, 8090, "", timeout=2)
            results.append(
                DiscoveredDevice(
                    device_name=f"Discovered at {ip_str}",
                    ip_address=ip_str,
                    location="",
                    state="online",
                    serial_number=device_info.get("serial_number") if device_info else None,
                    firmware_version=device_info.get("firmware_version") if device_info else None,
                )
            )
    
    return {"success": True, "data": results}
