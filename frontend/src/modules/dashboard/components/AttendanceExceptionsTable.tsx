import { useI18n } from '../../../infra/locales/I18nContext'
import { useDashboardStore } from '../store'
import type { ExceptionResult } from '../types'
import { formatDate, formatNumber, formatWallClockTime } from '../utils'

const headerKeys = ['date', 'time', 'employee', 'employeeNo', 'organization', 'device'] as const

export default function AttendanceExceptionsTable({ data }: { data: ExceptionResult }) {
  const { t, lang } = useI18n()
  const setPage = useDashboardStore((state) => state.setExceptionPage); const setPageSize = useDashboardStore((state) => state.setExceptionPageSize)
  const { page, pages, page_size } = data.meta
  const headers = {
    date: t('nav.dashboard.exceptions.date'), time: t('nav.dashboard.exceptions.time'), employee: t('nav.dashboard.exceptions.employee'),
    employeeNo: t('nav.dashboard.exceptions.employeeNo'), organization: t('nav.dashboard.exceptions.organization'), device: t('nav.dashboard.exceptions.device'),
  }
  return <>
    <div className="overflow-x-auto"><table className="w-full min-w-[650px] text-sm">
      <thead className="bg-surface-2 text-secondary"><tr>{headerKeys.map((key) => <th scope="col" key={key} className="px-3 py-3 text-start font-medium">{headers[key]}</th>)}</tr></thead>
      <tbody>{data.items.map((item) => <tr key={`${item.org_id ?? ''}:${item.id}`} className="border-t border-bd">
        <td className="px-3 py-3">{formatDate(item.report_date, lang)}</td><td className="px-3 py-3">{formatWallClockTime(item.clock_time, lang)}</td>
        <td className="px-3 py-3">{item.person_name ?? item.person_no ?? t('nav.dashboard.exceptions.unknown')}</td><td className="px-3 py-3">{item.person_no ?? '—'}</td>
        <td className="px-3 py-3">{item.org_id ?? '—'}</td><td className="px-3 py-3">{item.device_name ?? item.device_key ?? '—'}</td>
      </tr>)}</tbody>
    </table></div>
    <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm">
      <label>{t('nav.dashboard.exceptions.pageSize')}<select aria-label={t('nav.dashboard.exceptions.pageSize')} className="ms-2 min-h-10 rounded-lg border border-bd bg-surface-2 px-2" value={page_size} onChange={(event) => void setPageSize(Number(event.target.value))}>{[10, 20, 50].map((value) => <option key={value}>{value}</option>)}</select></label>
      <div className="flex items-center gap-2"><button aria-label={t('nav.dashboard.actions.previous')} disabled={page <= 1} onClick={() => void setPage(page - 1)} className="min-h-10 rounded-lg border border-bd px-3 disabled:opacity-40">{t('nav.dashboard.actions.previous')}</button><span>{formatNumber(page, lang)} / {formatNumber(Math.max(pages, 1), lang)}</span><button aria-label={t('nav.dashboard.actions.next')} disabled={page >= pages} onClick={() => void setPage(page + 1)} className="min-h-10 rounded-lg border border-bd px-3 disabled:opacity-40">{t('nav.dashboard.actions.next')}</button></div>
    </div>
  </>
}
