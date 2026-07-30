# Dashboard Module

## Purpose

Main dashboard view — landing page after login showing system overview and quick actions.

## Key Files

- `DashboardPage.tsx` — Main dashboard page component
- `manifest.ts` — Module manifest

## Store

None — uses global contexts only.

## Pages

| Page | Path | Description |
|------|------|-------------|
| DashboardPage | `/dashboard` | Main dashboard view |

## End-to-End Flow

```
1. User navigates to /dashboard:
   → DashboardPage renders

2. Page displays:
   → Overview widgets (placeholder)
```

## Related Modules

- All modules are accessible from sidebar
