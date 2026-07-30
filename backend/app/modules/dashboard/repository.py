"""Bounded cross-dialect SQLAlchemy Core aggregates for Luna analytics."""

from datetime import date
from typing import Any

from sqlalchemy import Select, and_, case, distinct, func, literal, select, union_all

from .constants import ACTIVE_DEL_STATUS
from .db import _execute_luna_select
from .tables import saas_ca_person, saas_ca_report_daily, saas_ca_report_exception


_DURATION_AGGREGATES = {
    "scheduled_seconds": saas_ca_report_daily.c.plan_work_time,
    "actual_seconds": saas_ca_report_daily.c.real_work_time,
    "normal_seconds": saas_ca_report_daily.c.normal_time,
    "overtime_seconds": saas_ca_report_daily.c.overwork_time,
    "late_seconds": saas_ca_report_daily.c.late_time,
    "early_seconds": saas_ca_report_daily.c.early_time,
    "absent_seconds": saas_ca_report_daily.c.absent_time,
}


def _normalized_identity_columns():
    person_id = func.nullif(func.trim(saas_ca_report_daily.c.person_id), "")
    person_no = func.nullif(func.trim(saas_ca_report_daily.c.person_no), "")
    source = case((person_id.is_not(None), literal("person_id")), else_=literal("person_no"))
    value = func.coalesce(person_id, person_no)
    return person_id, person_no, source, value


def _daily_predicates(start_date: date, end_date: date, org_id: str | None):
    predicates = [
        saas_ca_report_daily.c.del_status == ACTIVE_DEL_STATUS,
        saas_ca_report_daily.c.report_date >= start_date,
        saas_ca_report_daily.c.report_date <= end_date,
    ]
    if org_id is not None:
        predicates.append(saas_ca_report_daily.c.org_id == org_id)
    return predicates


def _sum_columns():
    return [
        func.coalesce(func.sum(column), 0).label(name)
        for name, column in _DURATION_AGGREGATES.items()
    ]


def latest_report_date_statement(org_id: str | None = None) -> Select[Any]:
    predicates = [saas_ca_report_daily.c.del_status == ACTIVE_DEL_STATUS]
    if org_id is not None:
        predicates.append(saas_ca_report_daily.c.org_id == org_id)
    return select(func.max(saas_ca_report_daily.c.report_date).label("latest")).where(*predicates)


def get_latest_report_date(org_id: str | None = None) -> date | None:
    rows = _execute_luna_select(latest_report_date_statement(org_id))
    return rows[0]["latest"] if rows else None


def overview_statement(start_date: date, end_date: date, org_id: str | None = None) -> Select[Any]:
    return select(
        func.count().label("report_row_count"),
        func.count(distinct(saas_ca_report_daily.c.report_date)).label("report_day_count"),
        *_sum_columns(),
    ).where(*_daily_predicates(start_date, end_date, org_id))


def scoped_identity_count_statement(
    start_date: date, end_date: date, org_id: str | None = None
) -> Select[Any]:
    _person_id, _person_no, source, value = _normalized_identity_columns()
    identities = (
        select(saas_ca_report_daily.c.org_id, source.label("identity_source"), value.label("identity_value"))
        .where(*_daily_predicates(start_date, end_date, org_id), value.is_not(None))
        .group_by(saas_ca_report_daily.c.org_id, source, value)
        .subquery("scoped_identities")
    )
    return select(func.count().label("employee_count")).select_from(identities)


def get_overview_aggregate(start_date: date, end_date: date, org_id: str | None = None):
    aggregate = dict(_execute_luna_select(overview_statement(start_date, end_date, org_id))[0])
    identity = _execute_luna_select(scoped_identity_count_statement(start_date, end_date, org_id))[0]
    aggregate["employee_count"] = int(identity["employee_count"])
    return aggregate


def trend_dates_statement(start_date: date, end_date: date, org_id: str | None = None) -> Select[Any]:
    return (
        select(
            saas_ca_report_daily.c.report_date,
            func.count().label("report_row_count"),
            *_sum_columns(),
        )
        .where(*_daily_predicates(start_date, end_date, org_id))
        .group_by(saas_ca_report_daily.c.report_date)
        .order_by(saas_ca_report_daily.c.report_date)
    )


def trend_date_identity_counts_statement(
    start_date: date, end_date: date, org_id: str | None = None
) -> Select[Any]:
    _person_id, _person_no, source, value = _normalized_identity_columns()
    identities = (
        select(
            saas_ca_report_daily.c.report_date,
            saas_ca_report_daily.c.org_id,
            source.label("identity_source"),
            value.label("identity_value"),
        )
        .where(*_daily_predicates(start_date, end_date, org_id), value.is_not(None))
        .group_by(saas_ca_report_daily.c.report_date, saas_ca_report_daily.c.org_id, source, value)
        .subquery("date_identities")
    )
    return (
        select(identities.c.report_date, func.count().label("employee_count"))
        .group_by(identities.c.report_date)
        .order_by(identities.c.report_date)
    )


def get_trend_date_aggregates(start_date: date, end_date: date, org_id: str | None = None):
    totals = [dict(row) for row in _execute_luna_select(trend_dates_statement(start_date, end_date, org_id))]
    counts = {
        row["report_date"]: int(row["employee_count"])
        for row in _execute_luna_select(trend_date_identity_counts_statement(start_date, end_date, org_id))
    }
    for row in totals:
        row["employee_count"] = counts.get(row["report_date"], 0)
    return totals


def trend_period_identity_counts_statement(
    periods: list[tuple[str, date, date]], org_id: str | None = None
):
    """Build one portable statement yielding one scoped identity count per period."""
    period_selects = []
    for index, (period_key, period_start, period_end) in enumerate(periods):
        _person_id, _person_no, source, value = _normalized_identity_columns()
        identities = (
            select(
                saas_ca_report_daily.c.org_id,
                source.label("identity_source"),
                value.label("identity_value"),
            )
            .where(*_daily_predicates(period_start, period_end, org_id), value.is_not(None))
            .group_by(saas_ca_report_daily.c.org_id, source, value)
            .subquery(f"period_identities_{index}")
        )
        period_selects.append(
            select(
                literal(period_key).label("period_key"),
                func.count().label("employee_count"),
            ).select_from(identities)
        )
    if not period_selects:
        raise ValueError("At least one trend period is required")
    combined = union_all(*period_selects).subquery("all_period_employee_counts")
    return select(combined.c.period_key, combined.c.employee_count)


def get_trend_period_employee_counts(
    periods: list[tuple[str, date, date]], org_id: str | None = None
) -> dict[str, int]:
    rows = _execute_luna_select(trend_period_identity_counts_statement(periods, org_id))
    return {row["period_key"]: int(row["employee_count"]) for row in rows}


def ranking_statement(
    start_date: date, end_date: date, org_id: str | None, limit: int
) -> Select[Any]:
    person_id, person_no, source, value = _normalized_identity_columns()
    display_person_no = func.min(person_no)
    display_person_name = func.min(saas_ca_report_daily.c.person_name)
    display_department = func.min(saas_ca_report_daily.c.dept_name)
    actual_total = func.coalesce(func.sum(saas_ca_report_daily.c.real_work_time), 0)
    selected_person_id = case((source == literal("person_id"), value), else_=None)
    statement = (
        select(
            saas_ca_report_daily.c.org_id,
            source.label("identity_source"),
            value.label("employee_key"),
            selected_person_id.label("person_id"),
            display_person_no.label("person_no"),
            display_person_name.label("person_name"),
            display_department.label("department_name"),
            func.count(distinct(saas_ca_report_daily.c.report_date)).label("report_day_count"),
            *_sum_columns(),
        )
        .where(*_daily_predicates(start_date, end_date, org_id), value.is_not(None))
        .group_by(saas_ca_report_daily.c.org_id, source, value)
        .order_by(
            actual_total.desc(),
            case((display_person_no.is_(None), 1), else_=0),
            display_person_no,
            case((selected_person_id.is_(None), 1), else_=0),
            selected_person_id,
            saas_ca_report_daily.c.org_id,
            source,
            value,
        )
        .limit(limit)
    )
    return statement


def get_ranking_aggregates(start_date: date, end_date: date, org_id: str | None, limit: int):
    return _execute_luna_select(ranking_statement(start_date, end_date, org_id, limit))


def exception_count_statement(start_date: date, end_date: date, org_id: str | None = None) -> Select[Any]:
    predicates = [
        saas_ca_report_exception.c.del_status == ACTIVE_DEL_STATUS,
        saas_ca_report_exception.c.report_date >= start_date,
        saas_ca_report_exception.c.report_date <= end_date,
    ]
    if org_id is not None:
        predicates.append(saas_ca_report_exception.c.org_id == org_id)
    return select(func.count().label("total")).select_from(saas_ca_report_exception).where(*predicates)


def count_exceptions(start_date: date, end_date: date, org_id: str | None = None) -> int:
    rows = _execute_luna_select(exception_count_statement(start_date, end_date, org_id))
    return int(rows[0]["total"]) if rows else 0


def exceptions_statement(
    start_date: date, end_date: date, org_id: str | None, page: int, page_size: int
) -> Select[Any]:
    active_person_ids = (
        select(
            saas_ca_person.c.org_id.label("org_id"), saas_ca_person.c.person_id.label("person_id"),
            func.min(saas_ca_person.c.id).label("person_row_id"),
        )
        .where(saas_ca_person.c.del_status == ACTIVE_DEL_STATUS)
        .group_by(saas_ca_person.c.org_id, saas_ca_person.c.person_id)
        .subquery("active_person_ids")
    )
    person = saas_ca_person.alias("exception_person")
    predicates = [
        saas_ca_report_exception.c.del_status == ACTIVE_DEL_STATUS,
        saas_ca_report_exception.c.report_date >= start_date,
        saas_ca_report_exception.c.report_date <= end_date,
    ]
    if org_id is not None:
        predicates.append(saas_ca_report_exception.c.org_id == org_id)
    return (
        select(
            saas_ca_report_exception.c.id, saas_ca_report_exception.c.org_id,
            saas_ca_report_exception.c.person_id, person.c.person_no, person.c.person_name,
            saas_ca_report_exception.c.report_date, saas_ca_report_exception.c.clock_time,
            saas_ca_report_exception.c.device_key, saas_ca_report_exception.c.device_name,
        )
        .select_from(
            saas_ca_report_exception.outerjoin(
                active_person_ids,
                and_(active_person_ids.c.org_id == saas_ca_report_exception.c.org_id,
                     active_person_ids.c.person_id == saas_ca_report_exception.c.person_id),
            ).outerjoin(person, person.c.id == active_person_ids.c.person_row_id)
        )
        .where(*predicates)
        .order_by(saas_ca_report_exception.c.report_date.desc(),
                  saas_ca_report_exception.c.clock_time.desc(), saas_ca_report_exception.c.id.desc())
        .offset((page - 1) * page_size).limit(page_size)
    )


def get_exceptions(start_date: date, end_date: date, org_id: str | None, page: int, page_size: int):
    return _execute_luna_select(exceptions_statement(start_date, end_date, org_id, page, page_size))
