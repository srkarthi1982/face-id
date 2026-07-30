import type { DashboardOverview } from '../types'
import { useI18n } from '../../../infra/locales/I18nContext'
import { formatDuration, formatNumber } from '../utils'

export default function DashboardKpiGrid({ data }: { data: DashboardOverview }) {
  const { t, lang } = useI18n()
  const units = { day: t('nav.dashboard.units.day'), hour: t('nav.dashboard.units.hour'), minute: t('nav.dashboard.units.minute'), zero: t('nav.dashboard.units.zero') }
  const cards = [
    ['employees', formatNumber(data.employee_count, lang)], ['actual', formatDuration(data.actual_seconds, lang, units)],
    ['overtime', formatDuration(data.overtime_seconds, lang, units)], ['exceptions', formatNumber(data.reported_exception_count, lang)],
    ['scheduled', formatDuration(data.scheduled_seconds, lang, units)], ['normal', formatDuration(data.normal_seconds, lang, units)],
    ['late', formatDuration(data.late_seconds, lang, units)], ['early', formatDuration(data.early_seconds, lang, units)],
    ['absent', formatDuration(data.absent_seconds, lang, units)], ['reportDays', formatNumber(data.report_day_count, lang)],
  ] as const
  return <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 xl:grid-cols-5">{cards.map(([key, value], index) => (
    <article key={key} data-testid={`kpi-${key}`} className={`min-w-0 rounded-xl border border-bd bg-surface p-4 shadow-sm ${index < 4 ? 'border-s-4 border-s-accent' : ''}`}>
      <p className="text-xs font-medium text-muted">{t(`nav.dashboard.kpi.${key}`)}</p><p className="mt-2 break-words text-lg font-semibold text-primary" title={value}>{value}</p>
    </article>
  ))}</div>
}
