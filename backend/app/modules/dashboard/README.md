# Dashboard PostgreSQL Attendance Source

The dashboard reads attendance analytics from the primary PostgreSQL database.
It uses active departments, active personnel, active department timings, and
successful recognition events.

Attendance calendar grouping uses `Asia/Dubai`. Queries fetch recognition events
with a bounded UTC range that corresponds to the requested Dubai-local date
range. Calculations use `recognition_records.event_time`; `created_at` is only
ingestion metadata.

V1 limitations:

- No overnight shifts.
- No multiple shifts.
- No grace period.
- No breaks.
- No holiday calendar.
- No effective-dated Timing history.
- Changing a Timing can recalculate historical dashboard output.
- Personnel in departments without an active Timing are excluded from scheduled
  attendance rather than assuming default hours.
