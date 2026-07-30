import { create } from 'zustand'
import { throwIfError } from '../../../infra/shared/utils/apiError'
import { getLocationTree, getLocations, createLocation, updateLocation, deleteLocation, getLocationsByType, createLocationWithFullChain, getCommandUnits } from '../api'
import type { LocationCreate, LocationUpdate, LocationType, LocationChainCreate, UnitChainItem, UnitType } from '../types'

export interface LocationItem {
    id: number
    name: string
    type: LocationType
    parent_id: number | null
    path: string
    unit_id: number | null
    unit_name: string | null
    is_active: boolean
    sort_order: number
    children?: LocationItem[]
}

export interface CommandUnitItem {
    id: number
    name: string
    type: UnitType
}

interface LocationState {
    treeItems: LocationItem[]
    flatItems: LocationItem[]
    itemsByType: Partial<Record<LocationType, LocationItem[]>>
    commandUnits: CommandUnitItem[]
    selectedUnitId: number | null
    isLoading: boolean
    fetchTree: (unitId?: number | null) => Promise<void>
    fetch: () => Promise<void>
    fetchByType: (type: LocationType) => Promise<void>
    fetchCommandUnits: () => Promise<void>
    create: (payload: LocationCreate) => Promise<void>
    update: (id: number, payload: LocationUpdate) => Promise<void>
    remove: (id: number) => Promise<void>
    createWithFullChain: (payload: LocationChainCreate) => Promise<void>
    setSelectedUnitId: (unitId: number | null) => void
    reset: () => void
}

export const useLocationStore = create<LocationState>((set, get) => ({
    treeItems: [],
    flatItems: [],
    itemsByType: {},
    commandUnits: [],
    selectedUnitId: null,
    isLoading: false,

    fetchTree: async (unitId?: number | null) => {
        set({ isLoading: true })
        try {
            const { data, error } = await getLocationTree(unitId)
            throwIfError(error)
            if (data) {
                const processTreeItems = (items: LocationItem[]): LocationItem[] => {
                    return items.map(item => ({
                        ...item,
                        children: item.children ? processTreeItems(item.children) : undefined,
                    }))
                }
                const processedData = processTreeItems(data)
                set({ treeItems: processedData, isLoading: false })
            }
        } catch (e) {
            set({ isLoading: false })
            throw e
        }
    },

    fetch: async () => {
        set({ isLoading: true })
        try {
            const { data, error } = await getLocations()
            throwIfError(error)
            if (data) set({ flatItems: data, isLoading: false })
        } catch (e) {
            set({ isLoading: false })
            throw e
        }
    },

    fetchByType: async (type) => {
        set({ isLoading: true })
        try {
            const { data, error } = await getLocationsByType(type)
            throwIfError(error)
            if (data) {
                set(state => ({
                    itemsByType: { ...state.itemsByType, [type]: data },
                    isLoading: false
                }))
            }
        } catch (e) {
            set({ isLoading: false })
            throw e
        }
    },

    create: async (payload) => {
        const { data, error } = await createLocation(payload)
        throwIfError(error)
        await get().fetchTree()
        await get().fetch()
    },

    update: async (id, payload) => {
        const { data, error } = await updateLocation(id, payload)
        throwIfError(error)
        await get().fetchTree()
        await get().fetch()
    },

    remove: async (id) => {
        const { error } = await deleteLocation(id)
        throwIfError(error)
        await get().fetchTree()
        await get().fetch()
    },

    createWithFullChain: async (payload) => {
        const { data, error } = await createLocationWithFullChain(payload)
        throwIfError(error)
        await get().fetchTree(get().selectedUnitId)
        await get().fetch()
    },

    fetchCommandUnits: async () => {
        const { data, error } = await getCommandUnits()
        throwIfError(error)
        if (data) {
            const commandUnitItems: CommandUnitItem[] = data.map((unit) => ({
                id: unit.id,
                name: unit.name,
                type: unit.type,
            }))
            set({ commandUnits: commandUnitItems })
        }
    },

    setSelectedUnitId: (unitId) => {
        set({ selectedUnitId: unitId })
        get().fetchTree(unitId)
    },

    reset: () => set({ treeItems: [], flatItems: [], itemsByType: {}, commandUnits: [], selectedUnitId: null, isLoading: false }),
}))
