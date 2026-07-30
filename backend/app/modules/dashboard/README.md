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
