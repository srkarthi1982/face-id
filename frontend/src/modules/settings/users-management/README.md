# Settings / Users Management Feature

## Purpose

User administration — CRUD operations for user accounts, role assignment, and Esnaad integration.

## Key Files

- `manifest.ts` — Feature manifest
- `pages/UsersPage.tsx` — User management page
- `pages/store.ts` — Zustand store for users

## Store

`useAdminStore` — manages user list, fetching, and mutations.

## Pages

| Page | Path | Description |
|------|------|-------------|
| UsersPage | `/settings/users` | User management |

## Features

- User list with sorting and search
- Pagination
- Create new user modal
- Edit user modal
- Role badges display
- Add user from Esnaad integration
- Navigate to user profile

## End-to-End Flow

```
1. Admin views user list:
   → GET /api/v1/users/ → Lists users with pagination

2. Admin creates user:
   → POST /api/v1/users/ → Creates user + profile

3. Admin edits user:
   → PUT /api/v1/users/{id} → Updates user data

4. Admin assigns roles:
   → PUT /api/v1/access/users/{id}/roles → Updates user roles

5. Admin deactivates user:
   → PATCH /api/v1/users/{id}/deactivate → Sets is_active=false

6. Admin adds from Esnaad:
   → Calls Esnaad API to fetch user data
   → Creates local user record
```

## Permissions Required

`admin:full` — full administrative access

## Related Features

- Parent module: `settings`
- `settings/access-management` — Role management
- `profile` — User profiles
