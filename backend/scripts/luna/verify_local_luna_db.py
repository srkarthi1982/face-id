#!/usr/bin/env python3
"""Verify the local Luna contract and runtime privileges with safe output."""

import os

from sqlalchemy import create_engine, func, inspect, select, text

try:
    from scripts.luna.common import LocalLunaSetupError, require_postgres_url
except ModuleNotFoundError:  # Direct script execution on Windows.
    from common import LocalLunaSetupError, require_postgres_url
from app.modules.dashboard.tables import APPROVED_LUNA_TABLES, luna_metadata


PROHIBITED_PREFIX = "dashboard"
SAFE_RUNTIME_PRIVILEGES = {
    "runtime_role_configured": True,
    "can_select": True,
    "can_insert": False,
    "can_update": False,
    "can_delete": False,
    "can_truncate": False,
    "can_create_table": False,
    "can_create_schema": False,
}


def validate_runtime_privileges(privileges: dict[str, bool]) -> None:
    """Fail closed unless every required runtime privilege is exactly safe."""
    if privileges != SAFE_RUNTIME_PRIVILEGES:
        raise LocalLunaSetupError(
            "Luna runtime role does not have the required SELECT-only privileges"
        )


def verify() -> tuple[dict[str, int], dict[str, bool]]:
    runtime_url = require_postgres_url("LUNA_DATABASE_URL")
    engine = create_engine(runtime_url)
    try:
        inspector = inspect(engine)
        if "dbo" not in set(inspector.get_schema_names()):
            raise LocalLunaSetupError("Schema dbo is missing")
        tables = set(inspector.get_table_names(schema="dbo"))
        if tables != APPROVED_LUNA_TABLES:
            raise LocalLunaSetupError("Luna dbo tables do not match the approved contract")
        if any(name.casefold().startswith(PROHIBITED_PREFIX) for name in tables):
            raise LocalLunaSetupError("A prohibited dashboard-owned table exists")
        with engine.connect() as connection:
            counts = {
                table.name: connection.execute(select(func.count()).select_from(table)).scalar_one()
                for table in luna_metadata.tables.values()
            }
            expected_role = os.getenv("LUNA_RUNTIME_DB_USER")
            runtime_role_configured = bool(expected_role) and bool(connection.execute(
                text("SELECT current_user = :expected_role"),
                {"expected_role": expected_role},
            ).scalar_one())
            privilege_row = connection.execute(text("""
                SELECT
                    bool_and(has_table_privilege(current_user, 'dbo.' || table_name, 'SELECT')) AS can_select,
                    bool_or(has_table_privilege(current_user, 'dbo.' || table_name, 'INSERT')) AS can_insert,
                    bool_or(has_table_privilege(current_user, 'dbo.' || table_name, 'UPDATE')) AS can_update,
                    bool_or(has_table_privilege(current_user, 'dbo.' || table_name, 'DELETE')) AS can_delete,
                    bool_or(has_table_privilege(current_user, 'dbo.' || table_name, 'TRUNCATE')) AS can_truncate,
                    has_schema_privilege(current_user, 'dbo', 'CREATE')
                      OR has_schema_privilege(current_user, 'public', 'CREATE') AS can_create_table,
                    has_database_privilege(current_user, current_database(), 'CREATE') AS can_create_schema
                FROM information_schema.tables
                WHERE table_schema = 'dbo'
            """)).mappings().one()
            privileges = {
                "runtime_role_configured": runtime_role_configured,
                "can_select": bool(privilege_row["can_select"]),
                "can_insert": bool(privilege_row["can_insert"]),
                "can_update": bool(privilege_row["can_update"]),
                "can_delete": bool(privilege_row["can_delete"]),
                "can_truncate": bool(privilege_row["can_truncate"]),
                "can_create_table": bool(privilege_row["can_create_table"]),
                "can_create_schema": bool(privilege_row["can_create_schema"]),
            }
            validate_runtime_privileges(privileges)
            return counts, privileges
    finally:
        engine.dispose()


def main() -> None:
    try:
        counts, privileges = verify()
    except LocalLunaSetupError as exc:
        raise SystemExit(f"Local Luna verification failed: {exc}") from None
    except Exception:
        raise SystemExit("Local Luna verification failed; check local configuration") from None
    print("Local Luna verification passed.")
    for table_name, count in sorted(counts.items()):
        print(f"  {table_name}: {count} rows")
    for name, value in privileges.items():
        print(f"{name}: {str(value).lower()}")


if __name__ == "__main__":
    main()
