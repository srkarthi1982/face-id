# PAT Module

## Purpose

Personal Access Tokens — allows users to create API tokens for programmatic access (MCP clients).

## Key Files

- `models.py` — PersonalAccessToken model
- `schemas.py` — Pydantic schemas for PAT operations
- `services.py` — Token generation and validation logic
- `router.py` — PAT management endpoints

## API Endpoints

| Method | Path | Function | Purpose |
|--------|------|----------|---------|
| POST | `/` | `create_token()` | Create PAT (returns plaintext once) |
| GET | `/` | `list_tokens()` | List user's tokens |
| DELETE | `/{token_id}` | `revoke_token()` | Revoke a token |

## End-to-End Flow

```
1. User creates PAT:
   POST /api/v1/pats/ → Creates token, returns plaintext (one-time display)

2. User uses PAT for API:
   Authorization: Bearer <PAT>
   - deps.get_current_user() validates PAT and loads user

3. User revokes PAT:
   DELETE /api/v1/pats/{id} → Sets revoked_at timestamp

4. PAT auto-expires:
   - Tokens with expires_at in past are rejected
   - Revoked tokens are rejected
```

## Security Notes

- Token hash stored in DB (not plaintext)
- Only prefix (first 16 chars) shown in list
- Tokens can have expiration dates

## Related Modules

- `auth` — Uses same JWT token validation logic
