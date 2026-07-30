# Shared Module

## Purpose

Provides reference data shared across the application — currently country list for profile addresses.

## Key Files

- `models.py` — Country model
- `schemas.py` — Pydantic schemas for countries
- `router.py` — Reference data endpoints

## API Endpoints

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| GET | `/country` | `list_countries()` | List all countries |

## End-to-End Flow

```
1. User edits profile:
   - GET /api/v1/shared/country → Fetches country list for dropdown
   - User selects country
   - PUT /api/v1/profile-info/ → Updates profile with country_id
```

## Related Modules

- `profile` — Uses country reference data
