from __future__ import annotations

from datetime import time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.permissions import PermissionCode
from app.modules import import_all_models
from app.modules.master import service
from app.modules.master.models import Department, Timing, Weekday
from app.modules.master.schemas import DepartmentCreate, DepartmentUpdate, TimingCreate, TimingUpdate


import_all_models()


@pytest.fixture()
def db() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def test_department_crud_and_tree(db: Session):
    parent = service.create_department(db, DepartmentCreate(name="Parent", code="P"))
    child = service.create_department(db, DepartmentCreate(name="Child", code="C", parent_id=parent.id))
    assert child.path == "/Parent/Child"
    updated = service.update_department(db, child.id, DepartmentUpdate(name="Child Ops"))
    assert updated.path == "/Parent/Child Ops"
    tree = service.get_department_tree(db)
    assert tree[0].children[0].name == "Child Ops"


def test_timing_create_read_update_delete(db: Session):
    department = service.create_department(db, DepartmentCreate(name="Ops"))
    timing = service.create_timing(db, TimingCreate(
        department_id=department.id,
        start_day=Weekday.MONDAY,
        end_day=Weekday.FRIDAY,
        start_time=time(8, 0),
        end_time=time(16, 0),
    ))
    assert timing.department_name == "Ops"
    assert service.get_timings(db)[0].id == timing.id
    updated = service.update_timing(db, timing.id, TimingUpdate(start_time=time(7, 30), is_active=True))
    assert updated.start_time == time(7, 30)
    service.delete_timing(db, timing.id)
    assert service.get_timings(db) == []


@pytest.mark.parametrize(
    "start,end",
    [(time(8, 0), time(8, 0)), (time(20, 0), time(6, 0))],
)
def test_timing_rejects_equal_and_overnight_times(db: Session, start, end):
    department = service.create_department(db, DepartmentCreate(name="Ops"))
    with pytest.raises(ValueError):
        TimingCreate(
            department_id=department.id,
            start_day=Weekday.MONDAY,
            end_day=Weekday.FRIDAY,
            start_time=start,
            end_time=end,
        )


def test_one_active_timing_per_department(db: Session):
    department = service.create_department(db, DepartmentCreate(name="Ops"))
    service.create_timing(db, TimingCreate(
        department_id=department.id,
        start_day=Weekday.MONDAY,
        end_day=Weekday.FRIDAY,
        start_time=time(8, 0),
        end_time=time(16, 0),
    ))
    with pytest.raises(Exception, match="already has an active timing"):
        service.create_timing(db, TimingCreate(
            department_id=department.id,
            start_day=Weekday.SUNDAY,
            end_day=Weekday.THURSDAY,
            start_time=time(7, 0),
            end_time=time(15, 0),
        ))


def test_inactive_department_rejected_for_active_timing(db: Session):
    department = Department(name="Inactive", path="/Inactive", is_active=False)
    db.add(department)
    db.commit()
    with pytest.raises(Exception, match="Department must be active"):
        service.create_timing(db, TimingCreate(
            department_id=department.id,
            start_day=Weekday.MONDAY,
            end_day=Weekday.FRIDAY,
            start_time=time(8, 0),
            end_time=time(16, 0),
        ))


def test_permission_codes_registered():
    assert PermissionCode.DEPARTMENT_READ.value == "department:read"
    assert PermissionCode.DEPARTMENT_WRITE.value == "department:write"
    assert PermissionCode.TIMING_READ.value == "timing:read"
    assert PermissionCode.TIMING_WRITE.value == "timing:write"
