from __future__ import annotations

import importlib
import inspect
from datetime import date, datetime, timedelta

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
    duration_map = {
        "scheduled_seconds": "plan_work_time", "actual_seconds": "real_work_time",
        "normal_seconds": "normal_time", "overtime_seconds": "overwork_time",
        "late_seconds": "late_time", "early_seconds": "early_time", "absent_seconds": "absent_time",
    }
    def identity(row):
        person_id = (row.get("person_id") or "").strip()
        person_no = (row.get("person_no") or "").strip()
        return (row.get("org_id"), "person_id", person_id) if person_id else (
            (row.get("org_id"), "person_no", person_no) if person_no else None
        )
    def in_range(start, end, org_id=None):
        return [row for row in rows if start <= row["report_date"] <= end and (org_id is None or row["org_id"] == org_id)]
    def totals(selected):
        return {name: sum(int(row.get(column) or 0) for row in selected) for name, column in duration_map.items()}
    def overview(start, end, org_id=None):
        selected = in_range(start, end, org_id)
        return {"report_row_count": len(selected), "report_day_count": len({r["report_date"] for r in selected}),
                "employee_count": len({value for r in selected if (value := identity(r))}), **totals(selected)}
    def trend(start, end, org_id=None):
        selected = in_range(start, end, org_id)
        return [{"report_date": day, "report_row_count": len(day_rows),
                 "employee_count": len({value for r in day_rows if (value := identity(r))}), **totals(day_rows)}
                for day in sorted({r["report_date"] for r in selected})
                if (day_rows := [r for r in selected if r["report_date"] == day])]
    def period_counts(periods, org_id=None):
        return {
            key: len({value for r in in_range(start, end, org_id) if (value := identity(r))})
            for key, start, end in periods
        }
    def ranking(start, end, org_id, limit):
        selected = in_range(start, end, org_id)
        groups = {}
        for row in selected:
            if key := identity(row): groups.setdefault(key, []).append(row)
        result = []
        for (scope, source, value), group in groups.items():
            result.append({"org_id": scope, "identity_source": source, "employee_key": value,
                           "person_id": value if source == "person_id" else None,
                           "person_no": min((r.get("person_no") for r in group if r.get("person_no")), default=None),
                           "person_name": min((r.get("person_name") for r in group if r.get("person_name")), default=None),
                           "department_name": min((r.get("dept_name") for r in group if r.get("dept_name")), default=None),
                           "report_day_count": len({r["report_date"] for r in group}), **totals(group)})
        result.sort(key=lambda r: (-r["actual_seconds"], r["person_no"] is None, r["person_no"] or "",
                                  r["person_id"] is None, r["person_id"] or "", r["org_id"] or ""))
        return result[:limit]
    monkeypatch.setattr(repository, "get_overview_aggregate", overview)
    monkeypatch.setattr(repository, "get_trend_date_aggregates", trend)
    monkeypatch.setattr(repository, "get_trend_period_employee_counts", period_counts)
    monkeypatch.setattr(repository, "get_ranking_aggregates", ranking)
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
    assert not hasattr(repository, "get_daily_rows")
    assert "get_daily_rows" not in inspect.getsource(service)


@pytest.mark.parametrize(
    "builder,args",
    [
        (repository.latest_report_date_statement, ("ORG",)),
        (repository.overview_statement, (date(2025, 1, 1), date(2025, 1, 31), "ORG")),
        (repository.scoped_identity_count_statement, (date(2025, 1, 1), date(2025, 1, 31), "ORG")),
        (repository.trend_dates_statement, (date(2025, 1, 1), date(2025, 1, 31), "ORG")),
        (repository.trend_date_identity_counts_statement, (date(2025, 1, 1), date(2025, 1, 31), "ORG")),
        (repository.trend_period_identity_counts_statement,
         ([("2025-W01", date(2024, 12, 30), date(2025, 1, 5)), ("2025-W02", date(2025, 1, 6), date(2025, 1, 12))], "ORG")),
        (repository.ranking_statement, (date(2025, 1, 1), date(2025, 1, 31), "ORG", 10)),
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


@pytest.mark.parametrize("granularity", list(DashboardTrendGranularity))
def test_trend_report_counts_sum_underlying_rows(monkeypatch, granularity):
    rows = [
        _daily(date(2025, 1, 2), "P1", "001", 10),
        _daily(date(2025, 1, 2), "P2", "002", 20),
        _daily(date(2025, 1, 2), "P3", "003", 30),
        _daily(date(2025, 1, 3), "P1", "001", 40),
    ]
    _stub_range(monkeypatch, rows, latest=date(2025, 1, 3))
    result = service.get_trend(
        date(2025, 1, 2), date(2025, 1, 3), "ORG", granularity,
        TREND_MAX_DAYS[granularity.value],
    )
    if granularity == DashboardTrendGranularity.DAY:
        assert [point.report_row_count for point in result.points] == [3, 1]
        assert [point.employee_count for point in result.points] == [3, 1]
    else:
        assert len(result.points) == 1
        assert result.points[0].report_row_count == 4
        assert result.points[0].employee_count == 3


@pytest.mark.parametrize(
    "granularity,days",
    [
        (DashboardTrendGranularity.DAY, 300),
        (DashboardTrendGranularity.WEEK, 1000),
        (DashboardTrendGranularity.MONTH, 3000),
        (DashboardTrendGranularity.YEAR, 3000),
    ],
)
def test_trend_period_count_repository_calls_are_bounded(monkeypatch, granularity, days):
    start = date(2018, 1, 1)
    end = start + timedelta(days=days - 1)
    date_rows = [
        {"report_date": start + timedelta(days=offset), "report_row_count": 2,
         "employee_count": 1, "scheduled_seconds": 2, "actual_seconds": 2,
         "normal_seconds": 2, "overtime_seconds": 0, "late_seconds": 0,
         "early_seconds": 0, "absent_seconds": 0}
        for offset in range(days)
    ]
    calls = {"latest": 0, "dates": 0, "periods": 0}
    def latest(org_id=None):
        calls["latest"] += 1
        return end
    def dates(*args):
        calls["dates"] += 1
        return date_rows
    def periods(descriptors, org_id=None):
        calls["periods"] += 1
        return {key: 1 for key, _start, _end in descriptors}
    monkeypatch.setattr(repository, "get_latest_report_date", latest)
    monkeypatch.setattr(repository, "get_trend_date_aggregates", dates)
    monkeypatch.setattr(repository, "get_trend_period_employee_counts", periods)
    result = service.get_trend(start, end, None, granularity, TREND_MAX_DAYS[granularity.value])
    assert result.points
    assert calls == {"latest": 1, "dates": 1, "periods": 0 if granularity.value == "day" else 1}


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
        missing_exception = dict(base_exception, id=99, person_id="MISSING")
        connection.execute(insert(saas_ca_report_exception), [base_exception, missing_exception, deleted_exception])
    monkeypatch.setattr(db, "_engine", engine)
    try:
        overview = service.get_overview(date(2026, 1, 1), date(2026, 1, 1), "ORG", 3660)
        assert overview.report_row_count == 1
        assert overview.actual_seconds == active_daily["real_work_time"]
        items, meta = service.get_attendance_exceptions(
            date(2026, 1, 1), date(2026, 1, 1), "ORG", 1, 1, 3660
        )
        assert meta.total == 2
        assert meta.pages == 2
        assert len(items) == 1
        assert items[0].person_no == "LOW"
        page_two, page_two_meta = service.get_attendance_exceptions(
            date(2026, 1, 1), date(2026, 1, 1), "ORG", 2, 1, 3660
        )
        assert page_two_meta.model_dump() == {"page": 2, "page_size": 1, "total": 2, "pages": 2}
        assert page_two[0].id == 99
        assert page_two[0].person_no is None
        assert page_two[0].person_name is None
    finally:
        db.dispose_luna_engine()


def test_bounded_aggregates_and_namespace_safe_identity(monkeypatch):
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS dbo")
        saas_ca_report_daily.create(connection)
        base = build_seed_rows()["daily"][0]
        specs = [
            (1, "A", "123", "900", date(2026, 1, 1), 10, "Zulu", "Zulu Dept", 0),
            (2, "A", "123", "900", date(2026, 1, 2), 20, "Alpha", "Alpha Dept", 0),
            (3, "B", "123", "800", date(2026, 1, 1), 30, "B Person", "B Dept", 0),
            (4, "A", None, "123", date(2026, 1, 1), 40, "Fallback A", "Ops", 0),
            (5, "B", None, "123", date(2026, 1, 1), 50, "Fallback B", "Ops", 0),
            (6, "A", "   ", " W ", date(2026, 1, 1), 60, "Whitespace", "Ops", 0),
            (7, "A", None, "   ", date(2026, 1, 1), 70, "Excluded Identity", "Ops", 0),
            (8, "A", "DELETED", "D", date(2026, 1, 1), 9999, "Deleted", "Ops", 1),
        ]
        rows = []
        for row_id, org, person_id, person_no, day, actual, name, department, deleted in specs:
            rows.append(dict(
                base, id=row_id, org_id=org, person_id=person_id, person_no=person_no,
                report_date=day, real_work_time=actual, normal_time=actual,
                plan_work_time=None if row_id == 1 else 100, overwork_time=0,
                person_name=name, dept_name=department, del_status=deleted,
            ))
        connection.execute(insert(saas_ca_report_daily), rows)
    monkeypatch.setattr(db, "_engine", engine)
    try:
        overview = repository.get_overview_aggregate(date(2026, 1, 1), date(2026, 1, 2))
        trend = repository.get_trend_date_aggregates(date(2026, 1, 1), date(2026, 1, 2))
        period_counts = repository.get_trend_period_employee_counts(
            [("all", date(2026, 1, 1), date(2026, 1, 2))]
        )
        ranking = list(repository.get_ranking_aggregates(date(2026, 1, 1), date(2026, 1, 2), None, 3))
        assert overview["report_row_count"] == 7
        assert overview["report_day_count"] == 2
        assert overview["employee_count"] == 5
        assert overview["actual_seconds"] == 280
        assert overview["scheduled_seconds"] == 600
        assert len(trend) == 2
        assert [row["report_row_count"] for row in trend] == [6, 1]
        assert [row["employee_count"] for row in trend] == [5, 1]
        assert period_counts == {"all": 5}
        assert sum(row["actual_seconds"] for row in trend) == 280
        assert len(ranking) == 3
        assert all(row["org_id"] is not None for row in ranking)
        all_ranking = list(repository.get_ranking_aggregates(
            date(2026, 1, 1), date(2026, 1, 2), None, 100
        ))
        identities = {(row["org_id"], row["identity_source"], row["employee_key"]) for row in all_ranking}
        assert len(identities) == 5
        assert ("A", "person_id", "123") in identities
        assert ("B", "person_id", "123") in identities
        assert ("A", "person_no", "123") in identities
        assert ("B", "person_no", "123") in identities
        assert ("A", "person_no", "W") in identities
        scoped = next(row for row in all_ranking if row["org_id"] == "A" and row["identity_source"] == "person_id")
        assert scoped["actual_seconds"] == 30
        assert scoped["report_day_count"] == 2
        assert scoped["person_name"] == "Alpha"
        assert scoped["department_name"] == "Alpha Dept"
        assert repository.get_overview_aggregate(date(2026, 1, 1), date(2026, 1, 2), "B")["employee_count"] == 2
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


@pytest.mark.parametrize(
    "path",
    [
        "/dashboard/overview", "/dashboard/work-hours/trend",
        "/dashboard/work-hours/ranking", "/dashboard/attendance-exceptions",
    ],
)
def test_every_route_without_analytics_permission_is_forbidden(path):
    app = FastAPI()
    app.include_router(dashboard_router)
    guard = dashboard_router.routes[0].dependencies[0].dependency
    def denied():
        raise HTTPException(status_code=403, detail="Missing required permission: analytics:read")
    app.dependency_overrides[guard] = denied
    assert TestClient(app).get(path).status_code == 403


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


@pytest.mark.parametrize(
    "path",
    [
        "/dashboard/overview", "/dashboard/work-hours/trend",
        "/dashboard/work-hours/ranking", "/dashboard/attendance-exceptions",
    ],
)
def test_every_route_succeeds_with_permission_guard(path, monkeypatch):
    _stub_range(monkeypatch, [])
    monkeypatch.setattr(repository, "get_exceptions", lambda *args: [])
    app = FastAPI()
    app.include_router(dashboard_router)
    guard = dashboard_router.routes[0].dependencies[0].dependency
    app.dependency_overrides[guard] = lambda: object()
    assert TestClient(app).get(path).status_code == 200
