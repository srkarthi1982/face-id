# Settings / Access Management Feature

## Purpose

Role-based access control management — manages roles, permissions, and user role assignments.

## Key Files

- `AccessManagementRoutes.tsx` — Route wrapper for sub-pages
- `manifest.ts` — Feature manifest

## Store

None — uses sub-components for each category.

## Pages

| Page | Path | Description |
|------|------|-------------|
| AccessManagementRoutes | `/settings/access-management/*` | Route wrapper |

## Sub-Pages (via AccessManagementRoutes)

| Sub-Page | Path | Description |
|----------|------|-------------|
| Roles | `/settings/access-management/roles` | Role CRUD |
| Permissions | `/settings/access-management/permissions` | Permission viewer |
| Access Control | `/settings/access-management/access-control` | User-role assignments |

## Features

- Role management (create, update, delete)
- Permission assignment to roles
- User-role assignment management
- Role hierarchy display

## End-to-End Flow

```
1. Admin views roles:
   → GET /api/v1/access/roles → Lists roles

2. Admin creates role:
   → POST /api/v1/access/roles → Creates role

3. Admin assigns permissions:
   → PUT /api/v1/access/roles/{id}/permissions → Updates role permissions

4. Admin assigns role to user:
   → PUT /api/v1/access/users/{user_id}/roles → Updates user roles

5. All changes audited:
   → AuditLog created for each change
```

## Permissions Required

`admin:*` — access to all admin functions

## Related Features

- Parent module: `settings`
- `settings/users-management` — User management
- `audit` — Changes logged
