#!/usr/bin/env python3
"""Seed default roles and role permissions for local development / first-run setup.

Creates a fixed set of system roles with their permissions assigned.
Safe to run repeatedly: existing roles are skipped, and existing
role_permissions are replaced idempotently so the script never duplicates data.

Run from anywhere with the backend's virtualenv interpreter, e.g.:

    backend/.venv/Scripts/python.exe backend/scripts/seed_default_roles.py  # Windows
    backend/.venv/bin/python backend/scripts/seed_default_roles.py          # Unix
"""

import logging
import os
import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))
os.chdir(_BACKEND_DIR)

_VENV_DIR = _BACKEND_DIR / ".venv"


def _ensure_backend_venv() -> None:
    if not _VENV_DIR.exists():
        return

    if Path(sys.prefix).resolve() == _VENV_DIR.resolve():
        return

    activate = (
        _VENV_DIR / "Scripts" / "Activate.ps1"
        if os.name == "nt"
        else f"source {_VENV_DIR / 'bin' / 'activate'}"
    )
    venv_python = _VENV_DIR / ("Scripts" if os.name == "nt" else "bin") / "python"
    sys.exit(
        "Virtual environment is not active.\n"
        f"Activate the backend virtualenv first, then re-run:\n"
        f"    {activate}\n"
        "Or run it directly with the venv interpreter:\n"
        f"    {venv_python} {Path(__file__).name}"
    )


_ensure_backend_venv()

from app.core.database import SessionLocal
from app.modules import import_all_models
from app.modules.users.models import Permission, Role
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# (role_name, role_description, [permission_codes])
DEFAULT_ROLES: list[tuple[str, str, list[str]]] = [
    (
        "Admin",
        "Admin Role",
        [
            "admin:full",
            "role:manage"
        ],
    ),
]


def seed_roles(db: Session) -> None:
    # Pre-load all existing permissions into a lookup dict.
    permissions_by_code = {p.code: p for p in db.query(Permission).all()}

    created_roles = 0
    skipped_roles = 0
    assigned_perms = 0
    skipped_perms = 0
    missing_perms: dict[str, list[str]] = {}

    # Handle existing 'admin' role: assign all permissions if it exists.
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if admin_role:
        logger.info("Found existing admin role: %s", admin_role.name)
        for perm in permissions_by_code.values():
            if perm not in admin_role.permissions:
                admin_role.permissions.append(perm)
                assigned_perms += 1
                logger.info("Assigned all permissions to admin role: %s", perm.code)
        db.commit()
        logger.info("Admin role updated with all %d permissions", len(permissions_by_code))
    else:
        logger.info("Admin role does not exist, skipping admin update")

    for role_name, role_desc, perm_codes in DEFAULT_ROLES:
        # Check if role already exists.
        existing_role = db.query(Role).filter(Role.name == role_name).first()
        if existing_role:
            logger.info("Role already exists, skipping: %s", role_name)
            skipped_roles += 1

            # Even for existing roles, make sure all permissions are assigned.
            existing_codes = {rp.code for rp in existing_role.permissions}
            for code in perm_codes:
                perm = permissions_by_code.get(code)
                if perm is None:
                    missing_perms.setdefault(role_name, []).append(code)
                    continue
                if perm not in existing_role.permissions:
                    existing_role.permissions.append(perm)
                    assigned_perms += 1
                    logger.info("Assigned permission to existing role: %s -> %s", role_name, code)
            continue

        # Verify all permissions exist before creating the role.
        role_perms = []
        missing: list[str] = []
        for code in perm_codes:
            perm = permissions_by_code.get(code)
            if perm is None:
                missing.append(code)
            else:
                role_perms.append(perm)

        if missing:
            logger.warning(
                "Role '%s' has missing permissions (%s); skipping role creation. "
                "Run permission seed first or create the missing permissions.",
                role_name,
                ", ".join(missing),
            )
            missing_perms[role_name] = missing
            continue

        role = Role(name=role_name, description=role_desc, is_system=True)
        role.permissions = role_perms
        db.add(role)
        created_roles += 1
        assigned_perms += len(role_perms)
        logger.info("Created role: %s (permissions=%d)", role_name, len(role_perms))

    db.commit()

    if missing_perms:
        logger.warning("Missing permissions (not assigned): %s", missing_perms)

    logger.info(
        "Seed complete: %d roles created, %d roles skipped, %d permissions assigned, %d permissions skipped",
        created_roles,
        skipped_roles,
        assigned_perms,
        skipped_perms,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    import_all_models()
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
