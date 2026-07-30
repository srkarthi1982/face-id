import { useI18n } from '../../../infra/locales/I18nContext'
import { useDashboardStore } from '../store'
import type { EmployeeWorkHoursRanking } from '../types'
import { formatDuration, formatNumber } from '../utils'

export default function EmployeeRankingTable({ data }: { data: EmployeeWorkHoursRanking }) {
  const { t, lang } = useI18n()
  const setRankingLimit = useDashboardStore((state) => state.setRankingLimit)
  const rankingLimit = useDashboardStore((state) => state.applied.ranking_limit)
  const units = { day: t('nav.dashboard.units.day'), hour: t('nav.dashboard.units.hour'), minute: t('nav.dashboard.units.minute'), zero: t('nav.dashboard.units.zero') }
  const headers = ['rank', 'employee', 'employeeNo', 'organization', 'department', 'reportDays', 'actual', 'overtime', 'late'] as const

  return <>
    <div className="mb-3 flex justify-end">
      <label className="text-sm text-secondary">{t('nav.dashboard.ranking.limit')}
        <select aria-label={t('nav.dashboard.ranking.limit')} className="ms-2 min-h-10 rounded-lg border border-bd bg-surface-2 px-2" value={rankingLimit} onChange={(event) => void setRankingLimit(Number(event.target.value))}>
          {[5, 10, 20, 50].map((value) => <option key={value}>{value}</option>)}
        </select>
      </label>
    </div>
    <div className="overflow-x-auto">
      <table className="w-full min-w-[780px] text-start text-sm">
        <thead className="bg-surface-2 text-secondary"><tr>{headers.map((header) => <th scope="col" key={header} className="px-3 py-3 text-start font-medium">{t(`nav.dashboard.ranking.${header}`)}</th>)}</tr></thead>
        <tbody>{data.items.map((item) => <tr key={`${item.org_id ?? ''}:${item.person_id ?? ''}:${item.person_no ?? ''}:${item.employee_key}`} className="border-t border-bd">
          <td className="px-3 py-3">{formatNumber(item.rank, lang)}</td>
          <td className="max-w-48 truncate px-3 py-3 font-medium" title={item.person_name ?? item.person_no ?? item.employee_key}>{item.person_name ?? item.person_no ?? item.employee_key}</td>
          <td className="px-3 py-3">{item.person_no ?? '—'}</td><td className="px-3 py-3">{item.org_id ?? '—'}</td>
          <td className="max-w-48 truncate px-3 py-3" title={item.department_name ?? ''}>{item.department_name ?? '—'}</td>
          <td className="px-3 py-3">{formatNumber(item.report_day_count, lang)}</td><td className="px-3 py-3">{formatDuration(item.actual_seconds, lang, units)}</td>
          <td className="px-3 py-3">{formatDuration(item.overtime_seconds, lang, units)}</td><td className="px-3 py-3">{formatDuration(item.late_seconds, lang, units)}</td>
        </tr>)}</tbody>
      </table>
    </div>
  </>
}
