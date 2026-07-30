import { create } from 'zustand'
import { client } from '../../api/client'
import { throwIfError } from '../../infra/shared/utils/apiError'
import type { PersonnelResponse } from '../../api/generated/index'

export interface PersonnelItem extends PersonnelResponse {}

export interface PersonnelCreate {
    emp_no: string
    full_name: string
    gender?: number
    email?: string | null
    phone?: string | null
    date_of_birth?: string | null
    nationality?: string | null
    idcard_num?: string | null
    id_number?: string | null
    card_no?: string | null
    department_id?: number | null
    position?: string | null
    hire_date?: string | null
    org_id?: number | null
    person_id_internal?: string | null
    person_id_device?: string | null
    permissions?: Record<string, unknown>
    pass_time?: Record<string, unknown> | null
    push_to_device?: boolean
    is_active?: boolean
}

export interface PersonnelUpdate {
    emp_no?: string
    full_name?: string
    gender?: number | null
    email?: string | null
    phone?: string | null
    date_of_birth?: string | null
    nationality?: string | null
    idcard_num?: string | null
    id_number?: string | null
    card_no?: string | null
    department_id?: number | null
    position?: string | null
    hire_date?: string | null
    push_to_device?: boolean | null
    person_id_internal?: string | null
    person_id_device?: string | null
    permissions?: Record<string, unknown> | null
    pass_time?: Record<string, unknown> | null
    is_active?: boolean | null
}

interface ListPersonnelParams {
    page: number
    page_size: number
    org_id?: number
    sort_by?: string
    order?: 'asc' | 'desc'
    filters?: {
        emp_no?: string
        full_name?: string
        email?: string
        gender?: number
        is_active?: boolean
        department_id?: number
        search?: string
    }
}

interface PersonnelState {
    items: PersonnelItem[]
    pagination: {
        page: number
        page_size: number
        total: number
        pages: number
    }
    isLoading: boolean
    fetch: (page?: number, params?: Partial<ListPersonnelParams>) => Promise<void>
    create: (payload: PersonnelCreate) => Promise<void>
    update: (id: number, payload: PersonnelUpdate) => Promise<void>
    remove: (id: number) => Promise<void>
    restore: (id: number) => Promise<void>
    reset: () => void
}

const DEFAULT_PAGINATION = {
    page: 1,
    page_size: 20,
    total: 0,
    pages: 1,
}

function apiErrMessage(err: unknown): string {
    if (!err) return 'An unexpected error occurred'
    if (typeof err === 'string') return err
    const e = err as Record<string, unknown>
    return (
        (typeof e.message === 'string' ? e.message : null) ||
        (typeof e.detail === 'string' ? e.detail : null) ||
        (typeof e.error === 'string' ? e.error : null) ||
        JSON.stringify(err)
    )
}

export const usePersonnelStore = create<PersonnelState>((set, get) => ({
    items: [],
    pagination: { ...DEFAULT_PAGINATION },
    isLoading: false,

    fetch: async (page = 1, params) => {
        set({ isLoading: true })
        try {
            const searchParams = new URLSearchParams()
            searchParams.set('page', String(page))
            searchParams.set('page_size', String(get().pagination.page_size))
            
            const effectiveParams = params ?? {}
            
            // Add org_id filter if provided
            if (effectiveParams.org_id) {
                searchParams.set('org_id', String(effectiveParams.org_id))
            }
            
            // Add sorting
            if (effectiveParams.sort_by) {
                searchParams.set('sort_by', effectiveParams.sort_by)
                searchParams.set('order', effectiveParams.order ?? 'asc')
            }
            
            // Add filters
            if (effectiveParams.filters) {
                const filters = effectiveParams.filters
                if (filters.emp_no) searchParams.set('emp_no', filters.emp_no)
                if (filters.full_name) searchParams.set('full_name', filters.full_name)
                if (filters.email) searchParams.set('email', filters.email)
                if (filters.gender !== undefined && filters.gender !== null) {
                    searchParams.set('gender', String(filters.gender))
                }
                if (filters.is_active !== undefined && filters.is_active !== null) {
                    searchParams.set('is_active', String(filters.is_active))
                }
                if (filters.department_id) {
                    searchParams.set('department_id', String(filters.department_id))
                }
                if (filters.search) {
                    searchParams.set('search', filters.search)
                }
            }

            const res = await client.get({
                url: `/api/v1/personnel/?${searchParams.toString()}`,
            })
            
            throwIfError(res.error)
            
            if (res.data) {
                const successRes = res.data as { 
                    success: boolean
                    data: PersonnelItem[]
                    meta?: { page: number; page_size: number; total: number; pages: number }
                }
                
                if (successRes?.data) {
                    const meta = successRes.meta ?? DEFAULT_PAGINATION
                    set({ 
                        items: successRes.data, 
                        pagination: {
                            page: meta.page ?? page,
                            page_size: meta.page_size ?? get().pagination.page_size,
                            total: meta.total ?? 0,
                            pages: meta.pages ?? 1,
                        },
                        isLoading: false 
                    })
                }
            }
        } catch (e) {
            set({ isLoading: false })
            throw e
        }
    },

    create: async (payload) => {
        const { error } = await client.post({
            url: '/api/v1/personnel/',
            body: payload,
            headers: { 'Content-Type': 'application/json' },
        })
        
        throwIfError(error)
        
        // Re-fetch current page
        await get().fetch(get().pagination.page)
    },

    update: async (id, payload) => {
        const { error } = await client.put({
            url: `/api/v1/personnel/${id}`,
            body: payload,
            headers: { 'Content-Type': 'application/json' },
        })
        
        throwIfError(error)
        
        // Re-fetch current page
        await get().fetch(get().pagination.page)
    },

    remove: async (id) => {
        const { error } = await client.delete({
            url: `/api/v1/personnel/${id}`,
        })
        
        throwIfError(error)
        
        // Re-fetch current page
        await get().fetch(get().pagination.page)
    },

    restore: async (id) => {
        const { error } = await client.post({
            url: `/api/v1/personnel/${id}/restore`,
        })
        
        throwIfError(error)
        
        // Re-fetch current page
        await get().fetch(get().pagination.page)
    },

    reset: () => set({ 
        items: [], 
        pagination: { ...DEFAULT_PAGINATION }, 
        isLoading: false 
    }),
}))
