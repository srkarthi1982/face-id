import { useShallow } from 'zustand/react/shallow'
import { useI18n } from '../../../infra/locales/I18nContext'
import { useDashboardStore } from '../store'

export default function DashboardRankingHeader() {
  const { t } = useI18n()
  const { rankingLimit, setRankingLimit } = useDashboardStore(useShallow((state) => ({ rankingLimit: state.applied.ranking_limit, setRankingLimit: state.setRankingLimit })))
  return <div data-testid="ranking-header" className="mb-4 flex flex-wrap items-center justify-between gap-3">
    <h2 className="text-lg font-semibold">{t('nav.dashboard.ranking.title')}</h2>
    <label className="text-sm text-secondary">{t('nav.dashboard.ranking.limit')}<select aria-label={t('nav.dashboard.ranking.limit')} className="ms-2 min-h-10 rounded-lg border border-bd bg-surface-2 px-2" value={rankingLimit} onChange={(event) => void setRankingLimit(Number(event.target.value))}>{[5, 10, 20, 50].map((value) => <option key={value}>{value}</option>)}</select></label>
  </div>
}
