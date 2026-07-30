# Settings / Audit Log Feature

## Purpose

Audit trail viewer — displays system changes logged via the audit module.

## Key Files

- `AuditLogPage.tsx` — Audit log viewer page
- `manifest.ts` — Feature manifest

## Store

None — uses generated API directly.

## Pages

| Page | Path | Description |
|------|------|-------------|
| AuditLogPage | `/settings/audit-log` | Audit log viewer |

## Features

- Audit log table with pagination
- Filtering by table name and operation type
- Sortable columns
- Detail modal showing before/after data
- Operation badges (INSERT=green, UPDATE=blue, DELETE=red)

## End-to-End Flow

```
1. Admin views audit logs:
   → listAuditLogsApiV1AuditLogsGet → GET /api/v1/audit-logs/
   → Displays paginated list

2. Admin filters logs:
   → Query params: table_name, operation, user_id, etc.
   → listAuditLogsApiV1AuditLogsGet({ query: { table_name: 'users' } })

3. Admin views change details:
   → Opens detail modal
   → Shows before_data, after_data, changed_fields

4. All changes come from audit module:
   → SQLAlchemy event listeners capture all changes
   → No manual API calls needed
```

## Permissions Required

`audit:read` — view audit logs

## Related Modules

- `audit` (backend) — generates audit logs
