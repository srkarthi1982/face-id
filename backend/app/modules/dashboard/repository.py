"""PostgreSQL attendance read model for dashboard analytics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import Date, and_, case, cast, extract, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.modules.device.models import Device
from app.modules.master.models import Department, Timing, Weekday
from app.modules.personnel.models import Personnel
from app.modules.recognition_records.models import RecognitionRecord
from .constants import LATEST_ATTENDANCE_DATE_SCAN_LIMIT, LATEST_ATTENDANCE_LOOKBACK_DAYS


BUSINESS_TZ = ZoneInfo("Asia/Dubai")
_WEEKDAY_ORDER = [
    Weekday.MONDAY,
    Weekday.TUESDAY,
    Weekday.WEDNESDAY,
    Weekday.THURSDAY,
    Weekday.FRIDAY,
    Weekday.SATURDAY,
    Weekday.SUNDAY,
]
_WEEKDAY_INDEX = {day.value: index for index, day in enumerate(_WEEKDAY_ORDER)}


@dataclass(frozen=True)
class EmployeeDay:
    report_date: date
    personnel_id: int
    department_id: int
    department_name: str
    employee_key: str
    person_id: str | None
    person_no: str | None
    person_name: str | None
    scheduled_seconds: int
    actual_seconds: int
    normal_seconds: int
    overtime_seconds: int
    late_seconds: int
    early_seconds: int
    absent_seconds: int
    check_in: datetime | None
    check_out: datetime | None
    event_count: int
    first_device_id: int | None
    last_device_id: int | None


def weekday_values(start_day: Weekday | str, end_day: Weekday | str) -> set[int]:
    start = _WEEKDAY_INDEX[start_day.value if isinstance(start_day, Weekday) else start_day]
    end = _WEEKDAY_INDEX[end_day.value if isinstance(end_day, Weekday) else end_day]
    if start <= end:
        return set(range(start, end + 1))
    return set(range(start, 7)) | set(range(0, end + 1))


def local_day_bounds_utc(start_date: date, end_date: date) -> tuple[datetime, datetime]:
    start = datetime.combine(start_date, time.min, BUSINESS_TZ).astimezone(timezone.utc)
    exclusive_end = datetime.combine(end_date + timedelta(days=1), time.min, BUSINESS_TZ).astimezone(timezone.utc)
    return start, exclusive_end


def _to_dubai(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(BUSINESS_TZ)


def get_departments(db: Session) -> list[dict]:
    rows = db.query(Department).filter(Department.is_active.is_(True)).order_by(Department.name, Department.id).all()
    return [{"department_id": row.id, "department_name": row.name} for row in rows]


def get_latest_report_date(db: Session, department_id: int | None = None) -> date | None:
    base_query = (
        db.query(func.max(RecognitionRecord.event_time))
        .join(Personnel, Personnel.person_id_internal == RecognitionRecord.person_id_internal)
        .join(Department, Department.id == Personnel.department_id)
        .join(Timing, and_(Timing.department_id == Department.id, Timing.is_active.is_(True)))
        .filter(
            Personnel.is_active.is_(True),
            Department.is_active.is_(True),
            RecognitionRecord.event_type == "success",
            RecognitionRecord.person_id_internal.isnot(None),
            RecognitionRecord.event_time.isnot(None),
        )
    )
    if department_id is not None:
        base_query = base_query.filter(Department.id == department_id)
    newest_event_time = base_query.scalar()
    if newest_event_time is None:
        return None

    newest_local_date = _to_dubai(newest_event_time).date()
    lower_bound, _ = local_day_bounds_utc(
        newest_local_date - timedelta(days=LATEST_ATTENDANCE_LOOKBACK_DAYS - 1),
        newest_local_date,
    )

    if db.bind and db.bind.dialect.name == "postgresql":
        local_time = func.timezone("Asia/Dubai", RecognitionRecord.event_time)
        local_date = cast(local_time, Date)
        iso_weekday = extract("isodow", local_time)
        start_iso = case(
            (Timing.start_day == Weekday.MONDAY, 1),
            (Timing.start_day == Weekday.TUESDAY, 2),
            (Timing.start_day == Weekday.WEDNESDAY, 3),
            (Timing.start_day == Weekday.THURSDAY, 4),
            (Timing.start_day == Weekday.FRIDAY, 5),
            (Timing.start_day == Weekday.SATURDAY, 6),
            else_=7,
        )
        end_iso = case(
            (Timing.end_day == Weekday.MONDAY, 1),
            (Timing.end_day == Weekday.TUESDAY, 2),
            (Timing.end_day == Weekday.WEDNESDAY, 3),
            (Timing.end_day == Weekday.THURSDAY, 4),
            (Timing.end_day == Weekday.FRIDAY, 5),
            (Timing.end_day == Weekday.SATURDAY, 6),
            else_=7,
        )
        query = (
            db.query(func.max(local_date))
            .join(Personnel, Personnel.person_id_internal == RecognitionRecord.person_id_internal)
            .join(Department, Department.id == Personnel.department_id)
            .join(Timing, and_(Timing.department_id == Department.id, Timing.is_active.is_(True)))
            .filter(
                Personnel.is_active.is_(True),
                Department.is_active.is_(True),
                RecognitionRecord.event_type == "success",
                RecognitionRecord.person_id_internal.isnot(None),
                RecognitionRecord.event_time.isnot(None),
                RecognitionRecord.event_time >= lower_bound,
                or_(
                    and_(start_iso <= end_iso, iso_weekday >= start_iso, iso_weekday <= end_iso),
                    and_(start_iso > end_iso, or_(iso_weekday >= start_iso, iso_weekday <= end_iso)),
                ),
            )
        )
        if department_id is not None:
            query = query.filter(Department.id == department_id)
        return query.scalar()

    query = (
        db.query(RecognitionRecord.event_time, Timing.start_day, Timing.end_day)
        .join(Personnel, Personnel.person_id_internal == RecognitionRecord.person_id_internal)
        .join(Department, Department.id == Personnel.department_id)
        .join(Timing, and_(Timing.department_id == Department.id, Timing.is_active.is_(True)))
        .filter(
            Personnel.is_active.is_(True),
            Department.is_active.is_(True),
            RecognitionRecord.event_type == "success",
            RecognitionRecord.person_id_internal.isnot(None),
            RecognitionRecord.event_time.isnot(None),
            RecognitionRecord.event_time >= lower_bound,
        )
    )
    if department_id is not None:
        query = query.filter(Department.id == department_id)
    for event_time, start_day, end_day in query.order_by(RecognitionRecord.event_time.desc(), RecognitionRecord.id.desc()).limit(LATEST_ATTENDANCE_DATE_SCAN_LIMIT):
        local_date = _to_dubai(event_time).date()
        if local_date.weekday() in weekday_values(start_day, end_day):
            return local_date
    return None


def build_employee_days(db: Session, start_date: date, end_date: date, department_id: int | None = None) -> list[EmployeeDay]:
    timing_query = (
        db.query(Timing)
        .options(joinedload(Timing.department))
        .join(Department)
        .filter(Timing.is_active.is_(True), Department.is_active.is_(True))
    )
    if department_id is not None:
        timing_query = timing_query.filter(Timing.department_id == department_id)
    timings = timing_query.all()
    timing_by_department = {timing.department_id: timing for timing in timings}
    if not timing_by_department:
        return []

    personnel = (
        db.query(Personnel)
        .options(joinedload(Personnel.department))
        .filter(
            Personnel.is_active.is_(True),
            Personnel.department_id.in_(timing_by_department.keys()),
        )
        .order_by(Personnel.emp_no, Personnel.id)
        .all()
    )
    if not personnel:
        return []

    event_start_utc, event_end_utc = local_day_bounds_utc(start_date, end_date)
    person_keys = [person.person_id_internal for person in personnel if person.person_id_internal]
    events = []
    if person_keys:
        events = (
            db.query(RecognitionRecord)
            .filter(
                RecognitionRecord.event_type == "success",
                RecognitionRecord.person_id_internal.in_(person_keys),
                RecognitionRecord.event_time.isnot(None),
                RecognitionRecord.event_time >= event_start_utc,
                RecognitionRecord.event_time < event_end_utc,
            )
            .order_by(RecognitionRecord.person_id_internal, RecognitionRecord.event_time, RecognitionRecord.id)
            .all()
        )

    events_by_person_day: dict[tuple[str, date], list[RecognitionRecord]] = {}
    for event in events:
        local_time = _to_dubai(event.event_time)
        key = (event.person_id_internal or "", local_time.date())
        events_by_person_day.setdefault(key, []).append(event)

    days: list[EmployeeDay] = []
    current = start_date
    while current <= end_date:
        weekday = current.weekday()
        for person in personnel:
            timing = timing_by_department.get(person.department_id)
            if timing is None or weekday not in weekday_values(timing.start_day, timing.end_day):
                continue
            scheduled_seconds = int(
                (
                    datetime.combine(current, timing.end_time, BUSINESS_TZ)
                    - datetime.combine(current, timing.start_time, BUSINESS_TZ)
                ).total_seconds()
            )
            person_events = events_by_person_day.get((person.person_id_internal or "", current), [])
            first = person_events[0] if person_events else None
            last = person_events[-1] if person_events else None
            check_in = _to_dubai(first.event_time) if first else None
            check_out = _to_dubai(last.event_time) if last else None
            if len(person_events) == 0:
                actual = normal = overtime = late = early = 0
                absent = scheduled_seconds
            elif len(person_events) == 1:
                actual = normal = overtime = late = early = absent = 0
            else:
                actual = max(int((check_out - check_in).total_seconds()), 0)
                normal = min(actual, scheduled_seconds)
                overtime = max(actual - scheduled_seconds, 0)
                configured_start = datetime.combine(current, timing.start_time, BUSINESS_TZ)
                configured_end = datetime.combine(current, timing.end_time, BUSINESS_TZ)
                late = max(int((check_in - configured_start).total_seconds()), 0)
                early = max(int((configured_end - check_out).total_seconds()), 0)
                absent = 0

            days.append(EmployeeDay(
                report_date=current,
                personnel_id=person.id,
                department_id=person.department_id,
                department_name=person.department.name if person.department else "",
                employee_key=f"personnel:{person.id}",
                person_id=person.person_id_internal,
                person_no=person.emp_no,
                person_name=person.full_name,
                scheduled_seconds=scheduled_seconds,
                actual_seconds=actual,
                normal_seconds=normal,
                overtime_seconds=overtime,
                late_seconds=late,
                early_seconds=early,
                absent_seconds=absent,
                check_in=check_in,
                check_out=check_out,
                event_count=len(person_events),
                first_device_id=first.device_id if first else None,
                last_device_id=last.device_id if last else None,
            ))
        current += timedelta(days=1)
    return days


def get_device_names(db: Session, device_ids: set[int]) -> dict[int, tuple[str, str]]:
    if not device_ids:
        return {}
    rows = db.execute(select(Device.id, Device.device_id, Device.device_name).where(Device.id.in_(device_ids))).all()
    return {row.id: (row.device_id, row.device_name) for row in rows}
