import '../../api/client'
import { create } from 'zustand'
import {
  attendanceExceptionsApiV1DashboardAttendanceExceptionsGet as fetchExceptions,
  overviewApiV1DashboardOverviewGet as fetchOverview,
  workHoursRankingApiV1DashboardWorkHoursRankingGet as fetchRanking,
  workHoursTrendApiV1DashboardWorkHoursTrendGet as fetchTrend,
} from '../../api/generated'
import type { DashboardFilters, DashboardOverview, DashboardTrend, EmployeeWorkHoursRanking, ExceptionResult, PanelState } from './types'

const defaults = (): DashboardFilters => ({
  granularity: 'week', ranking_limit: 10, exception_page: 1, exception_page_size: 20,
})
const panel = <T>(): PanelState<T> => ({ status: 'idle', data: null })
let generation = 0
let controllers: AbortController[] = []

function query(filters: DashboardFilters) {
  return {
    ...(filters.start_date ? { start_date: filters.start_date } : {}),
    ...(filters.end_date ? { end_date: filters.end_date } : {}),
    ...(filters.org_id?.trim() ? { org_id: filters.org_id.trim() } : {}),
  }
}

function abortCurrent() {
  controllers.forEach((controller) => controller.abort())
  controllers = []
}

function statusFor(error: unknown): 'unavailable' | 'error' {
  const candidate = error as { code?: string; error?: { code?: string }; status?: number }
  const code = candidate?.code ?? candidate?.error?.code ?? ''
  return candidate?.status === 503 || code === 'HTTP_ERROR' || code.includes('UNAVAILABLE') ? 'unavailable' : 'error'
}

type State = {
  draft: DashboardFilters
  applied: DashboardFilters
  overview: PanelState<DashboardOverview>
  trend: PanelState<DashboardTrend>
  ranking: PanelState<EmployeeWorkHoursRanking>
  exceptions: PanelState<ExceptionResult>
  setDraft: (patch: Partial<DashboardFilters>) => void
  loadAll: () => Promise<void>
  apply: () => Promise<void>
  reset: () => Promise<void>
  refresh: () => Promise<void>
  setGranularity: (value: DashboardFilters['granularity']) => Promise<void>
  setExceptionPage: (page: number) => Promise<void>
  setExceptionPageSize: (pageSize: number) => Promise<void>
  retry: (section: 'overview' | 'trend' | 'ranking' | 'exceptions') => Promise<void>
  dispose: () => void
}

export const useDashboardStore = create<State>((set, get) => {
  const run = async <T>(
    section: 'overview' | 'trend' | 'ranking' | 'exceptions',
    request: (signal: AbortSignal) => Promise<{ data?: unknown; error?: unknown }>,
    pick: (data: any) => T,
    empty: (data: T) => boolean,
    requestGeneration: number,
  ) => {
    const controller = new AbortController()
    controllers.push(controller)
    set((state) => ({ ...state, [section]: { ...state[section], status: 'loading' } }))
    try {
      const result = await request(controller.signal)
      if (requestGeneration !== generation || controller.signal.aborted) return
      if (result.error) {
        set((state) => ({ ...state, [section]: { ...state[section], status: statusFor(result.error) } }))
        return
      }
      const value = pick(result.data)
      set({ [section]: { data: value, status: empty(value) ? 'empty' : 'available' } } as Partial<State>)
    } catch {
      if (requestGeneration === generation && !controller.signal.aborted) {
        set((state) => ({ ...state, [section]: { ...state[section], status: 'error' } }))
      }
    } finally {
      controllers = controllers.filter((current) => current !== controller)
    }
  }

  const loadSection = async (section: 'overview' | 'trend' | 'ranking' | 'exceptions', ownGeneration = generation) => {
    const filters = get().applied
    const base = query(filters)
    if (section === 'overview') return run(section,
      (signal) => fetchOverview({ query: base, signal }),
      (data) => data.data, (data) => data.data_status === 'empty', ownGeneration)
    if (section === 'trend') return run(section,
      (signal) => fetchTrend({ query: { ...base, granularity: filters.granularity }, signal }),
      (data) => data.data, (data) => data.points.length === 0, ownGeneration)
    if (section === 'ranking') return run(section,
      (signal) => fetchRanking({ query: { ...base, limit: filters.ranking_limit }, signal }),
      (data) => data.data, (data) => data.items.length === 0, ownGeneration)
    return run(section,
      (signal) => fetchExceptions({ query: { ...base, page: filters.exception_page, page_size: filters.exception_page_size }, signal }),
      (data) => ({ items: data.data, meta: data.meta }), (data) => data.items.length === 0, ownGeneration)
  }

  const startGeneration = () => { abortCurrent(); generation += 1; return generation }
  return {
    draft: defaults(), applied: defaults(), overview: panel(), trend: panel(), ranking: panel(), exceptions: panel(),
    setDraft: (patch) => set((state) => ({ draft: { ...state.draft, ...patch } })),
    loadAll: async () => {
      const current = startGeneration()
      await Promise.allSettled(['overview', 'trend', 'ranking', 'exceptions'].map((name) => loadSection(name as any, current)))
    },
    apply: async () => {
      const next = { ...get().draft, exception_page: 1 }
      set({ applied: next, draft: next })
      await get().loadAll()
    },
    reset: async () => {
      const next = defaults(); set({ draft: next, applied: next }); await get().loadAll()
    },
    refresh: async () => get().loadAll(),
    setGranularity: async (value) => {
      const current = startGeneration()
      set((state) => ({ draft: { ...state.draft, granularity: value }, applied: { ...state.applied, granularity: value } }))
      await loadSection('trend', current)
    },
    setExceptionPage: async (page) => {
      const current = startGeneration()
      set((state) => ({ applied: { ...state.applied, exception_page: page }, draft: { ...state.draft, exception_page: page } }))
      await loadSection('exceptions', current)
    },
    setExceptionPageSize: async (pageSize) => {
      const current = startGeneration()
      set((state) => ({ applied: { ...state.applied, exception_page: 1, exception_page_size: pageSize }, draft: { ...state.draft, exception_page: 1, exception_page_size: pageSize } }))
      await loadSection('exceptions', current)
    },
    retry: async (section) => loadSection(section),
    dispose: () => { abortCurrent(); generation += 1 },
  }
})
