"""Shared helpers for explicit local Luna PostgreSQL commands."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL, make_url


BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(BACKEND_DIR / ".env")

LUNA_DATABASE_NAME = "luna_db"
_ROLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,62}$")


class LocalLunaSetupError(RuntimeError):
    pass


def require_postgres_url(variable: str) -> URL:
    raw_url = os.getenv(variable)
    if not raw_url:
        raise LocalLunaSetupError(f"{variable} is required")
    try:
        url = make_url(raw_url)
    except Exception as exc:
        raise LocalLunaSetupError(f"{variable} is not a valid SQLAlchemy URL") from exc
    if url.get_backend_name() != "postgresql":
        raise LocalLunaSetupError(f"{variable} must use PostgreSQL for local Luna tooling")
    return url


def target_admin_url() -> URL:
    return require_postgres_url("LUNA_ADMIN_DATABASE_URL").set(database=LUNA_DATABASE_NAME)


def runtime_role_config() -> tuple[str, str] | None:
    username = os.getenv("LUNA_RUNTIME_DB_USER")
    password = os.getenv("LUNA_RUNTIME_DB_PASSWORD")
    if not username and not password:
        return None
    if not username or not password:
        raise LocalLunaSetupError(
            "LUNA_RUNTIME_DB_USER and LUNA_RUNTIME_DB_PASSWORD must both be supplied"
        )
    if not _ROLE_NAME_PATTERN.fullmatch(username):
        raise LocalLunaSetupError("LUNA_RUNTIME_DB_USER is not a safe PostgreSQL role name")
    return username, password
