# Access Module

## Purpose

Role-based access control (RBAC) — manages roles, permissions, and user role assignments.

## Key Files

- `models.py` — (none, endpoints only; models in users module)
- `schemas.py` — Pydantic schemas for roles and permissions
- `service.py` — Database operations for roles
- `router.py` — RBAC endpoints

## API Endpoints

**Permissions:**
| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET | `/permissions` | `list_permissions()` | List all permissions |
| GET | `/permissions/{permission_id}` | `get_permission()` | Get permission by ID |
| GET | `/permission-codes` | `list_permission_codes()` | List all codes (public) |

**Roles:**
| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET | `/roles` | `list_roles()` | List all roles |
| GET | `/roles/{role_id}` | `get_role()` | Get role by ID |
| POST | `/roles` | `create_role()` | Create new role |
| PUT | `/roles/{role_id}` | `update_role()` | Update role |
| DELETE | `/roles/{role_id}` | `delete_role()` | Delete role |
| PUT | `/roles/{role_id}/permissions` | `update_role_permissions()` | Update role permissions |
| GET | `/roles/{role_id}/users` | `list_role_users()` | List users with role |

**User Roles:**
| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| PUT | `/users/{user_id}/roles` | `update_user_roles()` | Assign roles to user |

## End-to-End Flow

```
1. Admin creates role:
   POST /api/v1/access/roles → Creates role with no permissions

2. Admin assigns permissions to role:
   PUT /api/v1/access/roles/{id}/permissions → Sets permission codes

3. Admin assigns role to user:
   PUT /api/v1/access/users/{user_id}/roles → Adds role to user

4. User makes request:
   - deps.get_current_user() loads user with roles/permissions
   - require_permission() decorator checks permissions
```

## Related Modules

- `users` — User model with roles
- `auth` — Permissions checked during authentication
