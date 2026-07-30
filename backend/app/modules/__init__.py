from importlib import import_module

from fastapi import APIRouter

# Ordered list of domain modules. Order matters: models are imported in this
# order, so modules that define foreign-key targets must appear before modules
# that reference them.
MODULE_NAMES = [
    "users",         # User, Role, Permission, AuthProvider — no FKs
    "auth",          # endpoints only; imports user.models
    "access",        # endpoints only; imports user.models
    "shared",        # Country — standalone reference data (used by profile)
    "profile",       # Profile → User
    "pat",           # Personal access tokens (MCP clients) → User
    "master",        # Location & Unit master data (must be before device)
    "device",        # Device management endpoints (references master)
    "personnel",     # Employee management endpoints
    "photos",        # Photo registrations
    "person_mapping",# Device-person mapping
    "recognition_records", # Recognition records
    "callbacks",     # Callback configurations
    "audit",         # AuditLog → User — must be last
]

# Modules that expose SQLAlchemy models via a `models` submodule. The auth and
# access modules have no DB models of their own, so they're omitted from
# metadata import.
_MODEL_MODULES = [name for name in MODULE_NAMES if name not in ("auth", "access")]


def create_api_router() -> APIRouter:
    """Import all modules and aggregate their routers."""
    api_router = APIRouter()
    for name in MODULE_NAMES:
        mod = import_module(f"app.modules.{name}")
        api_router.include_router(mod.router)
    return api_router


def import_all_models():
    """Ensure every module's models are registered with Base.metadata.

    Called by Alembic env.py and at app startup so that SQLAlchemy can
    resolve all string-based relationship references.
    """
    for name in _MODEL_MODULES:
        import_module(f"app.modules.{name}.models")
