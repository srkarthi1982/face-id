import { client } from '../../api/client'
import type { DeviceCreate, DeviceResponse, DiscoveredDevice } from '../../api/generated'

function apiErrMessage(err: unknown): string {
    if (!err) return 'An unexpected error occurred'
    if (typeof err === 'string') return err
    const e = err as Record<string, unknown>
    return (
        (typeof e.message === 'string' ? e.message : null) ||
        (typeof e.detail === 'string' ? e.detail : null) ||
        (typeof e.error === 'string' ? e.error : null) ||
        ((typeof e.error === 'object' && e.error && 'message' in e.error && typeof (e.error as any).message === 'string')
            ? (e.error as any).message
            : null) ||
        JSON.stringify(err)
    )
}

export interface ListDevicesParams {
    page: number
    page_size: number
    search_text?: string
    status?: string
}

type SuccessResp<T> = { success: boolean; data: T; meta: unknown }

function extractMessage(res: any): { message: string } {
    const d = res?.data
    if (d && typeof d === 'object' && 'message' in d) {
        return d
    }
    throw new Error('Failed to connect device')
}

export async function listDevices(params: ListDevicesParams): Promise<{ data: DeviceResponse[]; meta: Record<string, unknown> }> {
    const searchParams = new URLSearchParams()
    searchParams.set('page', String(params.page))
    searchParams.set('page_size', String(params.page_size))
    if (params.search_text) searchParams.set('search_text', params.search_text)
    if (params.status) searchParams.set('status', params.status)

    const res = await (client as any).get({
        url: `/api/v1/device/endpoint/?${searchParams.toString()}`,
    })
    if (res.error) throw new Error(apiErrMessage(res.error) || 'Failed to list devices')
    const successRes = res.data as SuccessResp<DeviceResponse[]>
    if (!successRes?.data) throw new Error('Empty response')
    return { data: successRes.data, meta: (successRes.meta ?? {}) as Record<string, unknown> }
}

export async function addDevice(payload: DeviceCreate): Promise<DeviceResponse> {
    const res = await (client as any).post({
        url: '/api/v1/device/endpoint/',
        body: payload,
        headers: { 'Content-Type': 'application/json' },
    })
    if (res.error) throw new Error(apiErrMessage(res.error) || 'Failed to add device')
    const successRes = res.data as SuccessResp<DeviceResponse>
    if (!successRes?.data) throw new Error('Failed to add device')
    return successRes.data
}

export async function editDevice(id: number, payload: Partial<DeviceCreate> & { state?: string | null }): Promise<DeviceResponse> {
    const res = await (client as any).put({
        url: `/api/v1/device/endpoint/${id}`,
        body: payload,
        headers: { 'Content-Type': 'application/json' },
    })
    if (res.error) throw new Error(apiErrMessage(res.error) || 'Failed to edit device')
    const successRes = res.data as SuccessResp<DeviceResponse>
    if (!successRes?.data) throw new Error('Failed to edit device')
    return successRes.data
}

export async function removeDevice(id: number): Promise<DeviceResponse> {
    const res = await (client as any).delete({
        url: `/api/v1/device/endpoint/${id}`,
    })
    // 404 means device already deleted — treat as success
    if (res.status === 404) {
        return { id, device_name: '', ip_address: '', port: 8090, status: 'deleted', created_at: '', updated_at: '', device_id: '', api_password: '', settings: {}, callback_urls: {} }
    }
    // 204 No Content means success with no body
    if (res.status === 204) {
        return { id, device_name: '', ip_address: '', port: 8090, status: 'deleted', created_at: '', updated_at: '', device_id: '', api_password: '', settings: {}, callback_urls: {} }
    }
    if (res.error) throw new Error(apiErrMessage(res.error) || 'Failed to remove device')
    const successRes = res.data as SuccessResp<DeviceResponse>
    if (!successRes?.data) throw new Error('Failed to remove device')
    return successRes.data
}

export async function refreshDevice(id: number): Promise<DeviceResponse> {
    const res = await (client as any).post({
        url: `/api/v1/device/endpoint/${id}/refresh`,
    })
    if (res.error) throw new Error(apiErrMessage(res.error) || 'Failed to refresh device')
    const successRes = res.data as SuccessResp<DeviceResponse>
    if (!successRes?.data) throw new Error('Failed to refresh device')
    return successRes.data
}

export async function saveDevice(payload: DeviceCreate): Promise<{ message: string }> {
    const res = await (client as any).post({
        url: '/api/v1/device/setup/connect',
        body: payload,
        headers: { 'Content-Type': 'application/json' },
        throwOnError: false,
        responseStyle: 'fields',
    })
    if (res.error) throw new Error(apiErrMessage(res.error) || 'Failed to connect device')
    const successRes = res.data as SuccessResp<{ message: string }>
    if (successRes?.data?.message) {
        return successRes.data
    }
    throw new Error('Failed to connect device')
}

export async function scanDevices(params: { subnet?: string } = {}, signal?: AbortSignal): Promise<{ success: boolean; devices: DiscoveredDevice[] }> {
    const res = await (client as any).post({
        url: '/api/v1/device/setup/discover',
        body: params,
        headers: { 'Content-Type': 'application/json' },
        signal,
    })
    if (res.error) throw new Error(apiErrMessage(res.error) || 'Failed to discover devices')
    const successRes = res.data as SuccessResp<DiscoveredDevice[]>
    if (!successRes?.data) throw new Error('Empty response')
    return { success: true, devices: successRes.data }
}
