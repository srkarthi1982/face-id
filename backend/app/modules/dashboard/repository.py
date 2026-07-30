"""Cross-dialect SQLAlchemy Core reads for Luna dashboard analytics."""

from datetime import date
from typing import Any

from sqlalchemy import Select, and_, func, select

from .constants import ACTIVE_DEL_STATUS
from .db import _execute_luna_select
from .tables import saas_ca_person, saas_ca_report_daily, saas_ca_report_exception


DAILY_FIELDS = (
    saas_ca_report_daily.c.report_date,
    saas_ca_report_daily.c.person_id,
    saas_ca_report_daily.c.person_no,
    saas_ca_report_daily.c.person_name,
    saas_ca_report_daily.c.dept_name,
    saas_ca_report_daily.c.plan_work_time,
    saas_ca_report_daily.c.real_work_time,
    saas_ca_report_daily.c.normal_time,
    saas_ca_report_daily.c.overwork_time,
    saas_ca_report_daily.c.late_time,
    saas_ca_report_daily.c.early_time,
    saas_ca_report_daily.c.absent_time,
)


def latest_report_date_statement(org_id: str | None = None) -> Select[Any]:
    predicates = [saas_ca_report_daily.c.del_status == ACTIVE_DEL_STATUS]
    if org_id is not None:
        predicates.append(saas_ca_report_daily.c.org_id == org_id)
    return select(func.max(saas_ca_report_daily.c.report_date).label("latest")).where(*predicates)


def get_latest_report_date(org_id: str | None = None) -> date | None:
    rows = _execute_luna_select(latest_report_date_statement(org_id))
    return rows[0]["latest"] if rows else None


def daily_rows_statement(start_date: date, end_date: date, org_id: str | None = None) -> Select[Any]:
    predicates = [
        saas_ca_report_daily.c.del_status == ACTIVE_DEL_STATUS,
        saas_ca_report_daily.c.report_date >= start_date,
        saas_ca_report_daily.c.report_date <= end_date,
    ]
    if org_id is not None:
        predicates.append(saas_ca_report_daily.c.org_id == org_id)
    return select(*DAILY_FIELDS).where(*predicates).order_by(
        saas_ca_report_daily.c.report_date,
        saas_ca_report_daily.c.person_no,
        saas_ca_report_daily.c.person_id,
    )


def get_daily_rows(start_date: date, end_date: date, org_id: str | None = None):
    return _execute_luna_select(daily_rows_statement(start_date, end_date, org_id))


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
            saas_ca_person.c.org_id.label("org_id"),
            saas_ca_person.c.person_id.label("person_id"),
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
            saas_ca_report_exception.c.id,
            saas_ca_report_exception.c.org_id,
            saas_ca_report_exception.c.person_id,
            person.c.person_no,
            person.c.person_name,
            saas_ca_report_exception.c.report_date,
            saas_ca_report_exception.c.clock_time,
            saas_ca_report_exception.c.device_key,
            saas_ca_report_exception.c.device_name,
        )
        .select_from(
            saas_ca_report_exception
            .outerjoin(
                active_person_ids,
                and_(
                    active_person_ids.c.org_id == saas_ca_report_exception.c.org_id,
                    active_person_ids.c.person_id == saas_ca_report_exception.c.person_id,
                ),
            )
            .outerjoin(person, person.c.id == active_person_ids.c.person_row_id)
        )
        .where(*predicates)
        .order_by(
            saas_ca_report_exception.c.report_date.desc(),
            saas_ca_report_exception.c.clock_time.desc(),
            saas_ca_report_exception.c.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )


def get_exceptions(start_date: date, end_date: date, org_id: str | None, page: int, page_size: int):
    return _execute_luna_select(exceptions_statement(start_date, end_date, org_id, page, page_size))
