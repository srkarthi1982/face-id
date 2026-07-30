export type LocationType = 'emirate' | 'base' | 'location' | 'building' | 'area'
export type UnitType = 'force' | 'command' | 'battalion' | 'unit'

export const LOCATION_VALID_PARENTS: Record<LocationType, LocationType[]> = {
    emirate: [],
    base: ['emirate'],
    location: ['base'],
    building: ['base', 'location'],
    area: ['base', 'location', 'building'],
}

export const UNIT_VALID_PARENTS: Record<UnitType, UnitType[]> = {
    force: [],
    command: ['force'],
    battalion: ['command'],
    unit: ['battalion'],
}

export interface LocationCreate {
    name: string
    type?: LocationType
    parent_id?: number | null
    unit_id?: number | null
    sort_order?: number
}

export interface LocationUpdate {
    name?: string
    type?: LocationType
    parent_id?: number | null
    unit_id?: number | null
    is_active?: boolean
    sort_order?: number
}

export interface UnitCreate {
    name: string
    code?: string | null
    description?: string | null
    type?: 'force' | 'command' | 'battalion' | 'unit'
    parent_id?: number | null
    sort_order?: number
}

export interface UnitUpdate {
    name?: string
    code?: string | null
    description?: string | null
    type?: UnitType
    parent_id?: number | null
    is_active?: boolean
    sort_order?: number
}

export interface LocationChainItem {
    type: LocationType
    name: string
    sort_order?: number
}

export interface LocationChainCreate {
    chain: LocationChainItem[]
    skip_indices: number[]
    unit_id?: number | null
}

export interface UnitChainItem {
    type: UnitType
    name: string
    code?: string | null
    description?: string | null
    sort_order?: number
}

export interface UnitChainCreate {
    chain: UnitChainItem[]
}
