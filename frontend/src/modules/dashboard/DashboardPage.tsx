import { useEffect } from 'react'
import { HiMiniCubeTransparent, HiOutlineArrowPath } from 'react-icons/hi2'
import { useShallow } from 'zustand/react/shallow'
import SectionHeader from '../../infra/shared/components/SectionHeader'
import { useI18n } from '../../infra/locales/I18nContext'
import { useDashboardStore } from './store'
import DashboardFilters from './components/DashboardFilters'
import DashboardPanelState from './components/DashboardPanelState'
import DashboardKpiGrid from './components/DashboardKpiGrid'
import WorkHoursTrendChart from './components/WorkHoursTrendChart'
import EmployeeRankingTable from './components/EmployeeRankingTable'
import AttendanceExceptionsTable from './components/AttendanceExceptionsTable'
import { formatDate } from './utils'

export default function DashboardPage() {
  const { t, lang } = useI18n()
  const { overview, trend, ranking, exceptions, loadAll, refresh, retry, dispose } = useDashboardStore(useShallow((s)=>({overview:s.overview,trend:s.trend,ranking:s.ranking,exceptions:s.exceptions,loadAll:s.loadAll,refresh:s.refresh,retry:s.retry,dispose:s.dispose})))
  useEffect(()=>{void loadAll();return dispose},[loadAll,dispose])
  const dates=overview.data

  return (
    <div className="flex min-w-0 flex-col gap-5" data-testid="attendance-dashboard">
      <div className="flex flex-wrap items-start justify-between gap-3"><div><SectionHeader icon={<HiMiniCubeTransparent />} title={t('nav.dashboard.title')} /><p className="mt-1 text-sm text-muted">{t('nav.dashboard.description')}</p>{dates&&<p className="mt-2 text-xs text-secondary">{t('nav.dashboard.effectiveRange')}: {formatDate(dates.effective_start_date,lang)} — {formatDate(dates.effective_end_date,lang)} · {t('nav.dashboard.latestSource')}: {formatDate(dates.source_latest_report_date,lang)}</p>}</div><button aria-label={t('nav.dashboard.actions.refresh')} onClick={()=>void refresh()} className="flex min-h-11 items-center gap-2 rounded-lg border border-bd bg-surface px-4 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-accent"><HiOutlineArrowPath />{t('nav.dashboard.actions.refresh')}</button></div>
      <DashboardFilters />
      <DashboardPanelState status={overview.status} onRetry={()=>void retry('overview')}>{overview.data&&<DashboardKpiGrid data={overview.data}/>}</DashboardPanelState>
      <section className="rounded-xl border border-bd bg-surface p-4 shadow-sm"><h2 className="mb-4 text-lg font-semibold">{t('nav.dashboard.chart.title')}</h2><DashboardPanelState status={trend.status} onRetry={()=>void retry('trend')}>{trend.data&&<WorkHoursTrendChart data={trend.data}/>}</DashboardPanelState></section>
      <section className="rounded-xl border border-bd bg-surface p-4 shadow-sm"><h2 className="mb-4 text-lg font-semibold">{t('nav.dashboard.ranking.title')}</h2><DashboardPanelState status={ranking.status} onRetry={()=>void retry('ranking')}>{ranking.data&&<EmployeeRankingTable data={ranking.data}/>}</DashboardPanelState></section>
      <section className="rounded-xl border border-bd bg-surface p-4 shadow-sm"><h2 className="mb-4 text-lg font-semibold">{t('nav.dashboard.exceptions.title')}</h2><DashboardPanelState status={exceptions.status} onRetry={()=>void retry('exceptions')}>{exceptions.data&&<AttendanceExceptionsTable data={exceptions.data}/>}</DashboardPanelState></section>
    </div>
  )
}
