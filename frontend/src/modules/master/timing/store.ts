import { create } from 'zustand'
import { throwIfError } from '../../../infra/shared/utils/apiError'
import { createTiming, deleteTiming, getDepartments, getTimings, updateTiming } from '../api'
import type { DepartmentResponse, TimingResponse } from '../api'
import type { TimingCreate, TimingUpdate } from '../types'

interface TimingState {
    items: TimingResponse[]
    departments: DepartmentResponse[]
    isLoading: boolean
    fetch: () => Promise<void>
    create: (payload: TimingCreate) => Promise<void>
    update: (id: number, payload: TimingUpdate) => Promise<void>
    remove: (id: number) => Promise<void>
}

export const useTimingStore = create<TimingState>((set, get) => ({
    items: [],
    departments: [],
    isLoading: false,

    fetch: async () => {
        set({ isLoading: true })
        try {
            const [timingResult, departmentResult] = await Promise.all([
                getTimings(),
                getDepartments(true),
            ])
            throwIfError(timingResult.error)
            throwIfError(departmentResult.error)
            set({
                items: timingResult.data ?? [],
                departments: departmentResult.data ?? [],
                isLoading: false,
            })
        } catch (error) {
            set({ isLoading: false })
            throw error
        }
    },

    create: async (payload) => {
        const { error } = await createTiming(payload)
        throwIfError(error)
        await get().fetch()
    },

    update: async (id, payload) => {
        const { error } = await updateTiming(id, payload)
        throwIfError(error)
        await get().fetch()
    },

    remove: async (id) => {
        const { error } = await deleteTiming(id)
        throwIfError(error)
        await get().fetch()
    },
}))
