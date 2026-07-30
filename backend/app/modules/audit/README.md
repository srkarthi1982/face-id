# Audit Module

## Purpose

Records audit logs for database changes — tracks who changed what and when for compliance and debugging.

## Key Files

- `models.py` — AuditLog model
- `schemas.py` — Pydantic schemas for audit queries
- `router.py` — Audit log query endpoints

## API Endpoints

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET | `/` | `list_audit_logs()` | List audit logs with filters |

## Audit Events Captured

Changes to these tables are logged automatically via SQLAlchemy event listeners:
- users
- roles
- permissions
- profiles
- devices
- personnel
- photos
- recognition_records
- callback_configs
- device_person_mapping

## Logged Data

| Field | Description |
|-------|-------------|
| table_name | Database table changed |
| row_id | Primary key of changed row |
| operation | INSERT / UPDATE / DELETE |
| user_id | User who made the change (nullable) |
| timestamp | When the change occurred |
| before_data | Data before change (JSON) |
| after_data | Data after change (JSON) |
| changed_fields | Which fields changed (JSON array) |

## End-to-End Flow

```
1. User makes a change:
   PUT /api/v1/users/{id} → Updates user record

2. Audit listener fires:
   - Captures before state
   - Applies change
   - Captures after state
   - Computes changed_fields
   - Inserts AuditLog record

3. Admin views audit log:
   GET /api/v1/audit-logs/?table_name=users&row_id=123
```

## Related Modules

All modules that modify data are audited.
