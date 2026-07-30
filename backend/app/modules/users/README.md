# Users Module

## Purpose

Manages user accounts including CRUD operations, activation/deactivation, and password management.

## Key Files

- `models.py` — User, Role, Permission, AuthProvider models
- `schemas.py` — Pydantic schemas for user payloads and responses
- `crud.py` — Database operations for users
- `router.py` — User management endpoints

## API Endpoints

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET | `/` | `list_users()` | List users with filters and pagination |
| GET | `/{user_id}` | `get_user()` | Get user by ID |
| POST | `/` | `create_user()` | Create new user with roles |
| PUT | `/{user_id}` | `update_user()` | Update user fields |
| PATCH | `/{user_id}/deactivate` | `deactivate_user()` | Deactivate user account |
| PATCH | `/{user_id}/activate` | `activate_user()` | Activate user account |
| DELETE | `/{user_id}` | `delete_user()` | Delete user |
| PUT | `/{user_id}/passwd` | `change_password()` | Change password |

## End-to-End Flow

```
1. Admin creates user:
   POST /api/v1/users/ → Creates user + assigns roles

2. User updates profile via profile module:
   PUT /api/v1/profile-info/ → Updates profile fields

3. Admin deactivates user:
   PATCH /api/v1/users/{id}/deactivate → Sets is_active=false

4. Password change:
   PUT /api/v1/users/{id}/passwd → Updates hashed_password
```

## Related Modules

- `auth` — Authentication handled separately
- `profile` — Profiles linked to users
- `access` — Roles and permissions assigned to users
- `audit` — User changes logged
