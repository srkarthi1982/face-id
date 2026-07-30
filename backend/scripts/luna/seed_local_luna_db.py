#!/usr/bin/env python3
"""Seed deterministic synthetic Luna attendance data for local development.

Local-only provisional conventions:
- clock_type 1 = entry; clock_type 2 = exit.
- all duration columns are seconds.
These values must be confirmed against production Luna data before use there.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import create_engine, delete, insert, select, update

try:
    from scripts.luna.common import LocalLunaSetupError, target_admin_url
except ModuleNotFoundError:  # Direct script execution on Windows.
    from common import LocalLunaSetupError, target_admin_url
from app.modules.dashboard.tables import (
    saas_ca_clock_record,
    saas_ca_person,
    saas_ca_report_daily,
    saas_ca_report_exception,
)


CLOCK_TYPE_ENTRY = 1
CLOCK_TYPE_EXIT = 2
ACTIVE = 0
DELETED = 1
SEED_START = date(2025, 7, 1)
SEED_END = date(2026, 7, 29)
CREATED_AT = datetime(2026, 7, 30, 12, 0, 0)
ORG_ID = "SYNTHETIC-ORG"

EMPLOYEES = [
    (index, f"SYN-P-{index:03d}", f"SYN-{index:04d}", f"Synthetic Employee {index:02d}",
     ("Synthetic Operations", "Synthetic Security", "Synthetic Support")[(index - 1) % 3])
    for index in range(1, 13)
]


def _epoch_ms(value: datetime) -> int:
    return int(value.replace(tzinfo=timezone.utc).timestamp() * 1000)


def _days(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _clock_row(day: date, employee, sequence: int, moment: datetime, clock_type: int,
               *, fix_status: int = 0, del_status: int = ACTIVE) -> dict:
    index, person_id, person_no, person_name, _department = employee
    row_id = int(day.strftime("%Y%m%d")) * 1000 + index * 10 + sequence
    return {
        "id": row_id,
        "org_id": ORG_ID,
        "record_id": f"SYN-REC-{row_id}",
        "person_id": person_id,
        "person_no": person_no,
        "photo_id": f"SYN-PHOTO-{index:03d}",
        "photo_url": f"/synthetic/photos/{index:03d}.jpg",
        "device_key": "SYN-DEVICE-GATE-A" if index % 2 else "SYN-DEVICE-GATE-B",
        "recognition_time": _epoch_ms(moment),
        "fix_status": fix_status,
        "del_status": del_status,
        "gmt_modified": CREATED_AT,
        "gmt_create": CREATED_AT,
        "clock_type": clock_type,
        "person_name": person_name,
        "device_name": "Synthetic Main Gate A" if index % 2 else "Synthetic Main Gate B",
    }


def _completed_session_seconds(punches: list[tuple[datetime, int, int, int]]) -> int:
    """Pair active entry/exit punches and exclude time between sessions."""
    active_entry: datetime | None = None
    total = 0
    for moment, clock_type, _fix_status, del_status in sorted(punches):
        if del_status != ACTIVE:
            continue
        if clock_type == CLOCK_TYPE_ENTRY and active_entry is None:
            active_entry = moment
        elif clock_type == CLOCK_TYPE_EXIT and active_entry is not None:
            total += max(int((moment - active_entry).total_seconds()), 0)
            active_entry = None
    return total


def build_seed_rows() -> dict:
    persons = [
        {
            "id": index,
            "org_id": ORG_ID,
            "person_id": person_id,
            "person_no": person_no,
            "person_name": person_name,
            "del_status": ACTIVE,
            "gmt_modified": CREATED_AT,
            "gmt_create": CREATED_AT,
        }
        for index, person_id, person_no, person_name, _department in EMPLOYEES
    ]
    clocks: list[dict] = []
    daily: list[dict] = []
    exceptions: list[dict] = []

    missing_exit = (date(2025, 9, 15), 2)
    missing_entry = (date(2025, 10, 20), 3)
    multiple_sessions = (date(2025, 11, 18), 4)
    overnight = (date(2025, 12, 10), 5)
    corrected = (date(2026, 1, 14), 6)

    for day in _days(SEED_START, SEED_END):
        if day.weekday() >= 5:
            continue
        for employee in EMPLOYEES[:-1]:  # Employee 12 intentionally has no attendance.
            index, person_id, person_no, person_name, department = employee
            planned_in = datetime.combine(day, time(8, 0))
            planned_out = datetime.combine(day, time(16, 0))
            arrival = planned_in + timedelta(minutes=(index % 4) * 5)
            # Deliberately different totals support future ranking checks.
            departure = planned_out + timedelta(minutes=(index % 5) * 20 - 20)
            entry_status = 0 if arrival <= planned_in else 1
            exit_status = 0 if departure >= planned_out else 1

            if (day, index) == missing_exit:
                departure = None
            if (day, index) == missing_entry:
                arrival = None
            if (day, index) == overnight:
                arrival = datetime.combine(day, time(22, 0))
                departure = datetime.combine(day + timedelta(days=1), time(6, 0))

            punches: list[tuple[datetime, int, int, int]] = []
            if arrival:
                punches.append((arrival, CLOCK_TYPE_ENTRY, 0, ACTIVE))
            if departure:
                punches.append((departure, CLOCK_TYPE_EXIT, 0, ACTIVE))
            if (day, index) == multiple_sessions:
                punches = [
                    (datetime.combine(day, time(8, 0)), CLOCK_TYPE_ENTRY, 0, ACTIVE),
                    (datetime.combine(day, time(12, 0)), CLOCK_TYPE_EXIT, 0, ACTIVE),
                    (datetime.combine(day, time(13, 0)), CLOCK_TYPE_ENTRY, 0, ACTIVE),
                    (datetime.combine(day, time(17, 30)), CLOCK_TYPE_EXIT, 0, ACTIVE),
                ]
                arrival, departure = punches[0][0], punches[-1][0]
            if (day, index) == corrected:
                punches.extend([
                    (arrival, CLOCK_TYPE_ENTRY, 0, DELETED),  # duplicate logically deleted
                    (arrival + timedelta(minutes=1), CLOCK_TYPE_ENTRY, 1, ACTIVE),  # correction
                ])

            for sequence, (moment, clock_type, fix_status, del_status) in enumerate(punches, start=1):
                clocks.append(_clock_row(
                    day, employee, sequence, moment, clock_type,
                    fix_status=fix_status, del_status=del_status,
                ))

            real_seconds = _completed_session_seconds(punches)
            normal_seconds = min(real_seconds, 8 * 3600)
            over_seconds = max(real_seconds - 8 * 3600, 0)
            late_seconds = max(int((arrival - planned_in).total_seconds()), 0) if arrival else 8 * 3600
            early_seconds = max(int((planned_out - departure).total_seconds()), 0) if departure else 8 * 3600
            daily_id = int(day.strftime("%Y%m%d")) * 100 + index
            daily.append({
                "id": daily_id,
                "org_id": ORG_ID,
                "report_date": day,
                "person_id": person_id,
                "person_no": person_no,
                "person_name": person_name,
                "dept_name": department,
                "interval_id": 1,
                "interval_name": "Synthetic Day Shift",
                "plan_sign_in_datetime": planned_in,
                "plan_sign_out_datetime": planned_out,
                "plan_work_time": 8 * 3600,
                "clock_sign_in_datetime": arrival,
                "clock_sign_in_status": entry_status if arrival else 2,
                "clock_sign_out_datetime": departure,
                "clock_sign_out_status": exit_status if departure else 2,
                "real_work_time": real_seconds,
                "normal_time": normal_seconds,
                "late_time": late_seconds,
                "early_time": early_seconds,
                "absent_time": max(8 * 3600 - normal_seconds, 0),
                "sign_start_time": arrival,
                "sign_end_time": departure,
                "overwork_time": over_seconds,
                "date_type": 0,
                "del_status": ACTIVE,
                "gmt_modified": CREATED_AT,
                "gmt_create": CREATED_AT,
            })

    # Explicit weekend attendance scenario.
    weekend_day = date(2026, 2, 14)
    employee = EMPLOYEES[6]
    arrival = datetime.combine(weekend_day, time(9, 0))
    departure = datetime.combine(weekend_day, time(14, 0))
    clocks.extend([
        _clock_row(weekend_day, employee, 1, arrival, CLOCK_TYPE_ENTRY),
        _clock_row(weekend_day, employee, 2, departure, CLOCK_TYPE_EXIT),
    ])
    index, person_id, person_no, person_name, department = employee
    daily.append({
        "id": int(weekend_day.strftime("%Y%m%d")) * 100 + index,
        "org_id": ORG_ID, "report_date": weekend_day, "person_id": person_id,
        "person_no": person_no, "person_name": person_name, "dept_name": department,
        "interval_id": 2, "interval_name": "Synthetic Weekend Shift",
        "plan_sign_in_datetime": arrival, "plan_sign_out_datetime": departure,
        "plan_work_time": 5 * 3600, "clock_sign_in_datetime": arrival,
        "clock_sign_in_status": 0, "clock_sign_out_datetime": departure,
        "clock_sign_out_status": 0, "real_work_time": 5 * 3600,
        "normal_time": 0, "late_time": 0, "early_time": 0,
        "absent_time": 0, "sign_start_time": arrival, "sign_end_time": departure,
        "overwork_time": 5 * 3600, "date_type": 1, "del_status": ACTIVE,
        "gmt_modified": CREATED_AT, "gmt_create": CREATED_AT,
    })

    for exception_id, (day, employee_index, label, moment, device_key, device_name) in enumerate([
        (missing_exit[0], missing_exit[1], "missing-exit", datetime(2025, 9, 15, 8, 10), "SYN-DEVICE-GATE-A", "Synthetic Main Gate A"),
        (missing_entry[0], missing_entry[1], "missing-entry", datetime(2025, 10, 20, 16, 20), "SYN-DEVICE-GATE-A", "Synthetic Main Gate A"),
        (corrected[0], corrected[1], "corrected-duplicate", datetime(2026, 1, 14, 8, 11), "SYN-DEVICE-GATE-A", "Synthetic Main Gate A"),
        (SEED_END - timedelta(days=21), 7, "recent-001", datetime.combine(SEED_END - timedelta(days=21), time(8, 7)), "SYN-DEVICE-GATE-A", "Synthetic Main Gate A"),
        (SEED_END - timedelta(days=14), 8, "recent-002", datetime.combine(SEED_END - timedelta(days=14), time(12, 22)), "SYN-DEVICE-GATE-B", "Synthetic Main Gate B"),
        (SEED_END - timedelta(days=1), 9, "recent-003", datetime.combine(SEED_END - timedelta(days=1), time(16, 18)), "SYN-DEVICE-GATE-A", "Synthetic Main Gate A"),
    ], start=1):
        employee = EMPLOYEES[employee_index - 1]
        exceptions.append({
            "id": int(day.strftime("%Y%m%d")) * 100 + exception_id,
            "org_id": ORG_ID,
            "person_id": employee[1],
            "report_date": day,
            "clock_time": moment,
            "clock_photo_id": f"SYN-EXCEPTION-{label}",
            "device_key": device_key,
            "device_name": device_name,
            "del_status": ACTIVE,
            "gmt_modified": CREATED_AT,
            "gmt_create": CREATED_AT,
        })

    return {"persons": persons, "clocks": clocks, "daily": daily, "exceptions": exceptions}


def _sync_rows(connection, table, rows: list[dict]) -> dict[str, int]:
    """Converge stable synthetic rows without modifying non-synthetic records."""
    stats = {"created": 0, "updated": 0, "unchanged": 0, "skipped_non_synthetic": 0}
    if not rows:
        return stats
    ids = [row["id"] for row in rows]
    existing = {
        row["id"]: row
        for row in connection.execute(select(table).where(table.c.id.in_(ids))).mappings()
    }
    for desired in rows:
        current = existing.get(desired["id"])
        if current is None:
            connection.execute(insert(table), desired)
            stats["created"] += 1
        elif current["org_id"] != ORG_ID:
            stats["skipped_non_synthetic"] += 1
        elif any(current[column] != value for column, value in desired.items()):
            connection.execute(
                update(table)
                .where(table.c.id == desired["id"], table.c.org_id == ORG_ID)
                .values(**desired)
            )
            stats["updated"] += 1
        else:
            stats["unchanged"] += 1
    return stats


def seed() -> dict[str, dict[str, int]]:
    rows = build_seed_rows()
    engine = create_engine(target_admin_url())
    try:
        with engine.begin() as connection:
            # Remove only this synthetic dataset's records that belonged to an
            # older seed range. Never touch vendor or non-synthetic rows.
            end_of_seed_ms = _epoch_ms(datetime.combine(SEED_END + timedelta(days=1), time.min)) - 1
            connection.execute(delete(saas_ca_report_exception).where(
                saas_ca_report_exception.c.org_id == ORG_ID,
                saas_ca_report_exception.c.report_date > SEED_END,
            ))
            connection.execute(delete(saas_ca_report_daily).where(
                saas_ca_report_daily.c.org_id == ORG_ID,
                saas_ca_report_daily.c.report_date > SEED_END,
            ))
            connection.execute(delete(saas_ca_clock_record).where(
                saas_ca_clock_record.c.org_id == ORG_ID,
                saas_ca_clock_record.c.recognition_time > end_of_seed_ms,
            ))
            return {
                "saas_ca_person": _sync_rows(connection, saas_ca_person, rows["persons"]),
                "saas_ca_clock_record": _sync_rows(connection, saas_ca_clock_record, rows["clocks"]),
                "saas_ca_report_daily": _sync_rows(connection, saas_ca_report_daily, rows["daily"]),
                "saas_ca_report_exception": _sync_rows(connection, saas_ca_report_exception, rows["exceptions"]),
            }
    finally:
        engine.dispose()


def main() -> None:
    try:
        stats = seed()
    except LocalLunaSetupError as exc:
        raise SystemExit(f"Local Luna seed failed: {exc}") from None
    except Exception:
        raise SystemExit("Local Luna seed failed; run setup and check local configuration") from None
    print("Local Luna synthetic seed complete.")
    for table_name, table_stats in stats.items():
        rendered = ", ".join(f"{name}={count}" for name, count in table_stats.items())
        print(f"  {table_name}: {rendered}")


if __name__ == "__main__":
    main()
