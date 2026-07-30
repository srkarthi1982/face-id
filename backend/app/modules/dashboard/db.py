"""Lazy, narrow read boundary for the external Luna database."""

from __future__ import annotations

import importlib.util
from collections.abc import Sequence
from threading import Lock
from typing import Any

from sqlalchemy import Table, create_engine, select
from sqlalchemy.sql import Select
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.modules.dashboard.tables import luna_metadata


class LunaConfigurationError(RuntimeError):
    """Safe error for absent, unsupported, or unavailable configuration."""


class LunaUnavailableError(RuntimeError):
    """Safe application-level error for Luna connection/query failures."""


_engine: Engine | None = None
_engine_lock = Lock()

_DRIVER_MODULES = {
    "postgresql": "psycopg2",
    "postgresql+psycopg2": "psycopg2",
    "mssql+pyodbc": "pyodbc",
}


def _configured_url() -> URL:
    if not settings.LUNA_DATABASE_URL:
        raise LunaConfigurationError("Luna data source is not configured")
    try:
        url = make_url(settings.LUNA_DATABASE_URL)
    except Exception as exc:
        raise LunaConfigurationError("Luna data source configuration is invalid") from exc
    if url.drivername not in _DRIVER_MODULES:
        raise LunaConfigurationError("Luna database dialect or driver is unsupported")
    return url


def get_luna_dialect_name() -> str:
    """Return only the configured dialect name; this does not test connectivity."""
    return _configured_url().get_backend_name()


def get_luna_driver_status() -> dict[str, str | bool]:
    """Report safe driver capability metadata without opening a connection."""
    url = _configured_url()
    module_name = _DRIVER_MODULES[url.drivername]
    return {
        "dialect": url.get_backend_name(),
        "driver_available": importlib.util.find_spec(module_name) is not None,
        "connectivity_tested": False,
    }


def _get_luna_engine() -> Engine:
    """Create the independent Luna engine on first use, never at import time."""
    global _engine
    if _engine is not None:
        return _engine
    url = _configured_url()
    module_name = _DRIVER_MODULES[url.drivername]
    if importlib.util.find_spec(module_name) is None:
        raise LunaConfigurationError("Required Luna Python database driver is unavailable")
    with _engine_lock:
        if _engine is None:
            try:
                _engine = create_engine(url, pool_pre_ping=True)
            except (ImportError, ModuleNotFoundError, SQLAlchemyError) as exc:
                raise LunaConfigurationError(
                    "Required Luna Python database driver is unavailable"
                ) from exc
    return _engine


def fetch_luna_table_rows(table: Table, *, limit: int = 100) -> Sequence[dict[str, Any]]:
    """Read rows from one explicitly declared Luna table.

    Callers cannot submit SQL text, DML, DDL, arbitrary SQLAlchemy statements,
    or client-provided query structures. Database permissions remain the
    authoritative write-prevention boundary.
    """
    if (
        not isinstance(table, Table)
        or table.metadata is not luna_metadata
        or table.fullname not in luna_metadata.tables
    ):
        raise TypeError("Only approved Luna tables can be read")
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
        raise ValueError("Luna row limit must be between 1 and 1000")
    statement = select(table).limit(limit)
    try:
        with _get_luna_engine().connect() as connection:
            return [dict(row) for row in connection.execute(statement).mappings().all()]
    except (SQLAlchemyError, OSError) as exc:
        raise LunaUnavailableError("Luna data source is unavailable") from exc


def dispose_luna_engine() -> None:
    """Dispose the lazy engine for tests or controlled process shutdown."""
    global _engine
    with _engine_lock:
        if _engine is not None:
            _engine.dispose()
            _engine = None


def _execute_luna_select(statement: Select[Any]) -> Sequence[dict[str, Any]]:
    """Execute an internally built dashboard SELECT with sanitized failures."""
    if not isinstance(statement, Select):
        raise TypeError("Dashboard Luna executor accepts SELECT statements only")
    try:
        with _get_luna_engine().connect() as connection:
            return [dict(row) for row in connection.execute(statement).mappings().all()]
    except (SQLAlchemyError, OSError) as exc:
        raise LunaUnavailableError("Luna data source is unavailable") from exc
