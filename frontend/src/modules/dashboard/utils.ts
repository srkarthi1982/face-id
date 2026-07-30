import type { LanguageCode } from '../../infra/locales/I18nContext'

export const localeFor = (lang: LanguageCode) => lang === 'ar' ? 'ar-AE' : 'en-US'

export function formatNumber(value: number | null | undefined, lang: LanguageCode): string {
  return new Intl.NumberFormat(localeFor(lang)).format(Math.max(0, value ?? 0))
}

export function formatDuration(
  value: number | null | undefined,
  lang: LanguageCode,
  units: { day: string; hour: string; minute: string; zero: string },
): string {
  const seconds = Math.max(0, Math.trunc(value ?? 0))
  if (seconds === 0) return units.zero
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const number = new Intl.NumberFormat(localeFor(lang))
  return [
    days ? `${number.format(days)} ${units.day}` : '',
    hours ? `${number.format(hours)} ${units.hour}` : '',
    minutes ? `${number.format(minutes)} ${units.minute}` : '',
  ].filter(Boolean).join(' ') || units.zero
}

export function formatDate(value: string | null | undefined, lang: LanguageCode): string {
  if (!value) return '—'
  return new Intl.DateTimeFormat(localeFor(lang), { dateStyle: 'medium', timeZone: 'UTC' })
    .format(new Date(`${value}T00:00:00Z`))
}

export function formatDateTime(value: string | null | undefined, lang: LanguageCode, part: 'date' | 'time') {
  if (!value) return '—'
  const date = new Date(value)
  return new Intl.DateTimeFormat(localeFor(lang), part === 'date'
    ? { dateStyle: 'medium' }
    : { hour: '2-digit', minute: '2-digit' }).format(date)
}
