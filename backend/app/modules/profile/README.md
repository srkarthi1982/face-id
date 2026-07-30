# Profile Module

## Purpose

Manages user profile information including name, contact details, and personal data.

## Key Files

- `models.py` — Profile model
- `schemas.py` — Pydantic schemas for profile data
- `crud.py` — Database operations for profiles
- `router.py` — Profile endpoints

## API Endpoints

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET | `/{user_id}` | `get_profile()` | Get profile by user ID |
| PUT | `/` | `update_profile()` | Update current user's profile |
| DELETE | `/{profile_id}` | `delete_profile()` | Delete profile and user (admin) |

## End-to-End Flow

```
1. User views own profile:
   GET /api/v1/profile-info/{user_id} → Returns profile data

2. User updates profile:
   PUT /api/v1/profile-info/ → Updates first_name, middle_name, etc.

3. Admin deletes profile + user:
   DELETE /api/v1/profile-info/{profile_id} → Deletes profile + user record
```

## Related Modules

- `users` — User accounts linked to profiles
- `shared` — Country reference data used in profiles
