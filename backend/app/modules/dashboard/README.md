# Dashboard PostgreSQL Attendance Source

The dashboard reads attendance analytics from the primary PostgreSQL database.
It uses active departments, active personnel, active department timings, and
successful recognition events.

Attendance calendar grouping uses `Asia/Dubai`. Queries fetch recognition events
with a bounded UTC range that corresponds to the requested Dubai-local date
range. Calculations use `recognition_records.event_time`; `created_at` is only
ingestion metadata.

V1 analytics endpoints cap requested ranges at 366 days. Default latest-date
resolution first finds the newest successful recognition event and then scans a
bounded 366-day event-time window while applying configured Timing working-day
semantics, so non-working-day recognitions do not move the default dashboard
scope to an empty working-day calculation.

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
