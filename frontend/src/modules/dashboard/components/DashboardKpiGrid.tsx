import type { DashboardOverview } from '../types'
import { useI18n } from '../../../infra/locales/I18nContext'
import { formatDuration, formatNumber } from '../utils'

export default function DashboardKpiGrid({ data }: { data: DashboardOverview }) {
  const { t, lang } = useI18n()
  const units = { day: t('nav.dashboard.units.day'), hour: t('nav.dashboard.units.hour'), minute: t('nav.dashboard.units.minute'), zero: t('nav.dashboard.units.zero') }
  const primaryCards = [
    ['employees', formatNumber(data.employee_count, lang)], ['actual', formatDuration(data.actual_seconds, lang, units)],
    ['overtime', formatDuration(data.overtime_seconds, lang, units)], ['exceptions', formatNumber(data.reported_exception_count, lang)],
  ] as const
  const secondaryCards = [
    ['scheduled', formatDuration(data.scheduled_seconds, lang, units)], ['normal', formatDuration(data.normal_seconds, lang, units)],
    ['late', formatDuration(data.late_seconds, lang, units)], ['early', formatDuration(data.early_seconds, lang, units)],
    ['absent', formatDuration(data.absent_seconds, lang, units)], ['reportDays', formatNumber(data.report_day_count, lang)],
  ] as const
  const card = ([key, value]: (typeof primaryCards)[number] | (typeof secondaryCards)[number], primary: boolean) => (
    <article key={key} data-testid={`kpi-${key}`} data-kpi-tier={primary ? 'primary' : 'secondary'} className={`min-w-0 rounded-xl border border-bd bg-surface p-4 shadow-sm ${primary ? 'border-s-4 border-s-accent' : ''}`}>
      <p className="text-xs font-medium text-muted">{t(`nav.dashboard.kpi.${key}`)}</p><p className="mt-2 break-words text-lg font-semibold text-primary" title={value}>{value}</p>
    </article>
  )
  return <div className="flex min-w-0 flex-col gap-3">
    <div data-testid="kpi-primary-grid" className="grid grid-cols-2 gap-3 lg:grid-cols-4">{primaryCards.map((item) => card(item, true))}</div>
    <div data-testid="kpi-secondary-grid" className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">{secondaryCards.map((item) => card(item, false))}</div>
  </div>
}
