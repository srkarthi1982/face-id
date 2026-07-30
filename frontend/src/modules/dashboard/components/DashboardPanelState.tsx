import type { ReactNode } from 'react'
import { useI18n } from '../../../infra/locales/I18nContext'
import type { PanelStatus } from '../types'

export default function DashboardPanelState({ status, onRetry, children }: {
  status: PanelStatus; onRetry: () => void; children: ReactNode
}) {
  const { t } = useI18n()
  if (status === 'loading' || status === 'idle') return <div className="min-h-32 rounded-xl bg-surface-2 motion-safe:animate-pulse" role="status" aria-label={t('nav.dashboard.states.loading')} />
  if (status === 'empty') return <div className="py-10 text-center text-sm text-muted">{t('nav.dashboard.states.empty')}</div>
  if (status === 'unavailable' || status === 'error') return (
    <div className="flex min-h-32 flex-col items-center justify-center gap-3 text-center" role="alert">
      <p className="text-sm text-muted">{status === 'unavailable' ? t('nav.dashboard.states.unavailable') : t('nav.dashboard.states.error')}</p>
      <button className="min-h-11 rounded-lg border border-bd px-4 text-sm font-medium text-accent focus:outline-none focus:ring-2 focus:ring-accent" onClick={onRetry}>{t('nav.dashboard.actions.retry')}</button>
    </div>
  )
  return <>{children}</>
}
