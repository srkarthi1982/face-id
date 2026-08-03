import enum
from typing import cast


class PermissionCode(str, enum.Enum):
    """Granular permission codes used across the application."""

    # Users
    USER_READ = "user:read"
    USER_WRITE = "user:write"

    # Audit logs
    AUDIT_READ = "audit:read"

    # Usage analytics
    ANALYTICS_READ = "analytics:read"

    # RBAC management
    ROLE_MANAGE = "role:manage"

    # Admin blanket
    ADMIN_FULL = "admin:full"

    # Devices
    DEVICE_READ = "device:read"
    DEVICE_WRITE = "device:write"

    # Personnel
    PERSONNEL_READ = "personnel:read"
    PERSONNEL_WRITE = "personnel:write"

    # Recognition records
    RECORD_READ = "record:read"
    RECORD_WRITE = "record:write"

    # Master data
    LOCATION_READ = "location:read"
    LOCATION_WRITE = "location:write"
    UNIT_READ = "unit:read"
    UNIT_WRITE = "unit:write"
    DEPARTMENT_READ = "department:read"
    DEPARTMENT_WRITE = "department:write"
    TIMING_READ = "timing:read"
    TIMING_WRITE = "timing:write"

class _PermissionMeta:
    __slots__ = ("code", "name", "description", "module")

    def __init__(self, code: PermissionCode, name: str, description: str, module: str):
        self.code = code
        self.name = name
        self.description = description
        self.module = module


PERMISSION_REGISTRY: list[_PermissionMeta] = [
    _PermissionMeta(PermissionCode.USER_READ, "Read Users", "View user accounts", "users"),
    _PermissionMeta(PermissionCode.USER_WRITE, "Write Users", "Create, update, deactivate user accounts", "users"),    
    _PermissionMeta(PermissionCode.ADMIN_FULL, "Full Admin", "Unrestricted system access", "admin"),
    _PermissionMeta(PermissionCode.ANALYTICS_READ, "Read Usage Analytics", "View system usage analytics and statistics", "analytics"),
    _PermissionMeta(PermissionCode.ROLE_MANAGE, "Manage Roles", "Create and assign roles and permissions", "rbac"),
    _PermissionMeta(PermissionCode.DEVICE_READ, "Read Devices", "View device list, status, settings, and records", "device"),
    _PermissionMeta(PermissionCode.DEVICE_WRITE, "Write Devices", "Add, update, remove devices and manage settings", "device"),
    _PermissionMeta(PermissionCode.PERSONNEL_READ, "Read Personnel", "View personnel list and details", "personnel"),
    _PermissionMeta(PermissionCode.PERSONNEL_WRITE, "Write Personnel", "Add, update, delete personnel and sync to devices", "personnel"),
    _PermissionMeta(PermissionCode.RECORD_READ, "Read Records", "View recognition records", "recognition"),
    _PermissionMeta(PermissionCode.RECORD_WRITE, "Write Records", "Delete recognition records", "recognition"),
    _PermissionMeta(PermissionCode.LOCATION_READ, "Read Locations", "View location hierarchy", "master-data"),
    _PermissionMeta(PermissionCode.LOCATION_WRITE, "Write Locations", "Create, update, delete locations", "master-data"),
    _PermissionMeta(PermissionCode.UNIT_READ, "Read Units", "View unit hierarchy", "master-data"),
    _PermissionMeta(PermissionCode.UNIT_WRITE, "Write Units", "Create, update, delete units", "master-data"),
    _PermissionMeta(PermissionCode.DEPARTMENT_READ, "Read Departments", "View department hierarchy", "master-data"),
    _PermissionMeta(PermissionCode.DEPARTMENT_WRITE, "Write Departments", "Create, update, delete departments", "master-data"),
    _PermissionMeta(PermissionCode.TIMING_READ, "Read Timings", "View department timing rules", "master-data"),
    _PermissionMeta(PermissionCode.TIMING_WRITE, "Write Timings", "Create, update, delete department timing rules", "master-data"),
]

DEFAULT_ROLE_PERMISSIONS: dict[str, list[PermissionCode]] = {
    "admin": list(PermissionCode),  # all permissions
}


def get_permission_codes() -> list[str]:
    return [cast(str, p.code.value) for p in PERMISSION_REGISTRY]


def get_default_role_permissions(role_name: str) -> list[PermissionCode]:
    return list(DEFAULT_ROLE_PERMISSIONS.get(role_name.lower(), []))


def sync_permissions_to_db(db) -> None:
    """Upsert registered permissions into the database.

    Only adds missing permissions; never deletes or overwrites existing ones.
    Resets the PostgreSQL sequence first to avoid ID collisions with
    manually-assigned IDs (34-40) from migration f6dc191f9a13.
    """
    import sqlalchemy as sa
    from app.modules.users.models import Permission

    max_id = db.execute(sa.text("SELECT COALESCE(MAX(id), 0) FROM permissions")).scalar_one()
    db.execute(sa.text(f"SELECT setval('permissions_id_seq', GREATEST({max_id} + 1, 1), false)"))
    db.commit()

    existing = {p.code for p in db.query(Permission.code).all()}
    missing = []
    for meta in PERMISSION_REGISTRY:
        code = str(meta.code.value)
        if code not in existing:
            missing.append(
                Permission(
                    code=code,
                    name=meta.name,
                    description=meta.description,
                    module=meta.module,
                )
            )
    if missing:
        db.add_all(missing)
        db.commit()
