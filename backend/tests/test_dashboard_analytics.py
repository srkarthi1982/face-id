from __future__ import annotations

import importlib
import inspect
from datetime import date, datetime

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert
from sqlalchemy.dialects import mssql, postgresql

from app.core.permissions import PermissionCode
from app.core import deps
from app.modules import MODULE_NAMES, _MODEL_MODULES
from app.modules.dashboard import db, repository, router as dashboard_router, service
from app.modules.dashboard.constants import TREND_MAX_DAYS
from app.modules.dashboard.schemas import DashboardTrendGranularity
from app.modules.dashboard.tables import (
    saas_ca_person,
    saas_ca_report_daily,
    saas_ca_report_exception,
)
from scripts.luna.seed_local_luna_db import build_seed_rows

router_module = importlib.import_module("app.modules.dashboard.router")


def _daily(day, person_id="P1", person_no="001", actual=100, deleted=False, org="ORG"):
    return {
        "report_date": day,
        "person_id": person_id,
        "person_no": person_no,
        "person_name": f"Person {person_no}",
        "dept_name": "Synthetic Department",
        "plan_work_time": 120,
        "real_work_time": actual,
        "normal_time": actual,
        "overwork_time": 0,
        "late_time": None,
        "early_time": 2,
        "absent_time": 20,
        "del_status": 1 if deleted else 0,
        "org_id": org,
    }


def _stub_range(monkeypatch, rows, latest=date(2026, 1, 31), exceptions=0):
    monkeypatch.setattr(repository, "get_latest_report_date", lambda org_id=None: latest)
    monkeypatch.setattr(repository, "get_daily_rows", lambda *args: rows)
    monkeypatch.setattr(repository, "count_exceptions", lambda *args: exceptions)


def test_dashboard_registration_is_router_only_and_lazy(monkeypatch):
    assert "dashboard" in MODULE_NAMES
    assert "dashboard" not in _MODEL_MODULES
    db.dispose_luna_engine()
    monkeypatch.setattr(db.settings, "LUNA_DATABASE_URL", None)
    importlib.reload(repository)
    importlib.reload(service)
    assert db._engine is None
    assert len(dashboard_router.routes) == 4


def test_runtime_analytics_modules_have_no_primary_session_or_writes():
    combined = "\n".join(inspect.getsource(module) for module in (repository, service, router_module))
    assert "SessionLocal" not in combined
    assert "create_all" not in combined
    assert ".commit(" not in combined
    assert ".flush(" not in combined
    assert "insert(" not in combined
    assert "update(" not in combined
    assert "delete(" not in combined
    assert "saas_ca_clock_record" not in combined
    assert "require_role" not in combined
    assert "PermissionCode.ANALYTICS_READ" in inspect.getsource(router_module)


@pytest.mark.parametrize(
    "builder,args",
    [
        (repository.latest_report_date_statement, ("ORG",)),
        (repository.daily_rows_statement, (date(2025, 1, 1), date(2025, 1, 31), "ORG")),
        (repository.exception_count_statement, (date(2025, 1, 1), date(2025, 1, 31), "ORG")),
        (repository.exceptions_statement, (date(2025, 1, 1), date(2025, 1, 31), "ORG", 1, 20)),
    ],
)
def test_business_selects_compile_for_postgresql_and_mssql(builder, args):
    statement = builder(*args)
    for dialect in (postgresql.dialect(), mssql.dialect()):
        compiled = str(statement.compile(dialect=dialect))
        assert "dbo." in compiled
        assert "INSERT" not in compiled.upper()
        assert "UPDATE" not in compiled.upper()
        assert "DELETE FROM" not in compiled.upper()


def test_overview_uses_latest_default_range_and_exact_vendor_sums(monkeypatch):
    rows = [_daily(date(2026, 1, 30), actual=100), _daily(date(2026, 1, 31), "P2", "002", 80)]
    rows[1]["plan_work_time"] = None
    _stub_range(monkeypatch, rows, exceptions=3)
    result = service.get_overview(None, None, "ORG", 3660)
    assert result.effective_start_date == date(2026, 1, 2)
    assert result.effective_end_date == date(2026, 1, 31)
    assert result.report_row_count == 2
    assert result.report_day_count == 2
    assert result.employee_count == 2
    assert result.reported_exception_count == 3
    assert result.scheduled_seconds == 120
    assert result.actual_seconds == 180
    assert result.late_seconds == 0


def test_empty_source_has_null_effective_dates_and_zero_totals(monkeypatch):
    _stub_range(monkeypatch, [], latest=None)
    result = service.get_overview(date(2020, 1, 1), date(2020, 1, 2), None, 3660)
    assert result.data_status.value == "empty"
    assert result.effective_start_date is None
    assert result.actual_seconds == 0


@pytest.mark.parametrize("granularity", list(DashboardTrendGranularity))
def test_trend_grouping_and_clipping(monkeypatch, granularity):
    rows = [
        _daily(date(2020, 12, 31), actual=100),
        _daily(date(2021, 1, 1), "P2", "002", 200),
        _daily(date(2021, 2, 1), actual=300),
    ]
    _stub_range(monkeypatch, rows, latest=date(2021, 2, 1))
    result = service.get_trend(
        date(2020, 12, 31), date(2021, 2, 1), "ORG", granularity, TREND_MAX_DAYS[granularity.value]
    )
    assert result.points == sorted(result.points, key=lambda point: point.period_start)
    assert result.points[0].period_start == date(2020, 12, 31)
    assert result.points[-1].period_end == date(2021, 2, 1)
    if granularity == DashboardTrendGranularity.WEEK:
        assert result.points[0].period_key == "2020-W53"
        assert result.points[0].actual_seconds == 300


def test_ranking_identity_fallback_ties_and_limit(monkeypatch):
    rows = [
        _daily(date(2026, 1, 1), "P2", "002", 100),
        _daily(date(2026, 1, 1), "P1", "001", 100),
        _daily(date(2026, 1, 1), None, "003", 200),
        _daily(date(2026, 1, 1), None, None, 999),
    ]
    _stub_range(monkeypatch, rows)
    result = service.get_ranking(date(2026, 1, 1), date(2026, 1, 31), None, 3, 3660)
    assert [item.employee_key for item in result.items] == ["003", "P1", "P2"]
    assert [item.rank for item in result.items] == [1, 2, 3]


def test_invalid_and_excessive_ranges_are_rejected(monkeypatch):
    monkeypatch.setattr(repository, "get_latest_report_date", lambda org_id=None: date(2026, 1, 1))
    with pytest.raises(service.DashboardRangeError, match="after"):
        service.resolve_range(date(2026, 2, 1), date(2026, 1, 1), None, 3660)
    with pytest.raises(service.DashboardRangeError, match="limit"):
        service.resolve_range(date(2020, 1, 1), date(2026, 1, 1), None, 10)


def test_exception_dto_is_generic_and_excludes_photo_and_reason():
    fields = set(service.AttendanceExceptionItem.model_fields)
    assert "clock_photo_id" not in fields
    assert "reason" not in fields


def test_repository_filters_deleted_and_org_and_enriches_without_duplicates(monkeypatch):
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS dbo")
        for table in (saas_ca_person, saas_ca_report_daily, saas_ca_report_exception):
            table.create(connection)
        seed = build_seed_rows()
        active_daily = dict(seed["daily"][0], id=1, org_id="ORG", report_date=date(2026, 1, 1))
        deleted_daily = dict(active_daily, id=2, real_work_time=999999, del_status=1)
        other_org = dict(active_daily, id=3, org_id="OTHER", real_work_time=777)
        connection.execute(insert(saas_ca_report_daily), [active_daily, deleted_daily, other_org])
        base_person = dict(seed["persons"][0], id=10, org_id="ORG", person_id="P1", person_no="LOW")
        duplicate = dict(base_person, id=11, person_no="HIGH")
        deleted_lower = dict(base_person, id=9, person_no="DELETED", del_status=1)
        connection.execute(insert(saas_ca_person), [duplicate, deleted_lower, base_person])
        base_exception = dict(
            seed["exceptions"][0], id=100, org_id="ORG", person_id="P1", report_date=date(2026, 1, 1)
        )
        deleted_exception = dict(base_exception, id=101, del_status=1)
        connection.execute(insert(saas_ca_report_exception), [base_exception, deleted_exception])
    monkeypatch.setattr(db, "_engine", engine)
    try:
        overview = service.get_overview(date(2026, 1, 1), date(2026, 1, 1), "ORG", 3660)
        assert overview.report_row_count == 1
        assert overview.actual_seconds == active_daily["real_work_time"]
        items, meta = service.get_attendance_exceptions(
            date(2026, 1, 1), date(2026, 1, 1), "ORG", 1, 1, 3660
        )
        assert meta.total == 1
        assert len(items) == 1
        assert items[0].person_no == "LOW"
    finally:
        db.dispose_luna_engine()


@pytest.mark.parametrize(
    "path",
    [
        "/dashboard/overview",
        "/dashboard/work-hours/trend",
        "/dashboard/work-hours/ranking",
        "/dashboard/attendance-exceptions",
    ],
)
def test_every_route_requires_authentication(path):
    app = FastAPI()
    app.include_router(dashboard_router)
    assert TestClient(app).get(path).status_code == 401


@pytest.mark.parametrize("route", dashboard_router.routes)
def test_every_route_uses_one_router_level_permission_guard(route):
    assert len(route.dependencies) == 1


def test_http_contract_exposes_only_fixed_query_parameters():
    app = FastAPI()
    app.include_router(dashboard_router)
    allowed = {"start_date", "end_date", "org_id", "granularity", "limit", "page", "page_size"}
    actual = {
        parameter["name"]
        for path in app.openapi()["paths"].values()
        for operation in path.values()
        for parameter in operation.get("parameters", [])
    }
    assert actual <= allowed
    assert not actual & {"sql", "column", "sort", "expression"}


@pytest.mark.parametrize("failure", [db.LunaConfigurationError, db.LunaUnavailableError])
def test_safe_503_hides_configuration_and_query_failure_details(monkeypatch, failure):
    app = FastAPI()
    app.include_router(dashboard_router)
    guard = dashboard_router.routes[0].dependencies[0].dependency
    app.dependency_overrides[guard] = lambda: object()
    monkeypatch.setattr(
        service,
        "get_overview",
        lambda *args: (_ for _ in ()).throw(failure("secret://user@host")),
    )
    response = TestClient(app).get("/dashboard/overview")
    assert response.status_code == 503
    assert response.json()["detail"] == "Attendance analytics are temporarily unavailable"
    assert "secret" not in response.text


def test_user_without_permission_is_forbidden(monkeypatch):
    app = FastAPI()
    app.include_router(dashboard_router)
    guard = dashboard_router.routes[0].dependencies[0].dependency
    def denied():
        raise HTTPException(status_code=403, detail="Missing required permission: analytics:read")
    app.dependency_overrides[guard] = denied
    assert TestClient(app).get("/dashboard/overview").status_code == 403


def test_exact_analytics_permission_succeeds_independent_of_role_name(monkeypatch):
    class Role:
        name = "Ordinary Viewer"

    class User:
        username = "synthetic-viewer"
        roles = [Role()]

    monkeypatch.setattr(deps, "_cache_loaded", True)
    monkeypatch.setattr(deps, "_role_permissions_cache", {"Ordinary Viewer": {"analytics:read"}})
    guard = dashboard_router.routes[0].dependencies[0].dependency
    assert guard(current_user=User(), db=object()) is not None
    assert PermissionCode.ANALYTICS_READ.value == "analytics:read"
