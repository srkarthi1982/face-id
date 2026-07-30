import { create } from 'zustand'
import { throwIfError } from '../../../infra/shared/utils/apiError'
import { getUnitTree, getUnits, createUnit, updateUnit, deleteUnit, getUnitsByType, createUnitWithFullChain } from '../api'
import type { UnitCreate, UnitUpdate, UnitType, UnitChainCreate } from '../types'

export interface UnitItem {
    id: number
    name: string
    code: string | null
    description?: string | null
    type: UnitType
    path: string
    is_active: boolean
    sort_order: number
    parent_id?: number | null
    children?: UnitItem[]
}

interface UnitState {
    treeItems: UnitItem[]
    flatItems: UnitItem[]
    itemsByType: Partial<Record<UnitType, UnitItem[]>>
    isLoading: boolean
    fetchTree: () => Promise<void>
    fetch: () => Promise<void>
    fetchByType: (type: UnitType) => Promise<void>
    create: (payload: UnitCreate) => Promise<void>
    update: (id: number, payload: UnitUpdate) => Promise<void>
    remove: (id: number) => Promise<void>
    createWithFullChain: (payload: UnitChainCreate) => Promise<void>
    reset: () => void
}

export const useUnitStore = create<UnitState>((set, get) => ({
    treeItems: [],
    flatItems: [],
    itemsByType: {},
    isLoading: false,

    fetchTree: async () => {
        set({ isLoading: true })
        try {
            const { data, error } = await getUnitTree()
            throwIfError(error)
            if (data) {
                const processTreeItems = (items: UnitItem[]): UnitItem[] => {
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
            const { data, error } = await getUnits()
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
            const { data, error } = await getUnitsByType(type)
            throwIfError(error)
            if (data) {
                const sortedData = [...data].sort((a, b) => a.name.localeCompare(b.name))
                set(state => ({
                    itemsByType: { ...state.itemsByType, [type]: sortedData },
                    isLoading: false
                }))
            }
        } catch (e) {
            set({ isLoading: false })
            throw e
        }
    },

    create: async (payload) => {
        const { data, error } = await createUnit(payload)
        throwIfError(error)
        await get().fetchTree()
        await get().fetch()
    },

    update: async (id, payload) => {
        const { data, error } = await updateUnit(id, payload)
        throwIfError(error)
        await get().fetchTree()
        await get().fetch()
    },

    remove: async (id) => {
        const { error } = await deleteUnit(id)
        throwIfError(error)
        await get().fetchTree()
        await get().fetch()
    },

    createWithFullChain: async (payload) => {
        const { data, error } = await createUnitWithFullChain(payload)
        throwIfError(error)
        await get().fetchTree()
        await get().fetch()
        await get().fetchByType('force')
        await get().fetchByType('command')
        await get().fetchByType('battalion')
        await get().fetchByType('unit')
    },

    reset: () => set({ treeItems: [], flatItems: [], itemsByType: {}, isLoading: false }),
}))
