# Auth Module

## Purpose

Handles user authentication including login, logout, registration, token refresh, and retrieving current user information.

## Key Files

- `models.py` — (none, endpoints only)
- `schemas.py` — Pydantic schemas for auth payloads and responses
- `router.py` — Authentication endpoints

## API Endpoints

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| POST | `/register` | `register()` | Register new user with email/password |
| POST | `/login` | `login()` | Authenticate user, returns JWT tokens |
| POST | `/refresh` | `refresh_token_endpoint()` | Refresh access token |
| POST | `/logout` | `logout()` | Clear refresh token cookie |
| GET | `/me` | `get_me()` | Get current authenticated user |
| GET | `/me/permissions` | `get_my_permissions()` | Get current user's permissions |

## End-to-End Flow

```
1. User registers:
   POST /api/v1/auth/register → Creates user + profile

2. User logs in:
   POST /api/v1/auth/login → Validates credentials → Returns access_token + refresh_token

3. Subsequent requests:
   Authorization: Bearer <access_token>

4. Token refresh:
   POST /api/v1/auth/refresh → Validates refresh_token → Returns new access_token

5. Logout:
   POST /api/v1/auth/logout → Clears refresh cookie
```

## Related Modules

- `users` — User accounts created by auth
- `profile` — User profiles linked to auth users
- `access` — Permissions checked after authentication
