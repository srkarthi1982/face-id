import { useEffect, useMemo, useRef, useState } from 'react'
import * as d3 from 'd3'
import { useI18n } from '../../../infra/locales/I18nContext'
import { useDashboardStore } from '../store'
import type { DashboardFilters, DashboardTrend } from '../types'
import { formatDuration, formatNumber } from '../utils'

type TrendPoint = DashboardTrend['points'][number]
const granularities: DashboardFilters['granularity'][] = ['day', 'week', 'month', 'year']
const series = [
  { field: 'scheduled_seconds', color: '--text-muted', label: 'scheduled' },
  { field: 'actual_seconds', color: '--accent', label: 'actual' },
  { field: 'overtime_seconds', color: '--warning', label: 'overtime' },
] as const

export default function WorkHoursTrendChart({ data }: { data: DashboardTrend }) {
  const { t, lang } = useI18n(); const setGranularity = useDashboardStore((state) => state.setGranularity)
  const host = useRef<HTMLDivElement>(null); const [width, setWidth] = useState(700); const [active, setActive] = useState<number | null>(null)
  const points = useMemo(() => [...data.points].sort((left, right) => left.period_start.localeCompare(right.period_start)), [data.points])
  const units = { day: t('nav.dashboard.units.day'), hour: t('nav.dashboard.units.hour'), minute: t('nav.dashboard.units.minute'), zero: t('nav.dashboard.units.zero') }
  const labels = {
    scheduled: t('nav.dashboard.chart.scheduled'), actual: t('nav.dashboard.chart.actual'), overtime: t('nav.dashboard.chart.overtime'),
    day: t('nav.dashboard.granularity.day'), week: t('nav.dashboard.granularity.week'), month: t('nav.dashboard.granularity.month'), year: t('nav.dashboard.granularity.year'),
  }

  useEffect(() => {
    if (!host.current) return
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(280, entry.contentRect.width)))
    observer.observe(host.current); return () => observer.disconnect()
  }, [])

  const chart = useMemo(() => {
    const height = 280; const margin = { top: 20, right: 18, bottom: 42, left: 62 }
    const innerWidth = Math.max(1, width - margin.left - margin.right); const innerHeight = height - margin.top - margin.bottom
    const x = d3.scalePoint<string>().domain(points.map((point) => point.period_key)).range([0, innerWidth]).padding(.25)
    const maximum = d3.max(points, (point) => Math.max(point.scheduled_seconds, point.actual_seconds, point.overtime_seconds)) ?? 1
    const y = d3.scaleLinear().domain([0, maximum]).nice().range([innerHeight, 0])
    const paths = series.map(({ field }) => d3.line<TrendPoint>().x((point) => x(point.period_key) ?? 0).y((point) => y(point[field]))(points) ?? '')
    const xTicks = points.filter((_point, index) => index % Math.max(1, Math.ceil(points.length / 6)) === 0)
    return { height, margin, innerHeight, x, y, paths, xTicks, yTicks: y.ticks(5) }
  }, [points, width])

  const point = active === null ? null : points[active]
  return <div>
    <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
      <div className="flex flex-wrap gap-3 text-xs text-secondary">{series.map(({ color, label }) => <span key={label} className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: `var(${color})` }} />{labels[label]}</span>)}</div>
      <select aria-label={t('nav.dashboard.chart.granularity')} value={data.granularity} onChange={(event) => void setGranularity(event.target.value as DashboardFilters['granularity'])} className="min-h-10 rounded-lg border border-bd bg-surface-2 px-3">{granularities.map((value) => <option key={value} value={value}>{labels[value]}</option>)}</select>
    </div>
    <div ref={host} className="relative w-full overflow-hidden">
      <svg role="img" aria-labelledby="trend-title trend-desc" viewBox={`0 0 ${width} ${chart.height}`} className="h-auto w-full">
        <title id="trend-title">{t('nav.dashboard.chart.title')}</title><desc id="trend-desc">{t('nav.dashboard.chart.description')}</desc>
        <g transform={`translate(${chart.margin.left},${chart.margin.top})`}>
          <line x1="0" y1={chart.innerHeight} x2={width - chart.margin.left - chart.margin.right} y2={chart.innerHeight} stroke="var(--border)" />
          {chart.yTicks.map((tick) => <g key={tick} transform={`translate(0,${chart.y(tick)})`}><line x1="-4" x2="0" stroke="var(--border)" /><text x="-8" dy="0.32em" textAnchor="end" fill="var(--text-secondary)" fontSize="10">{tick / 3600} {t('nav.dashboard.units.hour')}</text></g>)}
          {chart.xTicks.map((tick) => <text key={tick.period_key} x={chart.x(tick.period_key)} y={chart.innerHeight + 24} textAnchor="middle" fill="var(--text-secondary)" fontSize="10">{tick.period_key}</text>)}
          {series.map(({ color, label }, index) => <path key={label} data-series={label} d={chart.paths[index]} fill="none" stroke={`var(${color})`} strokeWidth="2" />)}
          {points.map((entry, index) => <circle key={entry.period_key} cx={chart.x(entry.period_key)} cy={chart.y(entry.actual_seconds)} r="5" fill="var(--accent)" stroke="var(--surface)" strokeWidth="2" className="cursor-pointer" onMouseEnter={() => setActive(index)} onMouseLeave={() => setActive(null)} />)}
        </g>
      </svg>
      <div className="sr-only"><table><caption>{t('nav.dashboard.chart.summary')}</caption><thead><tr><th>{t('nav.dashboard.chart.period')}</th><th>{labels.scheduled}</th><th>{labels.actual}</th><th>{labels.overtime}</th><th>{t('nav.dashboard.kpi.employees')}</th></tr></thead><tbody>{points.map((entry, index) => <tr key={entry.period_key}><td><button onFocus={() => setActive(index)} onBlur={() => setActive(null)}>{entry.period_key}</button></td><td>{formatDuration(entry.scheduled_seconds, lang, units)}</td><td>{formatDuration(entry.actual_seconds, lang, units)}</td><td>{formatDuration(entry.overtime_seconds, lang, units)}</td><td>{formatNumber(entry.employee_count, lang)}</td></tr>)}</tbody></table></div>
      {point && <div className="absolute end-2 top-2 rounded-lg border border-bd bg-surface p-3 text-xs shadow-md"><strong>{point.period_key}</strong><div>{labels.scheduled}: {formatDuration(point.scheduled_seconds, lang, units)}</div><div>{labels.actual}: {formatDuration(point.actual_seconds, lang, units)}</div><div>{labels.overtime}: {formatDuration(point.overtime_seconds, lang, units)}</div><div>{t('nav.dashboard.kpi.employees')}: {formatNumber(point.employee_count, lang)}</div></div>}
    </div>
  </div>
}
