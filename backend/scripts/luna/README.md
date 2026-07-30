# Local Luna PostgreSQL Simulation

These commands explicitly create, seed, and verify a local PostgreSQL simulation
of the external Luna attendance database. They are never imported or executed by
FastAPI startup and do not use Alembic.

Configure local, uncommitted values in `backend/.env`:

```dotenv
LUNA_ADMIN_DATABASE_URL=postgresql+psycopg2://ADMIN_USER:ADMIN_PASSWORD@localhost:5432/postgres
LUNA_DATABASE_URL=postgresql+psycopg2://LUNA_READONLY_USER:LUNA_READONLY_PASSWORD@localhost:5432/luna_db
LUNA_RUNTIME_DB_USER=LUNA_READONLY_USER
LUNA_RUNTIME_DB_PASSWORD=LUNA_READONLY_PASSWORD
```

Run from `backend/`:

```powershell
.\.venv\Scripts\python.exe .\scripts\luna\setup_local_luna_db.py
.\.venv\Scripts\python.exe .\scripts\luna\seed_local_luna_db.py
.\.venv\Scripts\python.exe .\scripts\luna\verify_local_luna_db.py
```

The simulation contains only four vendor tables in schema `dbo`. Seed data is
synthetic and deterministic, covers 2025-07-01 through 2026-07-29, and uses
seconds for all duration values. Provisional raw punch mapping is `clock_type=1`
for entry and `clock_type=2` for exit. Confirm both conventions with real Luna
data before production integration.

Seeding is a transactional synchronization limited to `org_id=SYNTHETIC-ORG`.
Stable primary keys are inserted when missing and updated only when their
synthetic values changed; unchanged rows are not rewritten, and colliding
non-synthetic rows are never modified. The command reports created, updated,
unchanged, and skipped-non-synthetic counts for each table. Work duration pairs
completed active entry/exit sessions, excludes breaks, and partitions every
daily total into normal plus overtime. Weekend work is overtime only.

When both runtime-role variables are supplied, setup creates the role only when
it does not already exist, applies no password or role-attribute change to an
existing role, and grants only the documented read privileges. When they are
absent, setup leaves roles untouched and reports that database-enforced
read-only access is not configured. Partial role configuration is rejected.
Existing runtime roles with any role membership are also rejected because
`SET ROLE` could otherwise provide privilege escalation.

The verification command uses `LUNA_DATABASE_URL`, fails closed unless the full
SELECT-only privilege contract is satisfied, and then reports safe Boolean
privilege results. It never prints credentials, URLs, hosts, or raw errors.

## Read-only runtime grants

The setup command can provision the runtime login from ignored environment
values. These are the equivalent grants for manual administration:

```sql
GRANT CONNECT ON DATABASE luna_db TO LUNA_READONLY_USER;
GRANT USAGE ON SCHEMA dbo TO LUNA_READONLY_USER;
GRANT SELECT ON dbo.saas_ca_person TO LUNA_READONLY_USER;
GRANT SELECT ON dbo.saas_ca_clock_record TO LUNA_READONLY_USER;
GRANT SELECT ON dbo.saas_ca_report_daily TO LUNA_READONLY_USER;
GRANT SELECT ON dbo.saas_ca_report_exception TO LUNA_READONLY_USER;
REVOKE CREATE ON SCHEMA public FROM LUNA_READONLY_USER;
REVOKE CREATE ON SCHEMA dbo FROM LUNA_READONLY_USER;
```

Do not grant INSERT, UPDATE, DELETE, TRUNCATE, CREATE, ALTER, or DROP. For SQL
Server production, grant the login SELECT only on the same approved tables or
views. `ApplicationIntent=ReadOnly` is an optional defense-in-depth hint, not a
substitute for database permissions.

The repository includes `psycopg2-binary`, so PostgreSQL URLs use
`postgresql+psycopg2://`. SQL Server support is optional:

```powershell
pip install -e ".[mssql]"
```

The host must also have a compatible Microsoft ODBC Driver for SQL Server.
Changing the URL alone is insufficient. Parsing an MSSQL URL does not prove that
the Python driver, host driver, credentials, network, or database are working.
No office SQL Server connection was attempted in this task.
