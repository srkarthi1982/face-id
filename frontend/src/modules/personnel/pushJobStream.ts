import { client, silent } from '../../api/client'
import { throwIfError } from '../../infra/shared/utils/apiError'

export interface DevicePushResult {
    device_id: number
    device_name?: string | null
    success: boolean
    code?: string | null
    msg?: string | null
}

export interface PushJobError {
    code: 'PERSON_NOT_FOUND' | 'PERSON_INVALID' | 'INTERNAL_ERROR'
    message: string
}

export interface PersonPushJobResult {
    personnel_id: number
    ok: boolean
    pushed: number
    failed: number
    results: DevicePushResult[]
    error: PushJobError | null
}

export interface PushJobSnapshot {
    job_id: string
    status: 'running' | 'completed' | 'cancelled'
    total: number
    done: number
    results: PersonPushJobResult[]
    skipped_personnel_ids: number[]
}

/** The job vanished server-side (pruned, restarted) — final state is unknown. */
export class PushJobLostError extends Error {
    constructor() {
        super('Push job not found')
        this.name = 'PushJobLostError'
    }
}

const isTerminal = (s: PushJobSnapshot) => s.status !== 'running'

interface SubscribeOptions {
    onSnapshot: (snapshot: PushJobSnapshot) => void
    signal: AbortSignal
}

/**
 * Follow a push job until it reaches a terminal snapshot. Tries the SSE
 * stream first (raw fetch — EventSource cannot send the Bearer header) and
 * falls back to polling the snapshot endpoint on any stream problem.
 * Resolves after delivering a terminal snapshot; rejects with
 * PushJobLostError if the job disappears, or the abort reason on abort.
 */
export async function subscribeToPushJob(jobId: string, { onSnapshot, signal }: SubscribeOptions): Promise<void> {
    try {
        const finished = await streamEvents(jobId, onSnapshot, signal)
        if (finished) return
    } catch (err) {
        if (signal.aborted) throw err
        // fall through to polling
    }
    if (signal.aborted) throw new DOMException('Aborted', 'AbortError')
    await pollJob(jobId, onSnapshot, signal)
}

/** Returns true if a terminal snapshot was delivered; false to trigger fallback. */
async function streamEvents(
    jobId: string,
    onSnapshot: (s: PushJobSnapshot) => void,
    signal: AbortSignal,
): Promise<boolean> {
    const res = await fetch(`/api/v1/personnel/push-jobs/${jobId}/events`, {
        headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token') ?? ''}`,
            Accept: 'text/event-stream',
        },
        signal,
    })
    if (!res.ok || !res.body) return false

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    for (;;) {
        const { done, value } = await reader.read()
        if (done) return false
        buffer += decoder.decode(value, { stream: true })
        let sep
        while ((sep = buffer.indexOf('\n\n')) !== -1) {
            const block = buffer.slice(0, sep)
            buffer = buffer.slice(sep + 2)
            const data = block
                .split('\n')
                .filter((line) => line.startsWith('data:'))
                .map((line) => line.slice(5).trim())
                .join('')
            if (!data) continue
            let snapshot: PushJobSnapshot
            try {
                snapshot = JSON.parse(data) as PushJobSnapshot
            } catch {
                continue
            }
            onSnapshot(snapshot)
            if (isTerminal(snapshot)) {
                reader.cancel().catch(() => {})
                return true
            }
        }
    }
}

async function pollJob(
    jobId: string,
    onSnapshot: (s: PushJobSnapshot) => void,
    signal: AbortSignal,
): Promise<void> {
    for (;;) {
        if (signal.aborted) throw new DOMException('Aborted', 'AbortError')
        const res = await client.get({ url: `/api/v1/personnel/push-jobs/${jobId}`, ...silent() })
        if (res.response?.status === 404) throw new PushJobLostError()
        throwIfError(res.error)
        const snapshot = (res.data as { data?: PushJobSnapshot })?.data
        if (snapshot) {
            onSnapshot(snapshot)
            if (isTerminal(snapshot)) return
        }
        await new Promise((resolve) => setTimeout(resolve, 1500))
    }
}
