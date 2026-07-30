# Settings / Appearance Feature

## Purpose

Theme customization — light/dark mode toggle with visual preview.

## Key Files

- `AppearancePage.tsx` — Theme settings page
- `manifest.ts` — Feature manifest

## Store

`useTheme` — from `infra/theme` for theme state management.

## Pages

| Page | Path | Description |
|------|------|-------------|
| AppearancePage | `/settings/appearance` | Theme settings |

## Features

- Light/dark mode toggle
- Visual preview cards for each theme
- Instant theme switching
- Theme persists in localStorage

## End-to-End Flow

```
1. User views appearance settings:
   → useTheme provides current theme

2. User toggles theme:
   → useTheme.toggleTheme() → Updates theme context
   → Sets data-theme attribute on <html>
   → CSS variables change automatically

3. Theme persists:
   → Saved to localStorage
   → Restored on page load
```

## Related Features

- Parent module: `settings`
