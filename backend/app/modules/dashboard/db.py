"""Lazy, narrow read boundary for the external Luna database."""

from __future__ import annotations

import importlib.util
import re
from collections.abc import Sequence
from threading import Lock
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings


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
_FORBIDDEN_SQL = re.compile(
    r"\b(?:INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|CREATE|TRUNCATE|EXEC|EXECUTE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


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


def dispose_luna_engine() -> None:
    """Dispose the lazy engine for tests or controlled process shutdown."""
    global _engine
    with _engine_lock:
        if _engine is not None:
            _engine.dispose()
            _engine = None


def execute_luna_select(sql: str, parameters: dict[str, Any] | None = None) -> Sequence[dict[str, Any]]:
    """Execute one internal, parameterized, read-only dashboard SQL statement."""
    if (
        not isinstance(sql, str)
        or not sql.lstrip().upper().startswith(("SELECT", "WITH"))
        or _FORBIDDEN_SQL.search(sql)
    ):
        raise TypeError("Dashboard Luna executor accepts read-only SQL only")
    try:
        with _get_luna_engine().connect() as connection:
            return [
                dict(row)
                for row in connection.execute(text(sql), parameters or {}).mappings().all()
            ]
    except (SQLAlchemyError, OSError) as exc:
        raise LunaUnavailableError("Luna data source is unavailable") from exc
