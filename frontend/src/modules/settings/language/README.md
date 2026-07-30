# Settings / Language Feature

## Purpose

Internationalization — language selection between English and Arabic with RTL support.

## Key Files

- `LanguagePage.tsx` — Language settings page
- `manifest.ts` — Feature manifest

## Store

`useI18n` — from `infra/locales` for language state.

## Pages

| Page | Path | Description |
|------|------|-------------|
| LanguagePage | `/settings/language` | Language settings |

## Features

- Language selection with flag icons
- English and Arabic options
- Active state indicator
- RTL support for Arabic
- Language persists in localStorage

## End-to-End Flow

```
1. User views language settings:
   → useI18n provides current language

2. User selects language:
   → useI18n.setLanguage() → Updates language context
   → Sets dir="rtl" for Arabic, dir="ltr" for English
   → UI strings reload from appropriate JSON file

3. Language persists:
   → Saved to localStorage
   → Restored on page load
```

## Related Features

- Parent module: `settings`
- Translations: `en.json`, `ar.json`
