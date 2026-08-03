"""Explicit, parameterized, read-only T-SQL for Luna attendance analytics."""

from datetime import date
from typing import Any

from .constants import ACTIVE_DEL_STATUS
from .db import execute_luna_select


_ORG = "NULLIF(LTRIM(RTRIM(org_id)), '')"
_PERSON_ID = "NULLIF(LTRIM(RTRIM(person_id)), '')"
_PERSON_NO = "NULLIF(LTRIM(RTRIM(person_no)), '')"
_IDENTITY = f"COALESCE({_PERSON_ID}, {_PERSON_NO})"
_SOURCE = f"CASE WHEN {_PERSON_ID} IS NOT NULL THEN 'person_id' ELSE 'person_no' END"
_DURATION_SELECT = """
    COALESCE(SUM(plan_work_time), 0) AS scheduled_seconds,
    COALESCE(SUM(real_work_time), 0) AS actual_seconds,
    COALESCE(SUM(normal_time), 0) AS normal_seconds,
    COALESCE(SUM(overwork_time), 0) AS overtime_seconds,
    COALESCE(SUM(late_time), 0) AS late_seconds,
    COALESCE(SUM(early_time), 0) AS early_seconds,
    COALESCE(SUM(absent_time), 0) AS absent_seconds
"""


def _org_clause(org_id: str | None, *, alias: str = "") -> tuple[str, dict[str, Any]]:
    if org_id is None:
        return "", {}
    prefix = f"{alias}." if alias else ""
    return f" AND NULLIF(LTRIM(RTRIM({prefix}org_id)), '') = :org_id", {"org_id": org_id}


def _range_params(start_date: date, end_date: date, org_id: str | None = None):
    clause, params = _org_clause(org_id)
    return clause, {"active": ACTIVE_DEL_STATUS, "start_date": start_date, "end_date": end_date, **params}


def organizations_statement() -> tuple[str, dict[str, Any]]:
    sql = """
SELECT DISTINCT org_id
FROM (
    SELECT DISTINCT NULLIF(LTRIM(RTRIM(org_id)), '') AS org_id
    FROM dbo.saas_ca_report_daily WHERE del_status = :active
    UNION ALL
    SELECT DISTINCT NULLIF(LTRIM(RTRIM(org_id)), '') AS org_id
    FROM dbo.saas_ca_report_exception WHERE del_status = :active
    UNION ALL
    SELECT DISTINCT NULLIF(LTRIM(RTRIM(org_id)), '') AS org_id
    FROM dbo.saas_ca_person WHERE del_status = :active
) AS active_organization_sources
WHERE org_id IS NOT NULL
ORDER BY org_id
"""
    return sql, {"active": ACTIVE_DEL_STATUS}


def get_organizations():
    return execute_luna_select(*organizations_statement())


def latest_report_date_statement(org_id: str | None = None):
    clause, params = _org_clause(org_id)
    return f"""
SELECT MAX(report_date) AS latest
FROM dbo.saas_ca_report_daily
WHERE del_status = :active{clause}
""", {"active": ACTIVE_DEL_STATUS, **params}


def get_latest_report_date(org_id: str | None = None) -> date | None:
    rows = execute_luna_select(*latest_report_date_statement(org_id))
    return rows[0]["latest"] if rows else None


def overview_statement(start_date: date, end_date: date, org_id: str | None = None):
    clause, params = _range_params(start_date, end_date, org_id)
    return f"""
SELECT COUNT(*) AS report_row_count,
       COUNT(DISTINCT report_date) AS report_day_count,
       {_DURATION_SELECT}
FROM dbo.saas_ca_report_daily
WHERE del_status = :active AND report_date >= :start_date AND report_date <= :end_date{clause}
""", params


def scoped_identity_count_statement(start_date: date, end_date: date, org_id: str | None = None):
    clause, params = _range_params(start_date, end_date, org_id)
    return f"""
SELECT COUNT(*) AS employee_count
FROM (
    SELECT DISTINCT {_ORG} AS org_id, {_SOURCE} AS identity_source, {_IDENTITY} AS identity_value
    FROM dbo.saas_ca_report_daily
    WHERE del_status = :active AND report_date >= :start_date AND report_date <= :end_date
      AND {_IDENTITY} IS NOT NULL{clause}
) AS scoped_identities
""", params


def get_overview_aggregate(start_date: date, end_date: date, org_id: str | None = None):
    aggregate = dict(execute_luna_select(*overview_statement(start_date, end_date, org_id))[0])
    identity = execute_luna_select(*scoped_identity_count_statement(start_date, end_date, org_id))[0]
    aggregate["employee_count"] = int(identity["employee_count"])
    return aggregate


def trend_dates_statement(start_date: date, end_date: date, org_id: str | None = None):
    clause, params = _range_params(start_date, end_date, org_id)
    return f"""
SELECT report_date, COUNT(*) AS report_row_count, {_DURATION_SELECT}
FROM dbo.saas_ca_report_daily
WHERE del_status = :active AND report_date >= :start_date AND report_date <= :end_date{clause}
GROUP BY report_date
ORDER BY report_date
""", params


def trend_date_identity_counts_statement(start_date: date, end_date: date, org_id: str | None = None):
    clause, params = _range_params(start_date, end_date, org_id)
    return f"""
SELECT report_date, COUNT(*) AS employee_count
FROM (
    SELECT DISTINCT report_date, {_ORG} AS org_id, {_SOURCE} AS identity_source, {_IDENTITY} AS identity_value
    FROM dbo.saas_ca_report_daily
    WHERE del_status = :active AND report_date >= :start_date AND report_date <= :end_date
      AND {_IDENTITY} IS NOT NULL{clause}
) AS date_identities
GROUP BY report_date
ORDER BY report_date
""", params


def get_trend_date_aggregates(start_date: date, end_date: date, org_id: str | None = None):
    totals = [dict(row) for row in execute_luna_select(*trend_dates_statement(start_date, end_date, org_id))]
    counts = {row["report_date"]: int(row["employee_count"]) for row in execute_luna_select(*trend_date_identity_counts_statement(start_date, end_date, org_id))}
    for row in totals:
        row["employee_count"] = counts.get(row["report_date"], 0)
        if isinstance(row["report_date"], str):
            row["report_date"] = date.fromisoformat(row["report_date"])
    return totals


def trend_period_identity_counts_statement(periods: list[tuple[str, date, date]], org_id: str | None = None):
    if not periods:
        raise ValueError("At least one trend period is required")
    org_clause, org_params = _org_clause(org_id)
    selects, params = [], {"active": ACTIVE_DEL_STATUS, **org_params}
    for index, (_key, _start, _end) in enumerate(periods):
        selects.append(f"""
SELECT :period_key_{index} AS period_key, COUNT(*) AS employee_count
FROM (
    SELECT DISTINCT {_ORG} AS org_id, {_SOURCE} AS identity_source, {_IDENTITY} AS identity_value
    FROM dbo.saas_ca_report_daily
    WHERE del_status = :active AND report_date >= :period_start_{index} AND report_date <= :period_end_{index}
      AND {_IDENTITY} IS NOT NULL{org_clause}
) AS period_identities_{index}""")
        params = {**params, f"period_key_{index}": periods[index][0], f"period_start_{index}": periods[index][1], f"period_end_{index}": periods[index][2]}
    return "\nUNION ALL\n".join(selects), params


def get_trend_period_employee_counts(periods: list[tuple[str, date, date]], org_id: str | None = None) -> dict[str, int]:
    rows = execute_luna_select(*trend_period_identity_counts_statement(periods, org_id))
    return {row["period_key"]: int(row["employee_count"]) for row in rows}


def ranking_statement(start_date: date, end_date: date, org_id: str | None, limit: int | None):
    clause, params = _range_params(start_date, end_date, org_id)
    limit_clause = ""
    if limit is not None:
        params["limit"] = limit
        limit_clause = " WHERE row_position <= :limit"
    return f"""
WITH scoped AS (
    SELECT {_ORG} AS org_id, {_SOURCE} AS identity_source, {_IDENTITY} AS employee_key,
           {_PERSON_NO} AS person_no, person_name, dept_name, report_date,
           plan_work_time, real_work_time, normal_time, overwork_time, late_time, early_time, absent_time
    FROM dbo.saas_ca_report_daily
    WHERE del_status = :active AND report_date >= :start_date AND report_date <= :end_date
      AND {_IDENTITY} IS NOT NULL{clause}
), aggregated AS (
    SELECT org_id, identity_source, employee_key,
           CASE WHEN identity_source = 'person_id' THEN employee_key END AS person_id,
           MIN(person_no) AS person_no, MIN(person_name) AS person_name, MIN(dept_name) AS department_name,
           COUNT(DISTINCT report_date) AS report_day_count,
           COALESCE(SUM(plan_work_time), 0) AS scheduled_seconds,
           COALESCE(SUM(real_work_time), 0) AS actual_seconds,
           COALESCE(SUM(normal_time), 0) AS normal_seconds,
           COALESCE(SUM(overwork_time), 0) AS overtime_seconds,
           COALESCE(SUM(late_time), 0) AS late_seconds,
           COALESCE(SUM(early_time), 0) AS early_seconds,
           COALESCE(SUM(absent_time), 0) AS absent_seconds
    FROM scoped GROUP BY org_id, identity_source, employee_key
), ranked AS (
    SELECT ROW_NUMBER() OVER (ORDER BY actual_seconds DESC,
           CASE WHEN person_no IS NULL THEN 1 ELSE 0 END, person_no,
           CASE WHEN person_id IS NULL THEN 1 ELSE 0 END, person_id,
           org_id, identity_source, employee_key) AS row_position, *
    FROM aggregated
)
SELECT org_id, identity_source, employee_key, person_id, person_no, person_name,
       department_name, report_day_count, scheduled_seconds, actual_seconds,
       normal_seconds, overtime_seconds, late_seconds, early_seconds, absent_seconds
FROM ranked{limit_clause} ORDER BY row_position
""", params


def get_ranking_aggregates(start_date: date, end_date: date, org_id: str | None, limit: int | None):
    return execute_luna_select(*ranking_statement(start_date, end_date, org_id, limit))


def exception_count_statement(start_date: date, end_date: date, org_id: str | None = None):
    clause, params = _range_params(start_date, end_date, org_id)
    return f"""
SELECT COUNT(*) AS total FROM dbo.saas_ca_report_exception
WHERE del_status = :active AND report_date >= :start_date AND report_date <= :end_date{clause}
""", params


def count_exceptions(start_date: date, end_date: date, org_id: str | None = None) -> int:
    rows = execute_luna_select(*exception_count_statement(start_date, end_date, org_id))
    return int(rows[0]["total"]) if rows else 0


def exceptions_statement(start_date: date, end_date: date, org_id: str | None, page: int, page_size: int):
    clause, params = _range_params(start_date, end_date, org_id)
    params = {**params, "row_start": (page - 1) * page_size + 1, "row_end": page * page_size}
    exception_org_clause = " AND NULLIF(LTRIM(RTRIM(exception_report.org_id)), '') = :org_id" if org_id is not None else ""
    return f"""
WITH normalized_people AS (
    SELECT id, {_ORG} AS org_id, person_id, person_no, person_name
    FROM dbo.saas_ca_person WHERE del_status = :active
), active_person_ids AS (
    SELECT org_id, person_id, MIN(id) AS person_row_id
    FROM normalized_people GROUP BY org_id, person_id
), ranked_exceptions AS (
    SELECT ROW_NUMBER() OVER (ORDER BY exception_report.report_date DESC,
               exception_report.clock_time DESC, exception_report.id DESC) AS row_number,
           exception_report.id, NULLIF(LTRIM(RTRIM(exception_report.org_id)), '') AS org_id,
           exception_report.person_id, person.person_no, person.person_name,
           exception_report.report_date, exception_report.clock_time,
           exception_report.device_key, exception_report.device_name
    FROM dbo.saas_ca_report_exception AS exception_report
    LEFT JOIN active_person_ids ON active_person_ids.org_id = NULLIF(LTRIM(RTRIM(exception_report.org_id)), '')
         AND active_person_ids.person_id = exception_report.person_id
    LEFT JOIN normalized_people AS person ON person.id = active_person_ids.person_row_id
    WHERE exception_report.del_status = :active
      AND exception_report.report_date >= :start_date AND exception_report.report_date <= :end_date{exception_org_clause}
)
SELECT id, org_id, person_id, person_no, person_name, report_date, clock_time, device_key, device_name
FROM ranked_exceptions WHERE row_number >= :row_start AND row_number <= :row_end
ORDER BY row_number
""", params


def get_exceptions(start_date: date, end_date: date, org_id: str | None, page: int, page_size: int):
    return execute_luna_select(*exceptions_statement(start_date, end_date, org_id, page, page_size))
