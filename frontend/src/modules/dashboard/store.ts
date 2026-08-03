import '../../api/client'
import { create } from 'zustand'
import {
  attendanceExceptionsApiV1DashboardAttendanceExceptionsGet as fetchExceptions,
  organizationsApiV1DashboardOrganizationsGet as fetchOrganizations,
  overviewApiV1DashboardOverviewGet as fetchOverview,
  workHoursRankingApiV1DashboardWorkHoursRankingGet as fetchRanking,
} from '../../api/generated'
import type { SuccessResponseDashboardOverview, SuccessResponseEmployeeWorkHoursRanking, SuccessResponseListAttendanceExceptionItem, SuccessResponseListDashboardOrganizationOption } from '../../api/generated'
import type { DashboardFilters, DashboardOrganizationOption, DashboardOverview, EmployeeWorkHoursRanking, ExceptionResult, PanelState } from './types'

type Section = 'organizations' | 'overview' | 'comparison' | 'ranking' | 'exceptions'
type FilterError = 'dateRange' | null
type SdkResult<T> = { data?: T; error?: unknown; response: Response }

const analyticsSections: Section[] = ['overview', 'comparison', 'ranking', 'exceptions']
const sections: Section[] = ['organizations', ...analyticsSections]
const defaults = (): DashboardFilters => ({ granularity: 'week', ranking_limit: 10, exception_page: 1, exception_page_size: 20 })
const panel = <T>(): PanelState<T> => ({ status: 'idle', data: null })
const controllers: Record<Section, AbortController | null> = { organizations: null, overview: null, comparison: null, ranking: null, exceptions: null }
const requestIds: Record<Section, number> = { organizations: 0, overview: 0, comparison: 0, ranking: 0, exceptions: 0 }

function query(filters: DashboardFilters) {
  return {
    ...(filters.start_date ? { start_date: filters.start_date } : {}),
    ...(filters.end_date ? { end_date: filters.end_date } : {}),
    ...(filters.org_id?.trim() ? { org_id: filters.org_id.trim() } : {}),
  }
}

function invalidDateRange(filters: DashboardFilters) {
  return Boolean(filters.start_date && filters.end_date && filters.start_date > filters.end_date)
}

function cancelSection(section: Section) {
  requestIds[section] += 1
  controllers[section]?.abort()
  controllers[section] = null
}

function statusFor(response: Response): 'unavailable' | 'error' {
  return response.status === 503 ? 'unavailable' : 'error'
}

type State = {
  draft: DashboardFilters
  applied: DashboardFilters
  filterError: FilterError
  organizations: PanelState<DashboardOrganizationOption[]>
  overview: PanelState<DashboardOverview>
  comparison: PanelState<EmployeeWorkHoursRanking>
  ranking: PanelState<EmployeeWorkHoursRanking>
  exceptions: PanelState<ExceptionResult>
  setDraft: (patch: Partial<DashboardFilters>) => void
  initialize: () => Promise<void>
  loadAll: () => Promise<void>
  apply: () => Promise<void>
  reset: () => Promise<void>
  refresh: () => Promise<void>
  setRankingLimit: (limit: number) => Promise<void>
  setExceptionPage: (page: number) => Promise<void>
  setExceptionPageSize: (pageSize: number) => Promise<void>
  retry: (section: Section) => Promise<void>
  dispose: () => void
}

export const useDashboardStore = create<State>((set, get) => {
  const run = async <ResponseData, T>(section: Section, request: (signal: AbortSignal) => Promise<SdkResult<ResponseData>>, pick: (data: ResponseData) => T, empty: (data: T) => boolean) => {
    cancelSection(section)
    const requestId = requestIds[section]
    const controller = new AbortController(); controllers[section] = controller
    set((state) => ({ ...state, [section]: { data: section === 'overview' ? null : state[section].data, status: 'loading' } }))
    try {
      const result = await request(controller.signal)
      if (requestId !== requestIds[section] || controller.signal.aborted) return
      if (result.error || result.data === undefined) {
        set({ [section]: { data: null, status: statusFor(result.response) } } as Partial<State>)
        return
      }
      const value = pick(result.data)
      set({ [section]: { data: value, status: empty(value) ? 'empty' : 'available' } } as Partial<State>)
    } catch {
      if (requestId === requestIds[section] && !controller.signal.aborted) set({ [section]: { data: null, status: 'error' } } as Partial<State>)
    } finally {
      if (controllers[section] === controller) controllers[section] = null
    }
  }

  const loadSection = async (section: Section) => {
    const filters = get().applied; const base = query(filters)
    if (section === 'organizations') return run<SuccessResponseListDashboardOrganizationOption, DashboardOrganizationOption[]>(section, (signal) => fetchOrganizations({ signal }), (data) => data.data, () => false)
    if (section === 'overview') return run<SuccessResponseDashboardOverview, DashboardOverview>(section, (signal) => fetchOverview({ query: base, signal }), (data) => data.data, (data) => data.data_status === 'empty')
    if (section === 'comparison') return run<SuccessResponseEmployeeWorkHoursRanking, EmployeeWorkHoursRanking>(section, (signal) => fetchRanking({ query: { ...base, include_all: true }, signal }), (data) => data.data, (data) => data.items.length === 0)
    if (section === 'ranking') return run<SuccessResponseEmployeeWorkHoursRanking, EmployeeWorkHoursRanking>(section, (signal) => fetchRanking({ query: { ...base, limit: filters.ranking_limit }, signal }), (data) => data.data, (data) => data.items.length === 0)
    return run<SuccessResponseListAttendanceExceptionItem, ExceptionResult>(section, (signal) => fetchExceptions({ query: { ...base, page: filters.exception_page, page_size: filters.exception_page_size }, signal }), (data) => ({ items: data.data, meta: data.meta! }), (data) => data.items.length === 0)
  }

  return {
    draft: defaults(), applied: defaults(), filterError: null,
    organizations: panel(), overview: panel(), comparison: panel(), ranking: panel(), exceptions: panel(),
    setDraft: (patch) => set((state) => ({ draft: { ...state.draft, ...patch }, filterError: null })),
    initialize: async () => { await Promise.allSettled(sections.map(loadSection)) },
    loadAll: async () => { await Promise.allSettled(analyticsSections.map(loadSection)) },
    apply: async () => {
      const draft = get().draft
      if (invalidDateRange(draft)) { set({ filterError: 'dateRange' }); return }
      const next = { ...draft, exception_page: 1 }; set({ applied: next, draft: next, filterError: null }); await get().loadAll()
    },
    reset: async () => { const next = defaults(); set({ draft: next, applied: next, filterError: null }); await get().loadAll() },
    refresh: async () => { await Promise.allSettled(sections.map(loadSection)) },
    setRankingLimit: async (limit) => { set((state) => ({ draft: { ...state.draft, ranking_limit: limit }, applied: { ...state.applied, ranking_limit: limit } })); await loadSection('ranking') },
    setExceptionPage: async (page) => { set((state) => ({ draft: { ...state.draft, exception_page: page }, applied: { ...state.applied, exception_page: page } })); await loadSection('exceptions') },
    setExceptionPageSize: async (pageSize) => { set((state) => ({ draft: { ...state.draft, exception_page: 1, exception_page_size: pageSize }, applied: { ...state.applied, exception_page: 1, exception_page_size: pageSize } })); await loadSection('exceptions') },
    retry: loadSection,
    dispose: () => sections.forEach(cancelSection),
  }
})
