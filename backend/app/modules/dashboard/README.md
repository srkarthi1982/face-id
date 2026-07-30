# Dashboard Luna Data Source

The dashboard reads attendance data from Luna, an external and read-only data
source. Local development simulates Luna in PostgreSQL database `luna_db` under
schema `dbo`; production will use the office Microsoft SQL Server database.
`LUNA_DATABASE_URL` selects either SQLAlchemy dialect without changing dashboard
business code.

The primary Face ID engine, sessions, metadata, transactions, and Alembic chain
must remain completely separate from Luna. Alembic and runtime schema creation
are prohibited for Luna. Only the explicit local setup command under
`backend/scripts/luna` may create the local PostgreSQL simulation.

Application-level restriction and database-level enforcement are distinct:

- The application exposes only a narrow function that builds `SELECT` queries
  against the four declared tables. It does not accept arbitrary SQLAlchemy
  statements or textual SQL. This reduces accidental writes but is not a proof
  of database immutability.
- The configured database login must have database-enforced SELECT-only
  privileges. Database permissions are the authoritative write-prevention
  control. An administrator URL is never suitable for runtime deployment.

For SQL Server, `ApplicationIntent=ReadOnly` is an optional connection hint, not
a replacement for database permissions.

Local PostgreSQL uses the installed `psycopg2-binary` driver and a
`postgresql+psycopg2://` URL. SQL Server requires the optional `mssql` dependency
and a compatible Microsoft ODBC Driver for SQL Server on the host. Changing
`LUNA_DATABASE_URL` alone is not sufficient on a fresh host. URL parsing proves
neither driver availability nor connectivity. Production SQL Server connectivity
remains unverified until tested in an approved environment.

Future dashboard endpoints must require the exact `analytics:read` permission.
They must never authorize against an `Admin` role name. Administrators and future
normal-user roles can both access the dashboard when that permission is assigned.

Future reporting sources:

- `saas_ca_report_daily`: official working-hour totals.
- `saas_ca_clock_record`: raw entry/exit detail.
- `saas_ca_report_exception`: missing or exceptional attendance detail.
- `saas_ca_person`: Luna person reference data.

Local simulation duration fields are stored in seconds. Seed values provisionally
map `clock_type=1` to entry and `clock_type=2` to exit. Both assumptions require
validation against real Luna values before production integration.

## Read-only analytics APIs

All routes are under `/api/v1/dashboard` and require exactly
`analytics:read` through the standard permission dependency:

- `GET /overview` returns source status, effective dates, row/day/employee
  counts, reported-exception count, and official duration totals.
- `GET /work-hours/trend` returns day, ISO-week, calendar-month, or
  calendar-year duration buckets.
- `GET /work-hours/ranking` ranks employees by official actual seconds.
- `GET /attendance-exceptions` returns stable, paginated, generic reported
  exceptions with optional Luna person enrichment.

Official duration metrics come only from `dbo.saas_ca_report_daily` and remain
integer seconds. Reported exception counts and records come only from
`dbo.saas_ca_report_exception`. `dbo.saas_ca_person` is used only for
deterministic exception enrichment; when duplicates exist, the lowest active
person-row ID is selected. The runtime analytics API does not query
`dbo.saas_ca_clock_record`.

When dates are omitted, the effective end date is the latest active daily
report date for the optional organization, and the start is 29 calendar days
earlier (a 30-day inclusive window). A reachable source without daily reports
returns explicit empty HTTP 200 responses and never substitutes the current
server date. Maximum inclusive ranges are 3,660 days for overview, ranking,
exceptions, month trend, and year trend; 1,096 days for week trend; and 366
days for day trend.

ISO weeks begin Monday and end Sunday. Trend period boundaries are clipped to
the effective request range. Week/month/year bucketing occurs in Python so the
business queries remain portable between PostgreSQL and Microsoft SQL Server.

Every query assumes vendor `del_status=0` means active. That semantic remains
production validation work. Exception output deliberately says only
"attendance exception" or "reported exception" because no confirmed reason
field exists. Missing-entry, missing-exit, and unmatched entry/exit diagnostics
are not implemented. Raw-clock pairing, `clock_type` interpretation, punch
timezone handling, and raw-clock-derived work calculations are not implemented.

The APIs and read-only privileges are validated against the local PostgreSQL
simulation. Statements are compilation-tested for the MSSQL dialect, but real
production SQL Server connectivity remains untested pending an approved
environment and confirmation of vendor field semantics.
