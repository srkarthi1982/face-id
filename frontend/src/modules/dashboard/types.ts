import type {
  AttendanceExceptionItem,
  DashboardDepartmentOption,
  DashboardOverview,
  DashboardTrend,
  DashboardTrendGranularity,
  EmployeeWorkHoursRanking,
  Meta,
} from '../../api/generated'

export type PanelStatus = 'idle' | 'loading' | 'available' | 'empty' | 'unavailable' | 'error'

export type DashboardFilters = {
  start_date?: string
  end_date?: string
  department_id?: number
  granularity: DashboardTrendGranularity
  ranking_limit: number
  exception_page: number
  exception_page_size: number
}

export type PanelState<T> = { status: PanelStatus; data: T | null }

export type ExceptionResult = { items: AttendanceExceptionItem[]; meta: Meta }

export type { DashboardOverview, DashboardTrend, EmployeeWorkHoursRanking }
export type { DashboardDepartmentOption }
