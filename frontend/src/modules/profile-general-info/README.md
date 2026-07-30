# Profile General Info Module

## Purpose

User profile information page — displays and edits current user's profile data. Serves as the root `/` route.

## Key Files

- `UserProfileInfoPage.tsx` — Main profile page component
- `store.ts` — Zustand store for profile data
- `manifest.ts` — Module manifest

## Store

`useProfileInfoStore` — manages profile data fetching and updates.

## Pages

| Page | Path | Description |
|------|------|-------------|
| UserProfileInfoPage | `/profile-general-info`, also at `/` | User profile display and edit |

## End-to-End Flow

```
1. User views profile at /:
   → useProfileInfoStore.fetch() → GET /api/v1/profile-info/{user_id}
   → Displays profile card with avatar, name, contact info

2. User clicks edit:
   → Opens edit modal
   → PUT /api/v1/profile-info/ → Updates profile

3. User changes password:
   → Opens change password modal
   → PUT /api/v1/users/{id}/passwd

4. Avatar:
   → Shows initials in colored circle if no photo
```

## Related Modules

- `settings/account` — Linked from profile page
- `users` — User data linked to profile
