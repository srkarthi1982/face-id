"""Business rules and response assembly for PostgreSQL attendance analytics."""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from math import ceil
from typing import Any

from sqlalchemy.orm import Session

from app.core.response import Meta

from . import repository
from .constants import DEFAULT_RANGE_DAYS, DURATION_UNIT
from .schemas import (
    AttendanceExceptionItem,
    DashboardDataStatus,
    DashboardDepartmentOption,
    DashboardOverview,
    DashboardTrend,
    DashboardTrendGranularity,
    DashboardTrendPoint,
    EmployeeWorkHoursRanking,
    EmployeeWorkHoursRankingItem,
)


class DashboardRangeError(ValueError):
    """Safe client error for invalid or excessive date ranges."""


@dataclass(frozen=True)
class EffectiveRange:
    start: date | None
    end: date | None
    latest: date | None
    department_id: int | None


_DURATION_COLUMNS = (
    "scheduled_seconds",
    "actual_seconds",
    "normal_seconds",
    "overtime_seconds",
    "late_seconds",
    "early_seconds",
    "absent_seconds",
)


def get_departments(db: Session) -> list[DashboardDepartmentOption]:
    return [DashboardDepartmentOption(**row) for row in repository.get_departments(db)]


def resolve_range(
    db: Session,
    start_date: date | None,
    end_date: date | None,
    department_id: int | None,
    max_days: int,
) -> EffectiveRange:
    if start_date is not None and end_date is not None:
        if start_date > end_date:
            raise DashboardRangeError("start_date must not be after end_date")
        if (end_date - start_date).days + 1 > max_days:
            raise DashboardRangeError(f"Date range exceeds the {max_days}-day limit")
    latest = repository.get_latest_report_date(db, department_id)
    if end_date is not None:
        effective_end = end_date
    elif latest is not None:
        effective_end = latest
    else:
        return EffectiveRange(None, None, None, department_id)
    effective_start = start_date or (effective_end - timedelta(days=DEFAULT_RANGE_DAYS - 1))
    if effective_start > effective_end:
        raise DashboardRangeError("start_date must not be after end_date")
    if (effective_end - effective_start).days + 1 > max_days:
        raise DashboardRangeError(f"Date range exceeds the {max_days}-day limit")
    return EffectiveRange(effective_start, effective_end, latest, department_id)


def _zero_totals() -> dict[str, int]:
    return {name: 0 for name in _DURATION_COLUMNS}


def _aggregate_totals(rows) -> dict[str, int]:
    return {name: max(sum(int(getattr(row, name, 0) or 0) for row in rows), 0) for name in _DURATION_COLUMNS}


def _range_fields(value: EffectiveRange) -> dict[str, Any]:
    return {
        "effective_start_date": value.start,
        "effective_end_date": value.end,
        "source_latest_report_date": value.latest,
        "department_id": value.department_id,
    }


def _days_for_range(db: Session, resolved: EffectiveRange):
    if resolved.start is None or resolved.end is None:
        return []
    return repository.build_employee_days(db, resolved.start, resolved.end, resolved.department_id)


def _exception_count(days) -> int:
    total = 0
    for day in days:
        if day.event_count == 0:
            total += 1
        elif day.event_count == 1:
            total += 1
        else:
            total += int(day.late_seconds > 0) + int(day.early_seconds > 0)
    return total


def get_overview(db: Session, start_date, end_date, department_id, max_days: int) -> DashboardOverview:
    resolved = resolve_range(db, start_date, end_date, department_id, max_days)
    days = _days_for_range(db, resolved)
    totals = _aggregate_totals(days) if days else _zero_totals()
    report_dates = {row.report_date for row in days}
    employees = {row.employee_key for row in days}
    return DashboardOverview(
        **_range_fields(resolved),
        data_status=DashboardDataStatus.AVAILABLE if days else DashboardDataStatus.EMPTY,
        duration_unit=DURATION_UNIT,
        report_row_count=len(days),
        report_day_count=len(report_dates),
        employee_count=len(employees),
        reported_exception_count=_exception_count(days),
        **totals,
    )


def _period_bounds(day: date, granularity: DashboardTrendGranularity) -> tuple[str, date, date]:
    if granularity == DashboardTrendGranularity.DAY:
        return day.isoformat(), day, day
    if granularity == DashboardTrendGranularity.WEEK:
        iso_year, iso_week, _ = day.isocalendar()
        start = day - timedelta(days=day.weekday())
        return f"{iso_year}-W{iso_week:02d}", start, start + timedelta(days=6)
    if granularity == DashboardTrendGranularity.MONTH:
        start = day.replace(day=1)
        return day.strftime("%Y-%m"), start, day.replace(day=monthrange(day.year, day.month)[1])
    return str(day.year), date(day.year, 1, 1), date(day.year, 12, 31)


def get_trend(db: Session, start_date, end_date, department_id, granularity, max_days: int) -> DashboardTrend:
    resolved = resolve_range(db, start_date, end_date, department_id, max_days)
    days = _days_for_range(db, resolved)
    buckets: dict[str, dict[str, Any]] = {}
    for row in days:
        key, period_start, period_end = _period_bounds(row.report_date, granularity)
        bucket = buckets.setdefault(
            key,
            {"rows": [], "start": max(period_start, resolved.start), "end": min(period_end, resolved.end)},
        )
        bucket["rows"].append(row)

    points = []
    for key, bucket in sorted(buckets.items(), key=lambda item: item[1]["start"]):
        rows = bucket["rows"]
        points.append(DashboardTrendPoint(
            period_key=key,
            period_start=bucket["start"],
            period_end=bucket["end"],
            report_row_count=len(rows),
            employee_count=len({row.employee_key for row in rows}),
            **_aggregate_totals(rows),
        ))
    return DashboardTrend(
        **_range_fields(resolved),
        data_status=DashboardDataStatus.AVAILABLE if points else DashboardDataStatus.EMPTY,
        duration_unit=DURATION_UNIT,
        granularity=granularity,
        points=points,
    )


def _ranking_scope(end_date: date | None, period: DashboardTrendGranularity | None) -> tuple[date | None, date | None]:
    if end_date is None or period is None:
        return None, None
    _, start, end = _period_bounds(end_date, period)
    return start, end


def get_ranking(
    db: Session,
    start_date,
    end_date,
    department_id,
    limit: int,
    max_days: int,
    include_all: bool,
    period: DashboardTrendGranularity | None,
) -> EmployeeWorkHoursRanking:
    resolved = resolve_range(db, start_date, end_date, department_id, max_days)
    ranking_start, ranking_end = _ranking_scope(resolved.end, period)
    if ranking_start is not None and resolved.start is not None and resolved.end is not None:
        scoped = EffectiveRange(
            max(resolved.start, ranking_start),
            min(resolved.end, ranking_end),
            resolved.latest,
            resolved.department_id,
        )
        days = _days_for_range(db, scoped)
    else:
        days = _days_for_range(db, resolved)

    grouped: dict[str, dict[str, Any]] = {}
    for row in days:
        item = grouped.setdefault(
            row.employee_key,
            {
                "department_id": row.department_id,
                "department_name": row.department_name,
                "employee_key": row.employee_key,
                "person_id": row.person_id,
                "person_no": row.person_no,
                "person_name": row.person_name,
                "report_dates": set(),
                **_zero_totals(),
            },
        )
        item["report_dates"].add(row.report_date)
        for name in _DURATION_COLUMNS:
            item[name] += getattr(row, name)
    sorted_rows = sorted(
        grouped.values(),
        key=lambda row: (
            -row["actual_seconds"],
            row["person_no"] is None,
            row["person_no"] or "",
            row["person_id"] is None,
            row["person_id"] or "",
            row["department_id"] or 0,
            row["employee_key"],
        ),
    )
    if not include_all:
        sorted_rows = sorted_rows[:limit]
    items = []
    for index, row in enumerate(sorted_rows, 1):
        values = dict(row)
        report_dates = values.pop("report_dates")
        items.append(EmployeeWorkHoursRankingItem(rank=index, report_day_count=len(report_dates), **values))
    return EmployeeWorkHoursRanking(
        **_range_fields(resolved),
        data_status=DashboardDataStatus.AVAILABLE if items else DashboardDataStatus.EMPTY,
        duration_unit=DURATION_UNIT,
        items=items,
    )


def _exception_rows(db: Session, days) -> list[AttendanceExceptionItem]:
    device_ids = {day.first_device_id for day in days if day.first_device_id} | {day.last_device_id for day in days if day.last_device_id}
    devices = repository.get_device_names(db, device_ids)
    rows: list[AttendanceExceptionItem] = []
    for day in sorted(days, key=lambda row: (row.report_date, row.person_no or "", row.employee_key)):
        specs = []
        if day.event_count == 0:
            specs.append(("ABSENT", None, None))
        elif day.event_count == 1:
            specs.append(("MISSING_PAIR", day.check_in, day.first_device_id))
        else:
            if day.late_seconds > 0:
                specs.append(("LATE", day.check_in, day.first_device_id))
            if day.early_seconds > 0:
                specs.append(("EARLY", day.check_out, day.last_device_id))
        for exception_type, clock_time, device_id in specs:
            device_key, device_name = devices.get(device_id, (None, None))
            rows.append(AttendanceExceptionItem(
                id=f"{day.personnel_id}:{day.report_date.isoformat()}:{exception_type}",
                exception_type=exception_type,
                department_id=day.department_id,
                department_name=day.department_name,
                person_id=day.person_id,
                person_no=day.person_no,
                person_name=day.person_name,
                report_date=day.report_date,
                clock_time=clock_time,
                device_key=device_key,
                device_name=device_name,
            ))
    return rows


def get_attendance_exceptions(db: Session, start_date, end_date, department_id, page: int, page_size: int, max_days: int):
    resolved = resolve_range(db, start_date, end_date, department_id, max_days)
    days = _days_for_range(db, resolved)
    all_items = _exception_rows(db, days)
    total = len(all_items)
    offset = (page - 1) * page_size
    return all_items[offset:offset + page_size], Meta(page=page, page_size=page_size, total=total, pages=ceil(total / page_size) if total else 0)
