import { useEffect, useMemo, useRef, useState } from 'react'
import * as d3 from 'd3'
import { useI18n } from '../../../infra/locales/I18nContext'
import { useDashboardStore } from '../store'
import type { DashboardTrend } from '../types'
import { formatDuration, formatNumber } from '../utils'

export default function WorkHoursTrendChart({ data }: { data: DashboardTrend }) {
  const { t, lang } = useI18n()
  const setGranularity = useDashboardStore((state) => state.setGranularity)
  const host = useRef<HTMLDivElement>(null)
  const svg = useRef<SVGSVGElement>(null)
  const [width, setWidth] = useState(700)
  const [active, setActive] = useState<number | null>(null)
  const points = useMemo(() => [...data.points].sort((left, right) => left.period_start.localeCompare(right.period_start)), [data.points])
  const units = { day: t('nav.dashboard.units.day'), hour: t('nav.dashboard.units.hour'), minute: t('nav.dashboard.units.minute'), zero: t('nav.dashboard.units.zero') }

  useEffect(() => {
    if (!host.current) return
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(280, entry.contentRect.width)))
    observer.observe(host.current)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (!svg.current) return
    const root = d3.select(svg.current); root.selectAll('*').remove()
    const height = 280; const margin = { top: 20, right: 18, bottom: 42, left: 62 }
    const innerW = Math.max(1, width - margin.left - margin.right); const innerH = height - margin.top - margin.bottom
    const x = d3.scalePoint().domain(points.map((point) => point.period_key)).range([0, innerW]).padding(.25)
    const maximum = d3.max(points, (point: (typeof points)[number]) => Math.max(point.scheduled_seconds, point.actual_seconds, point.overtime_seconds)) ?? 1
    const y = d3.scaleLinear().domain([0, maximum]).nice().range([innerH, 0])
    const group = root.attr('viewBox', `0 0 ${width} ${height}`).append('g').attr('transform', `translate(${margin.left},${margin.top})`)
    const styles = getComputedStyle(document.documentElement)
    const colors = ['--text-muted', '--accent', '--warning'].map((token) => styles.getPropertyValue(token).trim())
    const ticks = x.domain().filter((_value: string, index: number) => index % Math.max(1, Math.ceil(points.length / 6)) === 0)
    group.append('g').attr('transform', `translate(0,${innerH})`).call(d3.axisBottom(x).tickValues(ticks)).call((axis: any) => axis.selectAll('text').attr('fill', 'var(--text-secondary)'))
    group.append('g').call(d3.axisLeft(y).ticks(5).tickFormat((value: number) => `${Number(value) / 3600} ${t('nav.dashboard.units.hour')}`)).call((axis: any) => axis.selectAll('text').attr('fill', 'var(--text-secondary)'))
    ;(['scheduled_seconds', 'actual_seconds', 'overtime_seconds'] as const).forEach((field, index) => {
      const line = d3.line().x((point: (typeof points)[number]) => x(point.period_key) ?? 0).y((point: (typeof points)[number]) => y(point[field]))
      group.append('path').datum(points).attr('fill', 'none').attr('stroke', colors[index]).attr('stroke-width', 2).attr('d', line)
    })
    group.selectAll('circle.trend-point').data(points).join('circle').attr('class', 'trend-point').attr('cx', (point: (typeof points)[number]) => x(point.period_key) ?? 0).attr('cy', (point: (typeof points)[number]) => y(point.actual_seconds)).attr('r', 5).attr('fill', 'var(--accent)').attr('stroke', 'var(--surface)').attr('stroke-width', 2).style('cursor', 'pointer').on('mouseenter', (_event: unknown, point: (typeof points)[number]) => setActive(points.indexOf(point))).on('mouseleave', () => setActive(null))
    return () => { root.selectAll('*').remove() }
  }, [points, width, t])

  const point = active === null ? null : points[active]
  return <div>
    <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
      <div className="flex flex-wrap gap-3 text-xs text-secondary">{(['scheduled', 'actual', 'overtime'] as const).map((key, index) => <span key={key} className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: `var(${['--text-muted', '--accent', '--warning'][index]})` }} />{t(`nav.dashboard.chart.${key}` as any)}</span>)}</div>
      <select aria-label={t('nav.dashboard.chart.granularity')} value={data.granularity} onChange={(event) => void setGranularity(event.target.value as any)} className="min-h-10 rounded-lg border border-bd bg-surface-2 px-3">{(['day', 'week', 'month', 'year'] as const).map((value) => <option key={value} value={value}>{t(`nav.dashboard.granularity.${value}` as any)}</option>)}</select>
    </div>
    <div ref={host} className="relative w-full overflow-hidden">
      <svg ref={svg} role="img" aria-labelledby="trend-title trend-desc" className="h-auto w-full"><title id="trend-title">{t('nav.dashboard.chart.title')}</title><desc id="trend-desc">{t('nav.dashboard.chart.description')}</desc></svg>
      <div className="sr-only"><table><caption>{t('nav.dashboard.chart.summary')}</caption><tbody>{points.map((entry, index) => <tr key={entry.period_key}><td><button onFocus={() => setActive(index)} onBlur={() => setActive(null)}>{entry.period_key}</button></td><td>{formatDuration(entry.actual_seconds, lang, units)}</td></tr>)}</tbody></table></div>
      {point && <div className="absolute end-2 top-2 rounded-lg border border-bd bg-surface p-3 text-xs shadow-md"><strong>{point.period_key}</strong><div>{t('nav.dashboard.chart.scheduled')}: {formatDuration(point.scheduled_seconds, lang, units)}</div><div>{t('nav.dashboard.chart.actual')}: {formatDuration(point.actual_seconds, lang, units)}</div><div>{t('nav.dashboard.chart.overtime')}: {formatDuration(point.overtime_seconds, lang, units)}</div><div>{t('nav.dashboard.kpi.employees')}: {formatNumber(point.employee_count, lang)}</div></div>}
    </div>
  </div>
}
