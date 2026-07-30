from __future__ import annotations

import importlib
import importlib.util
import inspect as python_inspect
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine, delete, func, insert, select, text, update
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.schema import CreateTable

from app.core.config import Settings, settings
from app.core.database import Base
from app.modules.dashboard import db as luna_db
from app.modules.dashboard.tables import (
    APPROVED_LUNA_TABLES,
    luna_metadata,
    saas_ca_clock_record,
    saas_ca_person,
    saas_ca_report_daily,
    saas_ca_report_exception,
)
from scripts.luna.common import LocalLunaSetupError, require_postgres_url, runtime_role_config
from scripts.luna.seed_local_luna_db import SEED_END, _insert_missing, build_seed_rows


def test_luna_metadata_is_isolated_and_exact() -> None:
    assert luna_metadata is not Base.metadata
    assert set(luna_metadata.tables) == {
        f"dbo.{name}" for name in APPROVED_LUNA_TABLES
    }
    assert set(Base.metadata.tables).isdisjoint(luna_metadata.tables)


def test_all_luna_tables_use_dbo_schema_and_match_63_vendor_columns() -> None:
    assert {table.schema for table in luna_metadata.tables.values()} == {"dbo"}
    assert sum(len(table.columns) for table in luna_metadata.tables.values()) == 63


def test_runtime_module_has_no_schema_creation_or_write_api() -> None:
    source = python_inspect.getsource(luna_db)
    assert "create_all" not in source
    assert ".commit(" not in source
    assert ".add(" not in source
    assert ".delete(" not in source
    assert "fetch_luna_mappings" not in source


@pytest.mark.parametrize(
    ("url", "dialect"),
    [
        ("postgresql+psycopg2://reader:secret@localhost:5432/luna_db", "postgresql"),
        (
            "mssql+pyodbc://reader:secret@luna-host/luna?driver=ODBC+Driver+18+for+SQL+Server",
            "mssql",
        ),
    ],
)
def test_url_parsing_is_separate_from_connectivity(
    monkeypatch: pytest.MonkeyPatch, url: str, dialect: str
) -> None:
    configured = Settings(
        DATABASE_URL="sqlite://",
        LUNA_DATABASE_URL=url,
        SECRET_KEY="x" * 32,
        DEBUG=False,
    )
    assert configured.LUNA_DATABASE_URL == url
    assert make_url(url).get_backend_name() == dialect
    monkeypatch.setattr(settings, "LUNA_DATABASE_URL", url)
    assert luna_db.get_luna_dialect_name() == dialect
    status = luna_db.get_luna_driver_status()
    assert status["dialect"] == dialect
    assert status["connectivity_tested"] is False


def test_psycopg3_is_not_advertised_as_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        settings,
        "LUNA_DATABASE_URL",
        "postgresql+psycopg://reader:secret@localhost:5432/luna_db",
    )
    with pytest.raises(luna_db.LunaConfigurationError, match="unsupported"):
        luna_db.get_luna_dialect_name()


def test_unavailable_mssql_driver_is_a_sanitized_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "LUNA_DATABASE_URL",
        "mssql+pyodbc://secret-user:secret-password@private-host/luna",
    )
    real_find_spec = importlib.util.find_spec
    monkeypatch.setattr(
        importlib.util,
        "find_spec",
        lambda name: None if name == "pyodbc" else real_find_spec(name),
    )
    with pytest.raises(luna_db.LunaConfigurationError) as captured:
        luna_db._get_luna_engine()
    assert str(captured.value) == "Required Luna Python database driver is unavailable"
    assert "secret" not in str(captured.value)
    assert "private-host" not in str(captured.value)


def test_local_setup_and_optional_role_support_reject_mssql(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "LUNA_ADMIN_DATABASE_URL",
        "mssql+pyodbc://reader:secret@host/luna?driver=ODBC+Driver+18+for+SQL+Server",
    )
    monkeypatch.setenv("LUNA_RUNTIME_DB_USER", "luna_reader")
    monkeypatch.setenv("LUNA_RUNTIME_DB_PASSWORD", "not-printed")
    assert runtime_role_config() == ("luna_reader", "not-printed")
    with pytest.raises(LocalLunaSetupError, match="must use PostgreSQL"):
        require_postgres_url("LUNA_ADMIN_DATABASE_URL")


def test_partial_runtime_role_configuration_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LUNA_RUNTIME_DB_USER", "luna_reader")
    monkeypatch.delenv("LUNA_RUNTIME_DB_PASSWORD", raising=False)
    with pytest.raises(LocalLunaSetupError, match="must both be supplied"):
        runtime_role_config()


def test_seed_rows_are_stable_and_have_unique_primary_keys() -> None:
    first = build_seed_rows()
    second = build_seed_rows()
    assert first == second
    assert len(first["persons"]) >= 12
    for rows in first.values():
        ids = [row["id"] for row in rows]
        assert len(ids) == len(set(ids))


def test_seed_contains_no_attendance_after_documented_end_date() -> None:
    rows = build_seed_rows()
    assert max(row["report_date"] for row in rows["daily"]) <= SEED_END
    assert max(row["report_date"] for row in rows["exceptions"]) <= SEED_END
    end_of_seed_ms = int(
        datetime.combine(
            SEED_END + timedelta(days=1), time.min, tzinfo=timezone.utc
        ).timestamp()
        * 1000
    ) - 1
    assert max(row["recognition_time"] for row in rows["clocks"]) <= end_of_seed_ms


def test_seed_insert_is_idempotent() -> None:
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS dbo")
        saas_ca_person.create(connection)
        rows = build_seed_rows()["persons"]
        assert _insert_missing(connection, saas_ca_person, rows) == 12
        assert _insert_missing(connection, saas_ca_person, rows) == 0
        assert connection.execute(
            select(func.count()).select_from(saas_ca_person)
        ).scalar_one() == 12
    engine.dispose()


def test_representative_select_through_narrow_runtime_helper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS dbo")
        saas_ca_person.create(connection)
        connection.execute(insert(saas_ca_person), build_seed_rows()["persons"][:1])
    monkeypatch.setattr(luna_db, "_engine", engine)
    try:
        rows = luna_db.fetch_luna_table_rows(saas_ca_person, limit=1)
        assert rows[0]["person_no"] == "SYN-0001"
    finally:
        luna_db.dispose_luna_engine()


@pytest.mark.parametrize(
    "statement",
    [
        text("SELECT 1"),
        insert(saas_ca_person),
        update(saas_ca_person),
        delete(saas_ca_person),
        CreateTable(saas_ca_person),
    ],
)
def test_runtime_helper_rejects_text_dml_and_ddl(statement) -> None:
    with pytest.raises(TypeError, match="approved Luna tables"):
        luna_db.fetch_luna_table_rows(statement)  # type: ignore[arg-type]


def test_connection_error_is_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    class BrokenEngine:
        def connect(self):
            raise SQLAlchemyError(
                "could not connect to postgresql://secret-user:secret-password@private-host/luna_db"
            )

    monkeypatch.setattr(luna_db, "_get_luna_engine", lambda: BrokenEngine())
    with pytest.raises(luna_db.LunaUnavailableError) as captured:
        luna_db.fetch_luna_table_rows(saas_ca_person)
    assert str(captured.value) == "Luna data source is unavailable"
    assert "secret" not in str(captured.value)
    assert "private-host" not in str(captured.value)


def test_documentation_distinguishes_application_and_database_controls() -> None:
    readme = Path("app/modules/dashboard/README.md").read_text(encoding="utf-8")
    assert "Application-level restriction" in readme
    assert "database login must have database-enforced SELECT-only" in readme
    assert "administrator URL is never suitable for runtime" in readme
    assert "URL parsing" in readme
    assert "neither driver availability nor connectivity" in readme


def test_dashboard_import_is_lazy_and_connection_free() -> None:
    luna_db.dispose_luna_engine()
    module = importlib.reload(luna_db)
    assert module._engine is None


def test_all_four_table_symbols_remain_declared() -> None:
    assert {
        saas_ca_person.name,
        saas_ca_clock_record.name,
        saas_ca_report_daily.name,
        saas_ca_report_exception.name,
    } == APPROVED_LUNA_TABLES
