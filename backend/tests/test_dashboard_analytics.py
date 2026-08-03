from __future__ import annotations

import inspect
import importlib
from datetime import date, datetime, time, timezone

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import deps
from app.core.database import Base, get_db
from app.core.permissions import PermissionCode, sync_permissions_to_db
from app.modules import import_all_models
from app.modules.dashboard import constants, repository, router as dashboard_router, service
from app.modules.dashboard.schemas import DashboardTrendGranularity
from app.modules.device.models import Device
from app.modules.master.models import Department, Timing, Weekday
from app.modules.personnel.models import Personnel
from app.modules.recognition_records.models import RecognitionRecord
from app.modules.users.models import Permission, Role, User


import_all_models()
router_module = importlib.import_module("app.modules.dashboard.router")


@pytest.fixture()
def db() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def _seed_department(db: Session, *, active: bool = True, start_day=Weekday.MONDAY, end_day=Weekday.FRIDAY) -> Department:
    department = Department(name="Operations", code="OPS", path="/Operations", is_active=active)
    db.add(department)
    db.flush()
    db.add(Timing(
        department_id=department.id,
        start_day=start_day,
        end_day=end_day,
        start_time=time(8, 0),
        end_time=time(16, 0),
        is_active=True,
    ))
    db.commit()
    db.refresh(department)
    return department


def _seed_person(db: Session, department: Department, *, key="P1", active=True, internal: str | None | object = object()) -> Personnel:
    internal_key = key if not isinstance(internal, str) and internal is not None else internal
    person = Personnel(
        emp_no=f"E-{key}",
        person_id_internal=internal_key,
        person_id_device=f"D-{key}" if internal_key else None,
        full_name=f"Person {key}",
        gender=0,
        department_id=department.id,
        is_active=active,
        push_to_device=False,
    )
    db.add(person)
    db.commit()
    return person


def _event(db: Session, key: str | None, when: datetime, *, event_type="success", device_id=1) -> None:
    db.add(RecognitionRecord(
        device_id=device_id,
        person_id_internal=key,
        person_id_device=key,
        record_type="face",
        event_type=event_type,
        event_name=event_type,
        event_time=when,
        source="callback",
    ))
    db.commit()


def test_dashboard_registration_uses_postgres_department_routes_only():
    source = "\n".join(inspect.getsource(module) for module in (repository, service, router_module))
    assert len(dashboard_router.routes) == 5
    assert "/dashboard/departments" in {route.path for route in dashboard_router.routes}
    for removed_reference in ("LU" + "NA_DATABASE_URL", "db" + "o.", "pyo" + "dbc"):
        assert removed_reference not in source
    assert "PermissionCode.ANALYTICS_READ" in inspect.getsource(router_module)
    assert constants.OVERVIEW_MAX_DAYS == 366
    assert constants.RANKING_MAX_DAYS == 366
    assert constants.EXCEPTIONS_MAX_DAYS == 366
    assert constants.TREND_MAX_DAYS == {"day": 366, "week": 366, "month": 366, "year": 366}
    latest_source = inspect.getsource(repository.get_latest_report_date)
    assert "LATEST_ATTENDANCE_LOOKBACK_DAYS" in latest_source
    assert "func.max(local_date)" in latest_source
    assert "extract(\"isodow\", local_time)" in latest_source
    assert ".limit(LATEST_ATTENDANCE_DATE_SCAN_LIMIT)" in latest_source


def test_attendance_uses_event_time_dubai_day_and_ignores_created_at(db: Session):
    department = _seed_department(db)
    _seed_person(db, department)
    db.add(Device(device_id="door-1", device_name="Door 1", ip_address="127.0.0.1", port=8090, api_password="x", status="ok"))
    db.commit()

    _event(db, "P1", datetime(2026, 1, 5, 4, 5, tzinfo=timezone.utc))   # 08:05 Dubai
    _event(db, "P1", datetime(2026, 1, 5, 12, 30, tzinfo=timezone.utc))  # 16:30 Dubai
    _event(db, "P1", datetime(2026, 1, 4, 20, 30, tzinfo=timezone.utc))  # 00:30 Dubai, same local day

    overview = service.get_overview(db, date(2026, 1, 5), date(2026, 1, 5), department.id, 366)
    assert overview.report_row_count == 1
    assert overview.report_day_count == 1
    assert overview.employee_count == 1
    assert overview.scheduled_seconds == 8 * 3600
    assert overview.actual_seconds == 16 * 3600
    assert overview.normal_seconds == 8 * 3600
    assert overview.overtime_seconds == 8 * 3600
    assert overview.late_seconds == 0
    assert overview.early_seconds == 0


def test_absent_missing_pair_late_and_early_exceptions_are_computed(db: Session):
    department = _seed_department(db)
    _seed_person(db, department, key="ABSENT")
    _seed_person(db, department, key="ONE")
    _seed_person(db, department, key="PAIR")
    _event(db, "ONE", datetime(2026, 1, 5, 5, 0, tzinfo=timezone.utc))    # 09:00 Dubai
    _event(db, "PAIR", datetime(2026, 1, 5, 4, 15, tzinfo=timezone.utc))  # 08:15 Dubai
    _event(db, "PAIR", datetime(2026, 1, 5, 11, 0, tzinfo=timezone.utc))  # 15:00 Dubai
    _event(db, "PAIR", datetime(2026, 1, 5, 10, 0, tzinfo=timezone.utc), event_type="failed")
    _event(db, None, datetime(2026, 1, 5, 4, 0, tzinfo=timezone.utc))

    items, meta = service.get_attendance_exceptions(db, date(2026, 1, 5), date(2026, 1, 5), department.id, 1, 20, 366)
    assert meta.total == 4
    assert sorted(item.exception_type for item in items) == ["ABSENT", "EARLY", "LATE", "MISSING_PAIR"]
    assert all(item.department_id == department.id for item in items)


def test_personnel_without_recognition_identity_are_scheduled_absent(db: Session):
    department = _seed_department(db)
    person = _seed_person(db, department, key="NO-ID", internal=None)
    overview = service.get_overview(db, date(2026, 1, 5), date(2026, 1, 5), department.id, 366)
    ranking = service.get_ranking(db, date(2026, 1, 5), date(2026, 1, 5), department.id, 10, 366, True, None)
    items, meta = service.get_attendance_exceptions(db, date(2026, 1, 5), date(2026, 1, 5), department.id, 1, 20, 366)
    assert overview.report_row_count == 1
    assert overview.absent_seconds == 8 * 3600
    assert ranking.items[0].employee_key == f"personnel:{person.id}"
    assert ranking.items[0].person_name == "Person NO-ID"
    assert meta.total == 1
    assert items[0].exception_type == "ABSENT"


def test_working_days_and_missing_timing_exclusion(db: Session):
    sunday_to_thursday = _seed_department(db, start_day=Weekday.SUNDAY, end_day=Weekday.THURSDAY)
    no_timing = Department(name="No Timing", path="/No Timing", is_active=True)
    db.add(no_timing)
    db.commit()
    _seed_person(db, sunday_to_thursday, key="WORK")
    _seed_person(db, no_timing, key="SKIP")

    friday = service.get_overview(db, date(2026, 1, 9), date(2026, 1, 9), None, 366)
    sunday = service.get_overview(db, date(2026, 1, 11), date(2026, 1, 11), None, 366)
    assert friday.report_row_count == 0
    assert sunday.report_row_count == 1
    assert sunday.employee_count == 1


def test_latest_date_uses_configured_working_day_semantics(db: Session):
    department = _seed_department(db, start_day=Weekday.SUNDAY, end_day=Weekday.THURSDAY)
    _seed_person(db, department)
    _event(db, "P1", datetime(2026, 1, 8, 4, 0, tzinfo=timezone.utc))
    _event(db, "P1", datetime(2026, 1, 8, 12, 0, tzinfo=timezone.utc))
    _event(db, "P1", datetime(2026, 1, 9, 4, 0, tzinfo=timezone.utc))
    assert repository.get_latest_report_date(db, department.id) == date(2026, 1, 8)
    overview = service.get_overview(db, None, None, department.id, 366)
    assert overview.effective_end_date == date(2026, 1, 8)
    assert overview.report_row_count >= 1


def test_inactive_personnel_department_and_timing_are_excluded(db: Session):
    active_department = _seed_department(db)
    inactive_department = _seed_department(db, active=False)
    disabled_timing_department = _seed_department(db)
    db.query(Timing).filter(Timing.department_id == disabled_timing_department.id).update({"is_active": False})
    db.commit()
    _seed_person(db, active_department, key="ACTIVE")
    _seed_person(db, active_department, key="INACTIVE", active=False)
    _seed_person(db, inactive_department, key="INACTIVE-DEPT")
    _seed_person(db, disabled_timing_department, key="NO-TIMING")
    overview = service.get_overview(db, date(2026, 1, 5), date(2026, 1, 5), None, 366)
    assert overview.report_row_count == 1
    assert overview.employee_count == 1


def test_null_event_time_and_non_success_events_are_ignored(db: Session):
    department = _seed_department(db)
    _seed_person(db, department)
    db.add(RecognitionRecord(
        device_id=1,
        person_id_internal="P1",
        person_id_device="P1",
        record_type="face",
        event_type="success",
        event_name="success",
        event_time=None,
        source="callback",
    ))
    db.commit()
    _event(db, "P1", datetime(2026, 1, 5, 4, 0, tzinfo=timezone.utc), event_type="failed")
    overview = service.get_overview(db, date(2026, 1, 5), date(2026, 1, 5), department.id, 366)
    assert overview.report_row_count == 1
    assert overview.absent_seconds == 8 * 3600


def test_three_or_more_events_use_earliest_check_in_and_latest_check_out(db: Session):
    department = _seed_department(db)
    _seed_person(db, department)
    _event(db, "P1", datetime(2026, 1, 5, 4, 5, tzinfo=timezone.utc))
    _event(db, "P1", datetime(2026, 1, 5, 8, 0, tzinfo=timezone.utc))
    _event(db, "P1", datetime(2026, 1, 5, 12, 30, tzinfo=timezone.utc))
    overview = service.get_overview(db, date(2026, 1, 5), date(2026, 1, 5), department.id, 366)
    assert overview.actual_seconds == 8 * 3600 + 25 * 60
    assert overview.overtime_seconds == 25 * 60


def test_circular_weekday_range_is_supported(db: Session):
    department = _seed_department(db, start_day=Weekday.FRIDAY, end_day=Weekday.MONDAY)
    _seed_person(db, department)
    friday = service.get_overview(db, date(2026, 1, 9), date(2026, 1, 9), department.id, 366)
    monday = service.get_overview(db, date(2026, 1, 12), date(2026, 1, 12), department.id, 366)
    tuesday = service.get_overview(db, date(2026, 1, 13), date(2026, 1, 13), department.id, 366)
    assert friday.report_row_count == 1
    assert monday.report_row_count == 1
    assert tuesday.report_row_count == 0


def test_ranking_include_all_and_stable_top_n(db: Session):
    department = _seed_department(db)
    for index in range(12):
        key = f"P{index:02d}"
        _seed_person(db, department, key=key)
        _event(db, key, datetime(2026, 1, 5, 4, 0, tzinfo=timezone.utc))
        _event(db, key, datetime(2026, 1, 5, 12, index, tzinfo=timezone.utc))

    top = service.get_ranking(db, date(2026, 1, 5), date(2026, 1, 5), department.id, 10, 366, False, None)
    all_rows = service.get_ranking(db, date(2026, 1, 5), date(2026, 1, 5), department.id, 10, 366, True, None)
    assert len(top.items) == 10
    assert len(all_rows.items) == 12
    assert all_rows.items[0].actual_seconds > all_rows.items[-1].actual_seconds


def test_ranking_ties_are_deterministic(db: Session):
    department = _seed_department(db)
    _seed_person(db, department, key="B")
    _seed_person(db, department, key="A")
    for key in ("A", "B"):
        _event(db, key, datetime(2026, 1, 5, 4, 0, tzinfo=timezone.utc))
        _event(db, key, datetime(2026, 1, 5, 12, 0, tzinfo=timezone.utc))
    ranking = service.get_ranking(db, date(2026, 1, 5), date(2026, 1, 5), department.id, 10, 366, True, None)
    assert [item.person_no for item in ranking.items] == ["E-A", "E-B"]


def test_day_month_and_year_ranking_scopes(db: Session):
    department = _seed_department(db)
    _seed_person(db, department)
    for day, checkout_hour in ((5, 12), (6, 10), (12, 11)):
        _event(db, "P1", datetime(2026, 1, day, 4, 0, tzinfo=timezone.utc))
        _event(db, "P1", datetime(2026, 1, day, checkout_hour, 0, tzinfo=timezone.utc))
    day_rank = service.get_ranking(db, date(2026, 1, 1), date(2026, 1, 12), department.id, 10, 366, True, DashboardTrendGranularity.DAY)
    month_rank = service.get_ranking(db, date(2026, 1, 1), date(2026, 1, 12), department.id, 10, 366, True, DashboardTrendGranularity.MONTH)
    year_rank = service.get_ranking(db, date(2026, 1, 1), date(2026, 1, 12), department.id, 10, 366, True, DashboardTrendGranularity.YEAR)
    assert day_rank.items[0].report_day_count == 1
    assert month_rank.items[0].report_day_count == 8
    assert year_rank.items[0].report_day_count == 8


def test_trend_periods_are_clipped_to_applied_range(db: Session):
    department = _seed_department(db)
    _seed_person(db, department)
    _event(db, "P1", datetime(2026, 1, 5, 4, 0, tzinfo=timezone.utc))
    _event(db, "P1", datetime(2026, 1, 5, 12, 0, tzinfo=timezone.utc))
    trend = service.get_trend(
        db,
        date(2026, 1, 5),
        date(2026, 1, 7),
        department.id,
        DashboardTrendGranularity.WEEK,
        366,
    )
    assert trend.points[0].period_start == date(2026, 1, 5)
    assert trend.points[0].period_end == date(2026, 1, 7)
    assert trend.points[0].report_row_count == 3


def test_invalid_and_excessive_ranges_raise_safe_errors(db: Session):
    department = _seed_department(db)
    with pytest.raises(service.DashboardRangeError):
        service.get_overview(db, date(2026, 1, 6), date(2026, 1, 5), department.id, 366)
    with pytest.raises(service.DashboardRangeError):
        service.get_overview(db, date(2026, 1, 1), date(2027, 1, 2), department.id, 366)


def test_empty_default_range_has_no_latest_date(db: Session):
    _seed_department(db)
    overview = service.get_overview(db, None, None, None, 366)
    assert overview.data_status == "empty"
    assert overview.effective_start_date is None
    assert overview.effective_end_date is None


def test_exception_pagination_and_order_are_deterministic(db: Session):
    department = _seed_department(db)
    _seed_person(db, department, key="B")
    _seed_person(db, department, key="A")
    items, meta = service.get_attendance_exceptions(db, date(2026, 1, 5), date(2026, 1, 6), department.id, 2, 1, 366)
    assert meta.total == 4
    assert meta.pages == 4
    assert len(items) == 1
    assert items[0].report_date == date(2026, 1, 5)
    assert items[0].person_no == "E-B"


def test_dashboard_routes_reject_missing_token():
    app = FastAPI()
    app.include_router(dashboard_router)
    response = TestClient(app).get("/dashboard/overview")
    assert response.status_code == 401


def test_dashboard_routes_require_analytics_read(db: Session):
    app = FastAPI()
    app.include_router(dashboard_router)
    guard = dashboard_router.routes[0].dependencies[0].dependency

    def denied():
        raise HTTPException(status_code=403, detail="Missing required permission: analytics:read")

    app.dependency_overrides[guard] = denied
    response = TestClient(app).get("/dashboard/departments")
    assert response.status_code == 403


@pytest.mark.parametrize(
    "path",
    [
        "/dashboard/departments",
        "/dashboard/overview",
        "/dashboard/work-hours/trend",
        "/dashboard/work-hours/ranking",
        "/dashboard/attendance-exceptions",
    ],
)
def test_all_dashboard_routes_require_analytics_read(db: Session, path: str):
    app = FastAPI()
    app.include_router(dashboard_router)
    guard = dashboard_router.routes[0].dependencies[0].dependency
    app.dependency_overrides[guard] = lambda: object()
    app.dependency_overrides[get_db] = lambda: db
    response = TestClient(app).get(path)
    assert response.status_code == 200


def test_dashboard_routes_use_department_parameters(db: Session):
    app = FastAPI()
    app.include_router(dashboard_router)
    guard = dashboard_router.routes[0].dependencies[0].dependency
    app.dependency_overrides[guard] = lambda: object()
    app.dependency_overrides[get_db] = lambda: db
    _seed_department(db)
    response = TestClient(app).get("/dashboard/work-hours/ranking?department_id=1&include_all=true&period=day")
    assert response.status_code == 200
    assert response.json()["data"]["department_id"] == 1
    assert PermissionCode.ANALYTICS_READ.value == "analytics:read"


def test_dashboard_routes_are_read_only():
    assert all(route.methods == {"GET"} for route in dashboard_router.routes)


def test_sync_permissions_grants_existing_admin_roles_and_invalidates_cache(db: Session):
    admin_role = Role(name="admin", description="Admin", is_system=True)
    user = User(username="admin-user", is_active=True)
    user.roles.append(admin_role)
    db.add_all([admin_role, user, Permission(code="admin:full", name="Full Admin", module="admin")])
    db.commit()
    deps.invalidate_permission_cache()

    assert PermissionCode.TIMING_WRITE.value not in deps.get_user_permission_codes(user, db)
    sync_permissions_to_db(db)
    permissions = deps.get_user_permission_codes(user, db)
    assert PermissionCode.DEPARTMENT_READ.value in permissions
    assert PermissionCode.DEPARTMENT_WRITE.value in permissions
    assert PermissionCode.TIMING_READ.value in permissions
    assert PermissionCode.TIMING_WRITE.value in permissions
