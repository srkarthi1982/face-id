import { useShallow } from 'zustand/react/shallow'
import { useI18n } from '../../../infra/locales/I18nContext'
import { useDashboardStore } from '../store'

export default function DashboardFilters() {
  const { t } = useI18n()
  const { draft, filterError, organizations, setDraft, apply, reset } = useDashboardStore(useShallow((s) => ({
    draft: s.draft, filterError: s.filterError, organizations: s.organizations, setDraft: s.setDraft, apply: s.apply, reset: s.reset,
  })))
  return (
    <section className="grid gap-4 rounded-xl border border-bd bg-surface p-4 shadow-sm sm:grid-cols-2 xl:grid-cols-[1fr_1fr_1.2fr_auto]" aria-label={t('nav.dashboard.filters.title')}>
      <label className="flex flex-col gap-1 text-sm text-secondary"><span>{t('nav.dashboard.filters.start')}</span><input data-testid="dashboard-start" type="date" max={draft.end_date} value={draft.start_date ?? ''} aria-describedby={filterError ? 'dashboard-filter-error' : undefined} aria-invalid={Boolean(filterError)} onChange={(e) => setDraft({ start_date: e.target.value || undefined })} className="min-h-11 rounded-lg border border-bd bg-surface-2 px-3 text-primary focus:outline-none focus:ring-2 focus:ring-accent" /></label>
      <label className="flex flex-col gap-1 text-sm text-secondary"><span>{t('nav.dashboard.filters.end')}</span><input data-testid="dashboard-end" type="date" min={draft.start_date} value={draft.end_date ?? ''} aria-describedby={filterError ? 'dashboard-filter-error' : undefined} aria-invalid={Boolean(filterError)} onChange={(e) => setDraft({ end_date: e.target.value || undefined })} className="min-h-11 rounded-lg border border-bd bg-surface-2 px-3 text-primary focus:outline-none focus:ring-2 focus:ring-accent" /></label>
      <label className="flex flex-col gap-1 text-sm text-secondary"><span>{t('nav.dashboard.filters.organization')}</span><select data-testid="dashboard-org" value={draft.org_id ?? ''} onChange={(event) => setDraft({ org_id: event.target.value || undefined })} className="min-h-11 rounded-lg border border-bd bg-surface-2 px-3 text-primary focus:outline-none focus:ring-2 focus:ring-accent"><option value="">{t('nav.dashboard.filters.allOrganizations')}</option>{(organizations.data ?? []).map((option) => <option key={option.org_id} value={option.org_id}>{option.org_id}</option>)}</select>{organizations.status === 'loading' && <span role="status" className="text-xs text-muted">{t('nav.dashboard.filters.organizationsLoading')}</span>}{(organizations.status === 'error' || organizations.status === 'unavailable') && <span role="alert" className="text-xs text-[var(--danger)]">{t('nav.dashboard.filters.organizationsUnavailable')}</span>}</label>
      <div className="flex items-end gap-2 sm:col-span-2 xl:col-span-1"><button data-testid="dashboard-apply" onClick={() => void apply()} className="min-h-11 flex-1 rounded-lg bg-accent px-4 font-medium text-surface focus:outline-none focus:ring-2 focus:ring-accent">{t('nav.dashboard.actions.apply')}</button><button data-testid="dashboard-reset" onClick={() => void reset()} className="min-h-11 rounded-lg border border-bd px-4 text-secondary focus:outline-none focus:ring-2 focus:ring-accent">{t('nav.dashboard.actions.reset')}</button></div>
      {filterError && <p id="dashboard-filter-error" role="alert" className="text-sm text-[var(--danger)] sm:col-span-2 xl:col-span-4">{t('nav.dashboard.validation.dateRange')}</p>}
    </section>
  )
}
