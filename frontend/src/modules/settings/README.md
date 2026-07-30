# Settings Module

## Purpose

Application settings hub — contains account, access management, users, appearance, language, and audit log features.

## Key Files

- `manifest.ts` — Module manifest (container only)

## Store

None — container module.

## Pages

Container module — renders submenu via `SubmenuAside` with features:
- `/settings/account` — Account settings
- `/settings/access-management/*` — RBAC management
- `/settings/users` — User management
- `/settings/appearance` — Theme settings
- `/settings/language` — Language settings
- `/settings/audit-log` — Audit logs

## Features (Submenu Items)

| Feature | Order | Path |
|---------|-------|------|
| account | 5 | /settings/account |
| access-management | 10 | /settings/access-management/* |
| users-management | 20 | /settings/users |
| appearance | 25 | /settings/appearance |
| language | 30 | /settings/language |
| audit-log | 30 | /settings/audit-log |

## End-to-End Flow

```
1. User navigates to /settings:
   → Container renders SubmenuAside
   → Shows submenu with feature options
   → Renders selected feature's page
```

## Related Features

- `settings/account` — Account page
- `settings/access-management` — RBAC pages
- `settings/users-management` — User CRUD
- `settings/appearance` — Theme toggle
- `settings/language` — i18n switch
- `settings/audit-log` — Audit viewer
