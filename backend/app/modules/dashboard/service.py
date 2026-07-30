"""Business rules and response assembly for dashboard analytics."""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from math import ceil
from typing import Any

from app.core.response import Meta

from . import repository
from .constants import DEFAULT_RANGE_DAYS, DURATION_UNIT
from .schemas import (
    AttendanceExceptionItem,
    DashboardDataStatus,
    DashboardOverview,
    DashboardOrganizationOption,
    DashboardTrend,
    DashboardTrendGranularity,
    DashboardTrendPoint,
    EmployeeWorkHoursRanking,
    EmployeeWorkHoursRankingItem,
)


def get_organizations() -> list[DashboardOrganizationOption]:
    return [DashboardOrganizationOption(org_id=row["org_id"]) for row in repository.get_organizations()]


class DashboardRangeError(ValueError):
    """Safe client error for invalid or excessive date ranges."""


@dataclass(frozen=True)
class EffectiveRange:
    start: date | None
    end: date | None
    latest: date | None
    org_id: str | None


_DURATION_COLUMNS = {
    "scheduled_seconds": "plan_work_time",
    "actual_seconds": "real_work_time",
    "normal_seconds": "normal_time",
    "overtime_seconds": "overwork_time",
    "late_seconds": "late_time",
    "early_seconds": "early_time",
    "absent_seconds": "absent_time",
}


def resolve_range(
    start_date: date | None, end_date: date | None, org_id: str | None, max_days: int
) -> EffectiveRange:
    if start_date is not None and end_date is not None:
        if start_date > end_date:
            raise DashboardRangeError("start_date must not be after end_date")
        if (end_date - start_date).days + 1 > max_days:
            raise DashboardRangeError(f"Date range exceeds the {max_days}-day limit")
    latest = repository.get_latest_report_date(org_id)
    if latest is None:
        return EffectiveRange(None, None, None, org_id)
    effective_end = end_date or latest
    effective_start = start_date or (effective_end - timedelta(days=DEFAULT_RANGE_DAYS - 1))
    if effective_start > effective_end:
        raise DashboardRangeError("start_date must not be after end_date")
    inclusive_days = (effective_end - effective_start).days + 1
    if inclusive_days > max_days:
        raise DashboardRangeError(f"Date range exceeds the {max_days}-day limit")
    return EffectiveRange(effective_start, effective_end, latest, org_id)


def _aggregate_totals(rows) -> dict[str, int]:
    return {
        response_name: max(sum(int(row.get(response_name) or 0) for row in rows), 0)
        for response_name in _DURATION_COLUMNS
    }


def _range_fields(value: EffectiveRange) -> dict[str, Any]:
    return {
        "effective_start_date": value.start,
        "effective_end_date": value.end,
        "source_latest_report_date": value.latest,
        "org_id": value.org_id,
    }


def get_overview(start_date, end_date, org_id, max_days: int) -> DashboardOverview:
    resolved = resolve_range(start_date, end_date, org_id, max_days)
    aggregate = None if resolved.start is None else repository.get_overview_aggregate(
        resolved.start, resolved.end, org_id
    )
    exception_count = 0 if resolved.start is None else repository.count_exceptions(resolved.start, resolved.end, org_id)
    report_row_count = int(aggregate["report_row_count"]) if aggregate else 0
    return DashboardOverview(
        **_range_fields(resolved),
        data_status=DashboardDataStatus.AVAILABLE if report_row_count else DashboardDataStatus.EMPTY,
        duration_unit=DURATION_UNIT,
        report_row_count=report_row_count,
        report_day_count=int(aggregate["report_day_count"]) if aggregate else 0,
        employee_count=int(aggregate["employee_count"]) if aggregate else 0,
        reported_exception_count=max(exception_count, 0),
        **({name: max(int(aggregate[name] or 0), 0) for name in _DURATION_COLUMNS} if aggregate else _aggregate_totals([])),
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
    start = date(day.year, 1, 1)
    return str(day.year), start, date(day.year, 12, 31)


def get_trend(start_date, end_date, org_id, granularity, max_days: int) -> DashboardTrend:
    resolved = resolve_range(start_date, end_date, org_id, max_days)
    rows = [] if resolved.start is None else list(
        repository.get_trend_date_aggregates(resolved.start, resolved.end, org_id)
    )
    buckets: dict[str, dict[str, Any]] = {}
    for row in rows:
        key, period_start, period_end = _period_bounds(row["report_date"], granularity)
        bucket = buckets.setdefault(
            key,
            {"rows": [], "start": max(period_start, resolved.start), "end": min(period_end, resolved.end)},
        )
        bucket["rows"].append(row)
    if granularity == DashboardTrendGranularity.DAY:
        employee_counts = {
            key: int(bucket["rows"][0]["employee_count"])
            for key, bucket in buckets.items()
        }
    else:
        descriptors = [
            (key, bucket["start"], bucket["end"])
            for key, bucket in sorted(buckets.items(), key=lambda item: item[1]["start"])
        ]
        employee_counts = (
            repository.get_trend_period_employee_counts(descriptors, org_id)
            if descriptors else {}
        )
    points = []
    for key, bucket in sorted(buckets.items(), key=lambda item: item[1]["start"]):
        period_rows = bucket["rows"]
        points.append(DashboardTrendPoint(
            period_key=key,
            period_start=bucket["start"],
            period_end=bucket["end"],
            report_row_count=sum(int(row["report_row_count"] or 0) for row in period_rows),
            employee_count=employee_counts.get(key, 0),
            **_aggregate_totals(period_rows),
        ))
    return DashboardTrend(
        **_range_fields(resolved),
        data_status=DashboardDataStatus.AVAILABLE if rows else DashboardDataStatus.EMPTY,
        duration_unit=DURATION_UNIT,
        granularity=granularity,
        points=points,
    )


def get_ranking(start_date, end_date, org_id, limit: int, max_days: int) -> EmployeeWorkHoursRanking:
    resolved = resolve_range(start_date, end_date, org_id, max_days)
    rows = [] if resolved.start is None else list(
        repository.get_ranking_aggregates(resolved.start, resolved.end, org_id, limit)
    )
    items = []
    for index, row in enumerate(rows, 1):
        item = dict(row)
        item.pop("identity_source", None)
        items.append(EmployeeWorkHoursRankingItem(rank=index, **item))
    return EmployeeWorkHoursRanking(
        **_range_fields(resolved),
        data_status=DashboardDataStatus.AVAILABLE if rows else DashboardDataStatus.EMPTY,
        duration_unit=DURATION_UNIT,
        items=items,
    )


def get_attendance_exceptions(start_date, end_date, org_id, page: int, page_size: int, max_days: int):
    resolved = resolve_range(start_date, end_date, org_id, max_days)
    if resolved.start is None:
        return [], Meta(page=page, page_size=page_size, total=0, pages=0)
    total = repository.count_exceptions(resolved.start, resolved.end, org_id)
    rows = repository.get_exceptions(resolved.start, resolved.end, org_id, page, page_size)
    items = [AttendanceExceptionItem.model_validate(row) for row in rows]
    return items, Meta(page=page, page_size=page_size, total=total, pages=ceil(total / page_size) if total else 0)
