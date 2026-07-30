import { useShallow } from 'zustand/react/shallow'
import { useI18n } from '../../../infra/locales/I18nContext'
import { useDashboardStore } from '../store'

export default function DashboardFilters() {
  const { t } = useI18n()
  const { draft, setDraft, apply, reset } = useDashboardStore(useShallow((s) => ({
    draft: s.draft, setDraft: s.setDraft, apply: s.apply, reset: s.reset,
  })))
  return (
    <section className="grid gap-4 rounded-xl border border-bd bg-surface p-4 shadow-sm sm:grid-cols-2 xl:grid-cols-[1fr_1fr_1.2fr_auto]" aria-label={t('nav.dashboard.filters.title')}>
      <label className="flex flex-col gap-1 text-sm text-secondary"><span>{t('nav.dashboard.filters.start')}</span><input data-testid="dashboard-start" type="date" value={draft.start_date ?? ''} onChange={(e) => setDraft({ start_date: e.target.value || undefined })} className="min-h-11 rounded-lg border border-bd bg-surface-2 px-3 text-primary focus:outline-none focus:ring-2 focus:ring-accent" /></label>
      <label className="flex flex-col gap-1 text-sm text-secondary"><span>{t('nav.dashboard.filters.end')}</span><input data-testid="dashboard-end" type="date" value={draft.end_date ?? ''} onChange={(e) => setDraft({ end_date: e.target.value || undefined })} className="min-h-11 rounded-lg border border-bd bg-surface-2 px-3 text-primary focus:outline-none focus:ring-2 focus:ring-accent" /></label>
      <label className="flex flex-col gap-1 text-sm text-secondary"><span>{t('nav.dashboard.filters.organization')}</span><input data-testid="dashboard-org" value={draft.org_id ?? ''} maxLength={64} onChange={(e) => setDraft({ org_id: e.target.value || undefined })} className="min-h-11 rounded-lg border border-bd bg-surface-2 px-3 text-primary focus:outline-none focus:ring-2 focus:ring-accent" /></label>
      <div className="flex items-end gap-2 sm:col-span-2 xl:col-span-1"><button data-testid="dashboard-apply" onClick={() => void apply()} className="min-h-11 flex-1 rounded-lg bg-accent px-4 font-medium text-surface focus:outline-none focus:ring-2 focus:ring-accent">{t('nav.dashboard.actions.apply')}</button><button data-testid="dashboard-reset" onClick={() => void reset()} className="min-h-11 rounded-lg border border-bd px-4 text-secondary focus:outline-none focus:ring-2 focus:ring-accent">{t('nav.dashboard.actions.reset')}</button></div>
    </section>
  )
}
