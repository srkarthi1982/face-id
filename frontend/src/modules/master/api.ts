import { client } from '../../api/client'
import type { DepartmentCreate, DepartmentUpdate, LocationCreate, UnitCreate, LocationType, TimingCreate, TimingUpdate, UnitType, LocationChainCreate, UnitChainCreate } from './types'

export interface LocationTreeItem {
    id: number
    name: string
    type: LocationType
    path: string
    is_active: boolean
    sort_order: number
    parent_id: number | null
    unit_id: number | null
    unit_name: string | null
    children?: LocationTreeItem[]
}

export interface LocationResponse {
    id: number
    name: string
    type: LocationType
    parent_id: number | null
    unit_id: number | null
    unit_name: string | null
    path: string
    is_active: boolean
    sort_order: number
    created_at: string
    updated_at: string
}

export interface UnitTreeItem {
    id: number
    name: string
    code: string | null
    type: UnitType
    path: string
    is_active: boolean
    sort_order: number
    children?: UnitTreeItem[]
}

export interface UnitResponse {
    id: number
    name: string
    code: string | null
    description: string | null
    type: UnitType
    parent_id: number | null
    path: string
    is_active: boolean
    sort_order: number
    created_at: string
    updated_at: string
}

export interface DepartmentResponse {
    id: number
    name: string
    code: string | null
    description: string | null
    parent_id: number | null
    path: string
    is_active: boolean
    sort_order: number
    created_at: string
    updated_at: string
}

export interface TimingResponse {
    id: number
    department_id: number
    department_name: string
    start_day: string
    end_day: string
    start_time: string
    end_time: string
    is_active: boolean
    created_at: string
    updated_at: string
}

export async function getLocationTree(unitId?: number | null): Promise<{ data?: LocationTreeItem[]; error?: unknown }> {
    const url = unitId 
        ? `/api/v1/master-data/locations/tree?unit_id=${unitId}`
        : '/api/v1/master-data/locations/tree'
    const result = await client.get({ url })
    return { data: result.data as LocationTreeItem[] | undefined, error: result.error }
}

export async function getLocations(): Promise<{ data?: LocationResponse[]; error?: unknown }> {
    const result = await client.get({
        url: '/api/v1/master-data/locations',
    })
    return { data: result.data as LocationResponse[] | undefined, error: result.error }
}

export async function getLocationsByType(type: LocationType): Promise<{ data?: LocationResponse[]; error?: unknown }> {
    const result = await client.get({
        url: `/api/v1/master-data/locations/by-type/${type}`,
    })
    return { data: result.data as LocationResponse[] | undefined, error: result.error }
}

export async function getValidParentLocations(childType: LocationType): Promise<{ data?: LocationResponse[]; error?: unknown }> {
    const result = await client.get({
        url: `/api/v1/master-data/locations/valid-parents/${childType}`,
    })
    return { data: result.data as LocationResponse[] | undefined, error: result.error }
}

export async function createLocationWithFullChain(body: LocationChainCreate): Promise<{ data?: any; error?: unknown }> {
    const result = await client.post({
        url: '/api/v1/master-data/locations/with-full-chain',
        body: {
            chain: body.chain,
            skip_indices: body.skip_indices,
            unit_id: body.unit_id,
        },
    })
    return { data: result.data as any | undefined, error: result.error }
}

export async function createLocation(body: LocationCreate): Promise<{ data?: LocationResponse; error?: unknown }> {
    const result = await client.post({
        url: '/api/v1/master-data/locations',
        body,
    })
    return { data: result.data as LocationResponse | undefined, error: result.error }
}

export async function updateLocation(id: number, body: Partial<LocationCreate>): Promise<{ data?: LocationResponse; error?: unknown }> {
    const result = await client.put({
        url: `/api/v1/master-data/locations/${id}`,
        body,
    })
    return { data: result.data as LocationResponse | undefined, error: result.error }
}

export async function deleteLocation(id: number): Promise<{ error?: unknown }> {
    return client.delete({
        url: `/api/v1/master-data/locations/${id}`,
    })
}

export async function getUnitTree(): Promise<{ data?: UnitTreeItem[]; error?: unknown }> {
    const result = await client.get({
        url: '/api/v1/master-data/units/tree',
    })
    return { data: result.data as UnitTreeItem[] | undefined, error: result.error }
}

export async function getUnits(): Promise<{ data?: UnitResponse[]; error?: unknown }> {
    const result = await client.get({
        url: '/api/v1/master-data/units',
    })
    return { data: result.data as UnitResponse[] | undefined, error: result.error }
}

export async function getUnitsByType(type: UnitType): Promise<{ data?: UnitResponse[]; error?: unknown }> {
      const result = await client.get({
          url: `/api/v1/master-data/units/by-type/${type}`,
      })
      return { data: result.data as UnitResponse[] | undefined, error: result.error }
  }
  
  export async function getValidParentUnits(childType: UnitType): Promise<{ data?: UnitResponse[]; error?: unknown }> {
      const result = await client.get({
          url: `/api/v1/master-data/units/valid-parents/${childType}`,
      })
    return { data: result.data as UnitResponse[] | undefined, error: result.error }
}

export async function createUnitWithFullChain(body: UnitChainCreate): Promise<{ data?: any; error?: unknown }> {
    const result = await client.post({
        url: '/api/v1/master-data/units/with-full-chain',
        body,
    })
    return { data: result.data as any | undefined, error: result.error }
}

export async function createUnit(body: UnitCreate): Promise<{ data?: UnitResponse; error?: unknown }> {
    const result = await client.post({
        url: '/api/v1/master-data/units',
        body,
    })
    return { data: result.data as UnitResponse | undefined, error: result.error }
}

export async function updateUnit(id: number, body: Partial<UnitCreate>): Promise<{ data?: UnitResponse; error?: unknown }> {
    const result = await client.put({
        url: `/api/v1/master-data/units/${id}`,
        body,
    })
    return { data: result.data as UnitResponse | undefined, error: result.error }
}

export async function deleteUnit(id: number): Promise<{ error?: unknown }> {
    return client.delete({
        url: `/api/v1/master-data/units/${id}`,
    })
}

export async function getDepartments(activeOnly = false): Promise<{ data?: DepartmentResponse[]; error?: unknown }> {
    const result = await client.get({
        url: `/api/v1/master-data/departments${activeOnly ? '?active_only=true' : ''}`,
    })
    return { data: result.data as DepartmentResponse[] | undefined, error: result.error }
}

export async function createDepartment(body: DepartmentCreate): Promise<{ data?: DepartmentResponse; error?: unknown }> {
    const result = await client.post({ url: '/api/v1/master-data/departments', body })
    return { data: result.data as DepartmentResponse | undefined, error: result.error }
}

export async function updateDepartment(id: number, body: DepartmentUpdate): Promise<{ data?: DepartmentResponse; error?: unknown }> {
    const result = await client.put({ url: `/api/v1/master-data/departments/${id}`, body })
    return { data: result.data as DepartmentResponse | undefined, error: result.error }
}

export async function deleteDepartment(id: number): Promise<{ error?: unknown }> {
    return client.delete({ url: `/api/v1/master-data/departments/${id}` })
}

export async function getTimings(): Promise<{ data?: TimingResponse[]; error?: unknown }> {
    const result = await client.get({ url: '/api/v1/master-data/timings' })
    return { data: result.data as TimingResponse[] | undefined, error: result.error }
}

export async function createTiming(body: TimingCreate): Promise<{ data?: TimingResponse; error?: unknown }> {
    const result = await client.post({ url: '/api/v1/master-data/timings', body })
    return { data: result.data as TimingResponse | undefined, error: result.error }
}

export async function updateTiming(id: number, body: TimingUpdate): Promise<{ data?: TimingResponse; error?: unknown }> {
    const result = await client.put({ url: `/api/v1/master-data/timings/${id}`, body })
    return { data: result.data as TimingResponse | undefined, error: result.error }
}

export async function deleteTiming(id: number): Promise<{ error?: unknown }> {
    return client.delete({ url: `/api/v1/master-data/timings/${id}` })
}

export async function getCommandUnits(): Promise<{ data?: UnitResponse[]; error?: unknown }> {
    const result = await client.get({
        url: '/api/v1/master-data/units/commands',
    })
    return { data: result.data as UnitResponse[] | undefined, error: result.error }
}
