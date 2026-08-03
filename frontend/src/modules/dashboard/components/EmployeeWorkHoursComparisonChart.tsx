import { useEffect, useMemo, useRef, useState } from 'react'
import * as d3 from 'd3'
import { useI18n } from '../../../infra/locales/I18nContext'
import { useDashboardStore } from '../store'
import type { DashboardFilters, EmployeeWorkHoursRanking } from '../types'
import { formatDuration, formatNumber } from '../utils'

type Item = EmployeeWorkHoursRanking['items'][number]
type Field = 'scheduled_seconds' | 'actual_seconds' | 'overtime_seconds'
const series: { field: Field; color: string; label: 'scheduled' | 'actual' | 'overtime' }[] = [
  { field: 'scheduled_seconds', color: '--text-muted', label: 'scheduled' },
  { field: 'actual_seconds', color: '--accent', label: 'actual' },
  { field: 'overtime_seconds', color: '--warning', label: 'overtime' },
]
const displayName = (item: Item) => item.person_name?.trim() || item.person_no?.trim() || item.employee_key
const toHours = (seconds: number) => seconds / 3600
const periods: DashboardFilters['granularity'][] = ['day', 'week', 'month', 'year']

export default function EmployeeWorkHoursComparisonChart({ data }: { data: EmployeeWorkHoursRanking }) {
  const { t, lang } = useI18n()
  const period = useDashboardStore((state) => state.applied.granularity)
  const setGranularity = useDashboardStore((state) => state.setGranularity)
  const host = useRef<HTMLDivElement>(null)
  const [width, setWidth] = useState(700)
  const [active, setActive] = useState<{ item: Item; field: Field } | null>(null)
  const rtl = lang === 'ar'
  const items = data.items
  const units = { day: t('nav.dashboard.units.day'), hour: t('nav.dashboard.units.hour'), minute: t('nav.dashboard.units.minute'), zero: t('nav.dashboard.units.zero') }
  const labels = { scheduled: t('nav.dashboard.chart.scheduled'), actual: t('nav.dashboard.chart.actual'), overtime: t('nav.dashboard.chart.overtime') }

  useEffect(() => {
    if (!host.current) return
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(300, entry.contentRect.width)))
    observer.observe(host.current)
    return () => observer.disconnect()
  }, [])

  const chart = useMemo(() => {
    const rowHeight = 68
    const height = Math.max(180, items.length * rowHeight + 48)
    const maximumLabelLength = d3.max(items, (item) => displayName(item).length) ?? 0
    const labelWidth = Math.max(120, Math.min(240, maximumLabelLength * 7 + 24))
    const margin = { top: 8, right: rtl ? labelWidth : 18, bottom: 40, left: rtl ? 18 : labelWidth }
    const innerWidth = Math.max(80, width - margin.left - margin.right)
    const innerHeight = height - margin.top - margin.bottom
    const maximum = d3.max(items, (item) => Math.max(item.scheduled_seconds, item.actual_seconds, item.overtime_seconds)) ?? 0
    const x = d3.scaleLinear().domain([0, Math.max(1, toHours(maximum))]).nice(5).range([0, innerWidth])
    const y = d3.scaleBand<string>().domain(items.map((item) => `${item.rank}:${item.org_id ?? ''}:${item.employee_key}`)).range([0, innerHeight]).paddingInner(.3)
    const grouped = d3.scaleBand<Field>().domain(series.map((entry) => entry.field)).range([0, y.bandwidth()]).padding(.1)
    return { height, margin, innerWidth, innerHeight, x, y, grouped }
  }, [items, rtl, width])

  return <div>
    <div className="mb-3 flex flex-wrap items-center justify-between gap-3"><div className="flex flex-wrap gap-3 text-xs text-secondary">{series.map(({ color, label }) => <span key={label} className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: `var(${color})` }} />{labels[label]}</span>)}</div><select aria-label={t('nav.dashboard.chart.granularity')} value={period} onChange={(event) => void setGranularity(event.target.value as DashboardFilters['granularity'])} className="min-h-10 rounded-lg border border-bd bg-surface-2 px-3">{periods.map((value) => <option key={value} value={value}>{t(`nav.dashboard.granularity.${value}`)}</option>)}</select></div>
    <div ref={host} className="relative max-h-[32rem] w-full overflow-auto" data-testid="employee-comparison-scroll">
      <svg role="img" aria-labelledby="employee-chart-title employee-chart-desc" width={width} height={chart.height} className="min-w-full">
        <title id="employee-chart-title">{t('nav.dashboard.chart.title')}</title>
        <desc id="employee-chart-desc">{t('nav.dashboard.chart.description')}</desc>
        <g transform={`translate(${chart.margin.left},${chart.margin.top})`}>
          {chart.x.ticks(5).map((tick) => <g key={tick} transform={`translate(${chart.x(tick)},0)`}><line y2={chart.innerHeight} stroke="var(--border)" opacity=".55" /><text y={chart.innerHeight + 24} textAnchor="middle" fill="var(--text-secondary)" fontSize="10">{formatNumber(Math.round(tick * 10) / 10, lang)} {t('nav.dashboard.units.hour')}</text></g>)}
          {items.map((item) => {
            const key = `${item.rank}:${item.org_id ?? ''}:${item.employee_key}`
            const name = displayName(item)
            const rowY = chart.y(key) ?? 0
            return <g key={key} data-testid="employee-chart-row">
              <text data-testid="employee-chart-name" x={rtl ? chart.innerWidth + 10 : -10} y={rowY + chart.y.bandwidth() / 2} dy=".35em" textAnchor={rtl ? 'start' : 'end'} fill="var(--text-primary)" fontSize="12"><title>{name}</title>{name.length > 28 ? `${name.slice(0, 27)}…` : name}</text>
              {series.map(({ field, color, label }) => <rect key={field} data-series={label} x={0} y={rowY + (chart.grouped(field) ?? 0)} width={chart.x(toHours(item[field]))} height={chart.grouped.bandwidth()} rx="2" fill={`var(${color})`} tabIndex={0} aria-label={`${name}, ${labels[label]}: ${formatDuration(item[field], lang, units)}`} onMouseEnter={() => setActive({ item, field })} onMouseLeave={() => setActive(null)} onFocus={() => setActive({ item, field })} onBlur={() => setActive(null)}><title>{name} — {labels[label]}: {formatDuration(item[field], lang, units)}</title></rect>)}
            </g>
          })}
        </g>
      </svg>
      {active && <div role="tooltip" className="sticky bottom-2 ms-auto me-2 w-fit rounded-lg border border-bd bg-surface p-3 text-xs shadow-md"><strong>{displayName(active.item)}</strong>{series.map(({ field, label }) => <div key={field}>{labels[label]}: {formatDuration(active.item[field], lang, units)}</div>)}</div>}
    </div>
  </div>
}
