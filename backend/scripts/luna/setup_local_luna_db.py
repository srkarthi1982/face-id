#!/usr/bin/env python3
"""Idempotently create only the approved local PostgreSQL Luna simulation."""

from sqlalchemy import create_engine, inspect, text
from psycopg2 import sql

try:
    from scripts.luna.common import (
        LUNA_DATABASE_NAME,
        LocalLunaSetupError,
        require_postgres_url,
        runtime_role_config,
        target_admin_url,
    )
except ModuleNotFoundError:  # Direct script execution on Windows.
    from common import (
        LUNA_DATABASE_NAME,
        LocalLunaSetupError,
        require_postgres_url,
        runtime_role_config,
        target_admin_url,
    )


def _validate_existing_runtime_role(existing, has_membership: bool) -> None:
    if (
        not existing["rolcanlogin"]
        or existing["rolsuper"]
        or existing["rolcreatedb"]
        or existing["rolcreaterole"]
        or existing["rolreplication"]
        or existing["rolinherit"]
    ):
        raise LocalLunaSetupError(
            "Existing Luna runtime role has unsafe attributes and was not altered"
        )
    if has_membership:
        raise LocalLunaSetupError(
            "Existing Luna runtime role has role memberships and was not altered"
        )


def _create_runtime_role_if_requested(connection, role_config: tuple[str, str] | None) -> bool:
    if role_config is None:
        return False
    username, password = role_config
    existing = connection.execute(
        text(
            "SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, "
            "rolreplication, rolinherit "
            "FROM pg_roles WHERE rolname = :role"
        ),
        {"role": username},
    ).mappings().one_or_none()
    if existing is None:
        dbapi_connection = connection.connection.driver_connection
        with dbapi_connection.cursor() as cursor:
            cursor.execute(
                sql.SQL(
                    "CREATE ROLE {} WITH LOGIN PASSWORD %s "
                    "NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOINHERIT"
                ).format(sql.Identifier(username)),
                (password,),
            )
    membership = connection.execute(
        text(
            "SELECT 1 FROM pg_auth_members membership "
            "JOIN pg_roles member ON member.oid = membership.member "
            "WHERE member.rolname = :role LIMIT 1"
        ),
        {"role": username},
    ).scalar_one_or_none()
    if existing is not None:
        _validate_existing_runtime_role(existing, membership is not None)
    return True


def _grant_runtime_read_access(connection, username: str) -> None:
    quoted_role = connection.dialect.identifier_preparer.quote(username)
    # Remove broadly inherited object-creation paths within this local database.
    connection.execute(text("REVOKE CREATE, TEMPORARY ON DATABASE luna_db FROM PUBLIC"))
    connection.execute(text("REVOKE CREATE ON SCHEMA public FROM PUBLIC"))
    connection.execute(text(f"REVOKE ALL PRIVILEGES ON DATABASE luna_db FROM {quoted_role}"))
    connection.execute(text(f"GRANT CONNECT ON DATABASE luna_db TO {quoted_role}"))
    connection.execute(text(f"REVOKE ALL PRIVILEGES ON SCHEMA dbo FROM {quoted_role}"))
    connection.execute(text(f"GRANT USAGE ON SCHEMA dbo TO {quoted_role}"))
    connection.execute(text(f"REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA dbo FROM {quoted_role}"))
    connection.execute(text(
        "GRANT SELECT ON dbo.saas_ca_person, dbo.saas_ca_clock_record, "
        "dbo.saas_ca_report_daily, dbo.saas_ca_report_exception "
        f"TO {quoted_role}"
    ))
    connection.execute(text(f"REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA dbo FROM {quoted_role}"))


def setup() -> bool:
    admin_url = require_postgres_url("LUNA_ADMIN_DATABASE_URL")
    role_config = runtime_role_config()
    maintenance_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with maintenance_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :database"),
                {"database": LUNA_DATABASE_NAME},
            ).scalar_one_or_none()
            if exists is None:
                # The database name is a fixed application constant, never user input.
                connection.execute(text(f'CREATE DATABASE "{LUNA_DATABASE_NAME}"'))
            role_configured = _create_runtime_role_if_requested(connection, role_config)
    finally:
        maintenance_engine.dispose()

    from app.modules.dashboard.tables import APPROVED_LUNA_TABLES, luna_metadata

    target_engine = create_engine(target_admin_url())
    try:
        with target_engine.begin() as connection:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS dbo"))
            luna_metadata.create_all(connection, checkfirst=True)
            if role_config is not None:
                _grant_runtime_read_access(connection, role_config[0])
        actual = set(inspect(target_engine).get_table_names(schema="dbo"))
        unexpected = actual - APPROVED_LUNA_TABLES
        if unexpected:
            raise LocalLunaSetupError("Unexpected tables already exist in Luna schema dbo")
    finally:
        target_engine.dispose()
    return role_configured


def main() -> None:
    try:
        role_configured = setup()
    except LocalLunaSetupError as exc:
        raise SystemExit(f"Local Luna setup failed: {exc}") from None
    except Exception:
        raise SystemExit("Local Luna setup failed; check local PostgreSQL configuration") from None
    print("Local Luna PostgreSQL schema is ready.")
    print(f"runtime_role_configured: {str(role_configured).lower()}")
    if not role_configured:
        print("warning: database-enforced read-only runtime access is not configured")


if __name__ == "__main__":
    main()
