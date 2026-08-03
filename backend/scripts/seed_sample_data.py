#!/usr/bin/env python3
"""Seed meaningful, idempotent sample data across the Face ID schema.

Run with the backend virtual environment after migrations and the default
role/user seeds have completed:

    .venv/Scripts/python.exe scripts/seed_sample_data.py
"""

from __future__ import annotations

import hashlib
import os
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))
os.chdir(_BACKEND_DIR)

_VENV_DIR = _BACKEND_DIR / ".venv"
if _VENV_DIR.exists() and Path(sys.prefix).resolve() != _VENV_DIR.resolve():
    raise SystemExit(
        "Run this script with backend/.venv/Scripts/python.exe (Windows) "
        "or backend/.venv/bin/python (Unix)."
    )

from app.core.database import SessionLocal
from app.modules import import_all_models
from app.modules.audit.models import AuditLog
from app.modules.callbacks.models import CallbackConfig
from app.modules.device.models import Device
from app.modules.master.models import Department, Location, LocationType, Timing, Unit, UnitType, Weekday
from app.modules.pat.models import PersonalAccessToken
from app.modules.person_mapping.models import DevicePersonMapping
from app.modules.personnel.models import Personnel
from app.modules.photos.models import PhotoRegistration
from app.modules.recognition_records.models import RecognitionRecord
from app.modules.shared.models import Country
from app.modules.users.models import User


SEED_TIMESTAMP = datetime(2026, 7, 29, 6, 0, tzinfo=timezone.utc)


def get_or_create(db, model, defaults: dict | None = None, **lookup):
    instance = db.query(model).filter_by(**lookup).first()
    if instance is not None:
        return instance, False
    instance = model(**lookup, **(defaults or {}))
    db.add(instance)
    db.flush()
    return instance, True


def seed_countries(db, counts: dict[str, int]) -> None:
    names = [
        "United Arab Emirates",
        "Bahrain",
        "Egypt",
        "Jordan",
        "Oman",
        "Saudi Arabia",
        "United Kingdom",
        "United States",
    ]
    for name in names:
        _, created = get_or_create(db, Country, name=name)
        counts["countries"] += int(created)


def seed_units(db, counts: dict[str, int]) -> dict[str, Unit]:
    specs = [
        ("joint", "Joint Forces", "JF", "Joint Forces headquarters", UnitType.FORCE, None, 10),
        ("adc", "Air Defence Command", "ADC", "Air defence operations command", UnitType.COMMAND, "joint", 20),
        ("b12", "12th Air Defence Battalion", "12-ADB", "Operational air defence battalion", UnitType.BATTALION, "adc", 30),
        ("hq", "Headquarters Company", "HQ-CO", "Headquarters and support unit", UnitType.UNIT, "b12", 40),
    ]
    result: dict[str, Unit] = {}
    for key, name, code, description, unit_type, parent_key, order in specs:
        parent = result.get(parent_key) if parent_key else None
        unit = db.query(Unit).filter(Unit.code == code, Unit.parent_id == (parent.id if parent else None)).first()
        if unit is None:
            parent_path = parent.path.rstrip("/") if parent else ""
            unit = Unit(
                name=name,
                code=code,
                description=description,
                type=unit_type,
                parent_id=parent.id if parent else None,
                path=f"{parent_path}/{code}",
                is_active=True,
                sort_order=order,
            )
            db.add(unit)
            db.flush()
            counts["units"] += 1
        result[key] = unit
    return result


def seed_locations(db, units: dict[str, Unit], counts: dict[str, int]) -> dict[str, Location]:
    specs = [
        ("abu_dhabi", "Abu Dhabi", LocationType.EMIRATE, None, "joint", 10),
        ("base", "Al Dhafra Base", LocationType.BASE, "abu_dhabi", "adc", 20),
        ("main_gate", "Main Gate", LocationType.LOCATION, "base", "b12", 30),
        ("hq_building", "Headquarters Building", LocationType.BUILDING, "base", "hq", 40),
        ("security", "Security Operations Room", LocationType.AREA, "hq_building", "hq", 50),
        ("data_centre", "Data Centre", LocationType.AREA, "hq_building", "hq", 60),
    ]
    result: dict[str, Location] = {}
    for key, name, location_type, parent_key, unit_key, order in specs:
        parent = result.get(parent_key) if parent_key else None
        location = db.query(Location).filter(
            Location.name == name,
            Location.type == location_type,
            Location.parent_id == (parent.id if parent else None),
        ).first()
        if location is None:
            parent_path = parent.path.rstrip("/") if parent else ""
            location = Location(
                name=name,
                type=location_type,
                parent_id=parent.id if parent else None,
                unit_id=units[unit_key].id,
                path=f"{parent_path}/{name}",
                is_active=True,
                sort_order=order,
            )
            db.add(location)
            db.flush()
            counts["locations"] += 1
        result[key] = location
    return result


def seed_departments(db, counts: dict[str, int]) -> dict[str, Department]:
    specs = [
        ("operations", "Operations", "OPS", "Operations department", None, 10),
        ("security", "Security", "SEC", "Security operations department", "operations", 20),
        ("headquarters", "Headquarters", "HQ", "Headquarters support department", "operations", 30),
    ]
    result: dict[str, Department] = {}
    for key, name, code, description, parent_key, order in specs:
        parent = result.get(parent_key) if parent_key else None
        department = db.query(Department).filter(
            Department.code == code,
            Department.parent_id == (parent.id if parent else None),
        ).first()
        if department is None:
            parent_path = parent.path.rstrip("/") if parent else ""
            department = Department(
                name=name,
                code=code,
                description=description,
                parent_id=parent.id if parent else None,
                path=f"{parent_path}/{name}",
                is_active=True,
                sort_order=order,
            )
            db.add(department)
            db.flush()
            counts["departments"] += 1
        result[key] = department
    return result


def seed_timings(db, departments: dict[str, Department], counts: dict[str, int]) -> None:
    specs = [
        ("operations", Weekday.MONDAY, Weekday.FRIDAY, time(8, 0), time(16, 0)),
        ("security", Weekday.MONDAY, Weekday.SATURDAY, time(7, 0), time(15, 0)),
        ("headquarters", Weekday.MONDAY, Weekday.FRIDAY, time(8, 30), time(16, 30)),
    ]
    for department_key, start_day, end_day, start_time, end_time in specs:
        department = departments[department_key]
        timing = db.query(Timing).filter(
            Timing.department_id == department.id,
            Timing.is_active.is_(True),
        ).first()
        if timing is None:
            db.add(Timing(
                department_id=department.id,
                start_day=start_day,
                end_day=end_day,
                start_time=start_time,
                end_time=end_time,
                is_active=True,
            ))
            counts["timings"] += 1


def seed_devices(db, locations: dict[str, Location], counts: dict[str, int]) -> dict[str, Device]:
    specs = [
        ("gate_in", "FID-GATE-IN-01", "Main Gate Entry", "192.0.2.11", "main_gate", "online", "SN-GATE-IN-001"),
        ("gate_out", "FID-GATE-OUT-01", "Main Gate Exit", "192.0.2.12", "main_gate", "online", "SN-GATE-OUT-001"),
        ("hq", "FID-HQ-01", "HQ Building Lobby", "192.0.2.21", "hq_building", "maintenance", "SN-HQ-001"),
        ("dc", "FID-DC-01", "Data Centre Entry", "192.0.2.31", "data_centre", "offline", "SN-DC-001"),
    ]
    result: dict[str, Device] = {}
    for key, device_id, name, ip, location_key, status, serial in specs:
        device, created = get_or_create(
            db,
            Device,
            device_id=device_id,
            defaults={
                "device_name": name,
                "ip_address": ip,
                "port": 8090,
                "api_password": "seed-device-password",
                "location_id": locations[location_key].id,
                "serial_number": serial,
                "firmware_version": "3.8.2",
                "sdk_version": "5.1.0",
                "status": status,
                "last_seen_at": SEED_TIMESTAMP if status == "online" else SEED_TIMESTAMP - timedelta(days=2),
                "settings": {"recognition_threshold": 0.82, "liveness_detection": True, "timezone": "Asia/Dubai"},
                "callback_urls": {"records": "http://localhost:8000/api/v1/callback/records"},
            },
        )
        counts["devices"] += int(created)
        result[key] = device
    return result


def seed_personnel(
    db,
    locations: dict[str, Location],
    departments: dict[str, Department],
    counts: dict[str, int],
) -> dict[str, Personnel]:
    specs = [
        ("P-1001", "EMP-1001", "Ahmed Al Mansoori", 1, "ahmed.mansoori@example.com", "+971501110001", "Operations Officer", "1988-03-14", "2014-09-01"),
        ("P-1002", "EMP-1002", "Mariam Al Suwaidi", 2, "mariam.suwaidi@example.com", "+971501110002", "Security Supervisor", "1990-11-22", "2016-02-15"),
        ("P-1003", "EMP-1003", "Omar Al Nuaimi", 1, "omar.nuaimi@example.com", "+971501110003", "Systems Engineer", "1992-07-09", "2018-05-20"),
        ("P-1004", "EMP-1004", "Fatima Al Zaabi", 2, "fatima.zaabi@example.com", "+971501110004", "HR Specialist", "1994-01-30", "2020-01-12"),
        ("P-1005", "EMP-1005", "Yousef Al Hammadi", 1, "yousef.hammadi@example.com", "+971501110005", "Gate Controller", "1987-09-18", "2012-06-10"),
    ]
    result: dict[str, Personnel] = {}
    for index, (person_id, emp_no, name, gender, email, phone, position, dob, hired) in enumerate(specs, start=1):
        person, created = get_or_create(
            db,
            Personnel,
            person_id_internal=person_id,
            defaults={
                "org_id": locations["base"].id,
                "department_id": departments["security"].id if index in (2, 5) else departments["headquarters"].id,
                "emp_no": emp_no,
                "person_id_device": f"DEV-{1000 + index}",
                "full_name": name,
                "gender": gender,
                "email": email,
                "phone": phone,
                "date_of_birth": dob,
                "nationality": "United Arab Emirates",
                "idcard_num": f"784-198{index}-123456{index}-1",
                "id_number": f"EID-{100000 + index}",
                "card_no": f"CARD-{2000 + index}",
                "position": position,
                "hire_date": hired,
                "permissions": {"doors": ["main_gate", "hq_lobby"], "access_level": "standard"},
                "pass_time": {"start": "06:00", "end": "22:00", "days": [0, 1, 2, 3, 4]},
                "push_to_device": True,
                "is_active": True,
            },
        )
        counts["personnel"] += int(created)
        result[person_id] = person
    return result


def seed_photos_and_mappings(db, people: dict[str, Personnel], devices: dict[str, Device], counts: dict[str, int]) -> None:
    assigned_devices = {
        "P-1001": ["gate_in", "hq"],
        "P-1002": ["gate_in", "gate_out", "hq"],
        "P-1003": ["gate_in", "hq", "dc"],
        "P-1004": ["gate_in", "gate_out"],
        "P-1005": ["gate_in", "gate_out"],
    }
    for person_id, device_keys in assigned_devices.items():
        person = people[person_id]
        master = db.query(PhotoRegistration).filter(
            PhotoRegistration.person_id_internal == person_id,
            PhotoRegistration.device_id.is_(None),
            PhotoRegistration.source == "seed",
        ).first()
        if master is None:
            master = PhotoRegistration(
                person_id_internal=person_id,
                person_id_device=person.person_id_device,
                face_id=f"FACE-{person_id}",
                feature="seed-feature-v1",
                feature_key=f"FEATURE-{person_id}",
                img_url=f"/seed/photos/{person_id.lower()}.jpg",
                img_content_type="image/jpeg",
                source="seed",
            )
            db.add(master)
            db.flush()
            counts["photo_registrations"] += 1

        for device_key in device_keys:
            device = devices[device_key]
            mapping = db.query(DevicePersonMapping).filter_by(
                person_id_internal=person_id, device_id=device.id
            ).first()
            if mapping is None:
                mapping = DevicePersonMapping(
                    person_id_internal=person_id,
                    device_id=device.id,
                    person_id_device=person.person_id_device,
                    photo_ids={"master": master.id, "face_id": master.face_id},
                    synced_at=SEED_TIMESTAMP - timedelta(hours=device.id),
                )
                db.add(mapping)
                counts["device_person_mapping"] += 1


def seed_callbacks(db, devices: dict[str, Device], counts: dict[str, int]) -> None:
    for device_key in ("gate_in", "gate_out", "hq", "dc"):
        device = devices[device_key]
        for config_type, path in (("recognition", "records"), ("heartbeat", "heartbeat")):
            _, created = get_or_create(
                db,
                CallbackConfig,
                device_id=device.id,
                config_type=config_type,
                defaults={
                    "callback_url": f"http://localhost:8000/api/v1/callback/{path}",
                    "enabled": device.status != "offline",
                },
            )
            counts["callback_configs"] += int(created)


def seed_recognition_records(db, people: dict[str, Personnel], devices: dict[str, Device], counts: dict[str, int]) -> None:
    events = [
        ("gate_in", "P-1001", 0, "entry", "Access Granted"),
        ("gate_in", "P-1002", 7, "entry", "Access Granted"),
        ("gate_out", "P-1001", 540, "exit", "Exit Recorded"),
        ("hq", "P-1003", 25, "entry", "Access Granted"),
        ("dc", "P-1003", 45, "entry", "Device Offline Queue"),
        ("gate_in", "P-1004", 65, "entry", "Access Granted"),
        ("gate_out", "P-1005", 600, "exit", "Exit Recorded"),
        ("gate_in", None, 90, "entry", "Unknown Person"),
    ]
    for device_key, person_id, minute_offset, event_type, event_name in events:
        device = devices[device_key]
        event_time = SEED_TIMESTAMP + timedelta(minutes=minute_offset)
        query = db.query(RecognitionRecord).filter(
            RecognitionRecord.device_id == device.id,
            RecognitionRecord.event_time == event_time,
            RecognitionRecord.event_name == event_name,
        )
        if person_id is None:
            query = query.filter(RecognitionRecord.person_id_internal.is_(None))
        else:
            query = query.filter(RecognitionRecord.person_id_internal == person_id)
        existing = query.first()
        if existing is not None:
            if existing.person_id_internal is not None and existing.event_type != "success":
                existing.event_type = "success"
                db.add(existing)
            continue
        person = people.get(person_id) if person_id else None
        db.add(RecognitionRecord(
            device_id=device.id,
            person_id_internal=person_id,
            person_id_device=person.person_id_device if person else None,
            record_type="face_recognition",
            mode="face",
            event_type="success" if person_id else event_type,
            event_name=event_name,
            event_time=event_time,
            source="seed",
        ))
        counts["recognition_records"] += 1


def seed_revoked_pat_and_audit(db, counts: dict[str, int]) -> None:
    admin = db.query(User).filter_by(username="admin").one()
    token_name = "Seeded integration example (revoked)"
    token = db.query(PersonalAccessToken).filter_by(user_id=admin.id, name=token_name).first()
    if token is None:
        raw_token = "face-id-seed-token-not-for-use"
        db.add(PersonalAccessToken(
            user_id=admin.id,
            name=token_name,
            token_prefix="fid_seed_",
            token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
            expires_at=SEED_TIMESTAMP + timedelta(days=365),
            last_used_at=SEED_TIMESTAMP,
            revoked_at=SEED_TIMESTAMP,
        ))
        counts["personal_access_tokens"] += 1

    marker = db.query(AuditLog).filter_by(table_name="seed_data", row_id="sample-v1").first()
    if marker is None:
        db.add(AuditLog(
            table_name="seed_data",
            row_id="sample-v1",
            operation="INSERT",
            user_id=admin.id,
            timestamp=SEED_TIMESTAMP,
            before_data=None,
            after_data={"dataset": "Face ID meaningful sample data", "version": 1},
            changed_fields=None,
        ))
        counts["audit_logs"] += 1


def main() -> None:
    import_all_models()
    counts = {
        "countries": 0,
        "units": 0,
        "locations": 0,
        "departments": 0,
        "timings": 0,
        "devices": 0,
        "personnel": 0,
        "photo_registrations": 0,
        "device_person_mapping": 0,
        "callback_configs": 0,
        "recognition_records": 0,
        "personal_access_tokens": 0,
        "audit_logs": 0,
    }
    db = SessionLocal()
    try:
        seed_countries(db, counts)
        units = seed_units(db, counts)
        locations = seed_locations(db, units, counts)
        departments = seed_departments(db, counts)
        seed_timings(db, departments, counts)
        devices = seed_devices(db, locations, counts)
        people = seed_personnel(db, locations, departments, counts)
        seed_photos_and_mappings(db, people, devices, counts)
        seed_callbacks(db, devices, counts)
        seed_recognition_records(db, people, devices, counts)
        seed_revoked_pat_and_audit(db, counts)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print("Sample data seed complete.")
    for table, created in counts.items():
        print(f"  {table}: {created} created")


if __name__ == "__main__":
    main()
