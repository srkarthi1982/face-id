import type { LanguageCode } from '../../infra/locales/I18nContext'

export const localeFor = (lang: LanguageCode) => lang === 'ar' ? 'ar-AE' : 'en-US'

export function formatNumber(value: number | null | undefined, lang: LanguageCode): string {
  return new Intl.NumberFormat(localeFor(lang)).format(Math.max(0, value ?? 0))
}

export function formatDuration(value: number | null | undefined, lang: LanguageCode, units: { day: string; hour: string; minute: string; zero: string }): string {
  const seconds = Math.max(0, Math.trunc(value ?? 0))
  if (seconds === 0) return units.zero
  const days = Math.floor(seconds / 86400); const hours = Math.floor((seconds % 86400) / 3600); const minutes = Math.floor((seconds % 3600) / 60)
  const number = new Intl.NumberFormat(localeFor(lang))
  return [days ? `${number.format(days)} ${units.day}` : '', hours ? `${number.format(hours)} ${units.hour}` : '', minutes ? `${number.format(minutes)} ${units.minute}` : ''].filter(Boolean).join(' ') || units.zero
}

export function formatDate(value: string | null | undefined, lang: LanguageCode): string {
  if (!value) return '—'
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value)
  if (!match) return '—'
  const [, year, month, day] = match
  return new Intl.DateTimeFormat(localeFor(lang), { dateStyle: 'medium', timeZone: 'UTC' }).format(new Date(Date.UTC(Number(year), Number(month) - 1, Number(day))))
}

export function formatWallClockTime(value: string | null | undefined, lang: LanguageCode): string {
  if (!value) return '—'
  const match = /(?:T|\s)?(\d{2}):(\d{2})(?::\d{2})?/.exec(value)
  if (!match) return '—'
  const [, hour, minute] = match
  return new Intl.DateTimeFormat(localeFor(lang), { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' }).format(new Date(Date.UTC(2000, 0, 1, Number(hour), Number(minute))))
}
