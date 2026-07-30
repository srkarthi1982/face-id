# Settings / Account Feature

## Purpose

User account settings — displays user info, provides quick links, and manages Personal Access Tokens (PATs).

## Key Files

- `AccountPage.tsx` — Account settings page
- `manifest.ts` — Feature manifest

## Store

`useAuthStore` — from `infra/auth` for user data and authentication state.

## Pages

| Page | Path | Description |
|------|------|-------------|
| AccountPage | `/settings/account` | Account settings |

## Features

- User profile card (avatar, name, email)
- Quick links to profile, access management, appearance, language
- Personal Access Tokens section (when `VITE_ENABLE_PAT=true`)
- Logout button

## End-to-End Flow

```
1. User views account page:
   → useAuthStore provides user data
   → Displays profile card

2. User manages PATs:
   → GET /api/v1/pats/ → Lists user's tokens
   → POST /api/v1/pats/ → Creates new token
   → DELETE /api/v1/pats/{id} → Revokes token

3. User logs out:
   → useAuthStore.logout() → POST /api/v1/auth/logout
   → Redirects to /login
```

## Related Features

- Parent module: `settings`
- `profile-general-info` — Linked profile page
- `settings/access-management` — Linked for permissions
