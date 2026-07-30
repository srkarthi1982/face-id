import { useEffect, useMemo, useRef, useState } from 'react'
import { HiOutlineArrowUpTray, HiOutlineExclamationCircle, HiOutlineCheckCircle, HiOutlineXCircle } from 'react-icons/hi2'
import { client, silent } from '../../api/client'
import { throwIfError } from '../../infra/shared/utils/apiError'
import { useI18n } from '../../infra/locales/I18nContext'
import useToastStore from '../../infra/shared/store/useToastStore'
import SearchBar from '../../infra/shared/components/SearchBar'
import { listDevices } from '../device/api'
import type { DeviceResponse } from '../../api/generated'
import type { PersonnelItem } from './store'
import {
    PushJobLostError,
    subscribeToPushJob,
    type DevicePushResult,
    type PushJobSnapshot,
} from './pushJobStream'

interface PushResponse {
    personnel_id: number
    person_id_device: string
    pushed: number
    failed: number
    results: DevicePushResult[]
}

export interface PersonPushOutcome {
    person: PersonnelItem
    ok: boolean
    response?: PushResponse
    errorMsg?: string
}

interface LocationGroup {
    id: number
    name: string
    deviceIds: number[]
}

type SelectMode = 'location' | 'device'

interface PushToDeviceModalProps {
    persons: PersonnelItem[]
    onClose: () => void
    onPushed?: (outcomes: PersonPushOutcome[]) => void
}

export default function PushToDeviceModal({ persons, onClose, onPushed }: PushToDeviceModalProps) {
    const { t } = useI18n()
    const [devices, setDevices] = useState<DeviceResponse[]>([])
    const [selected, setSelected] = useState<Set<number>>(new Set())
    const [mode, setMode] = useState<SelectMode>('location')
    const [search, setSearch] = useState('')
    const [includePhoto, setIncludePhoto] = useState(true)
    const [isLoading, setIsLoading] = useState(true)
    const [isPushing, setIsPushing] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [outcomes, setOutcomes] = useState<PersonPushOutcome[] | null>(null)
    const [progress, setProgress] = useState<{ done: number; total: number; currentName: string } | null>(null)
    const outcomesRef = useRef<PersonPushOutcome[]>([])
    const lastSnapshotRef = useRef<PushJobSnapshot | null>(null)
    const abortRef = useRef<AbortController | null>(null)
    const jobIdRef = useRef<string | null>(null)

    const isBulk = persons.length > 1

    // Unmounting aborts only the progress stream — the job keeps running
    // server-side; the Cancel button is what actually stops the push.
    useEffect(() => () => { abortRef.current?.abort() }, [])

    useEffect(() => {
        let cancelled = false
        ;(async () => {
            try {
                const all: DeviceResponse[] = []
                for (let page = 1; page <= 50; page++) {
                    const res = await listDevices({ page, page_size: 100 })
                    if (cancelled) return
                    all.push(...res.data)
                    if (res.data.length < 100) break
                }
                setDevices(all)
            } catch {
                if (!cancelled) setError(t('nav.personnel.push.loadDevicesFailed'))
            } finally {
                if (!cancelled) setIsLoading(false)
            }
        })()
        return () => { cancelled = true }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    const locationGroups = useMemo<LocationGroup[]>(() => {
        const byId = new Map<number, LocationGroup>()
        for (const d of devices) {
            if (d.location_id == null) continue
            let group = byId.get(d.location_id)
            if (!group) {
                group = { id: d.location_id, name: d.location_name ?? `#${d.location_id}`, deviceIds: [] }
                byId.set(d.location_id, group)
            }
            group.deviceIds.push(d.id)
        }
        return Array.from(byId.values()).sort((a, b) => a.name.localeCompare(b.name))
    }, [devices])

    const query = search.trim().toLowerCase()

    const visibleDevices = useMemo(() => {
        if (!query) return devices
        return devices.filter((d) =>
            d.device_name.toLowerCase().includes(query) || d.ip_address.toLowerCase().includes(query))
    }, [devices, query])

    const visibleLocations = useMemo(() => {
        if (!query) return locationGroups
        return locationGroups.filter((g) => g.name.toLowerCase().includes(query))
    }, [locationGroups, query])

    const visibleDeviceIds = useMemo(() => (
        mode === 'device'
            ? visibleDevices.map((d) => d.id)
            : visibleLocations.flatMap((g) => g.deviceIds)
    ), [mode, visibleDevices, visibleLocations])

    // Per-device aggregation of push results across all persons
    const deviceAgg = useMemo(() => {
        const agg = new Map<number, { ok: number; attempts: number; lastMsg: string | null }>()
        for (const outcome of outcomes ?? []) {
            for (const r of outcome.response?.results ?? []) {
                const entry = agg.get(r.device_id) ?? { ok: 0, attempts: 0, lastMsg: null }
                entry.attempts += 1
                if (r.success) entry.ok += 1
                else entry.lastMsg = r.msg ?? r.code ?? null
                agg.set(r.device_id, entry)
            }
        }
        return agg
    }, [outcomes])

    const toggleDevice = (id: number) => {
        setSelected((prev) => {
            const next = new Set(prev)
            if (next.has(id)) next.delete(id)
            else next.add(id)
            return next
        })
    }

    const toggleLocation = (group: LocationGroup) => {
        setSelected((prev) => {
            const next = new Set(prev)
            const allSelected = group.deviceIds.every((id) => next.has(id))
            for (const id of group.deviceIds) {
                if (allSelected) next.delete(id)
                else next.add(id)
            }
            return next
        })
    }

    const allVisibleSelected = visibleDeviceIds.length > 0 && visibleDeviceIds.every((id) => selected.has(id))

    const toggleAll = () => {
        setSelected((prev) => {
            const next = new Set(prev)
            for (const id of visibleDeviceIds) {
                if (allVisibleSelected) next.delete(id)
                else next.add(id)
            }
            return next
        })
    }

    const switchMode = (next: SelectMode) => {
        if (next === mode) return
        setMode(next)
        setSearch('')
    }

    const applySnapshot = (s: PushJobSnapshot) => {
        lastSnapshotRef.current = s
        const personsById = new Map(persons.map((p) => [p.id, p]))
        // Workers run in parallel, so "current" is really the next unresolved person
        const resolved = new Set(s.results.map((r) => r.personnel_id))
        const nextPending = persons.find((p) => !resolved.has(p.id))
        setProgress({ done: s.done, total: s.total, currentName: nextPending?.full_name ?? '' })

        const outcomes: PersonPushOutcome[] = []
        for (const r of s.results) {
            const person = personsById.get(r.personnel_id)
            if (!person) continue
            outcomes.push({
                person,
                ok: r.ok,
                response: r.error ? undefined : {
                    personnel_id: r.personnel_id,
                    person_id_device: '',
                    pushed: r.pushed,
                    failed: r.failed,
                    results: r.results,
                },
                errorMsg: r.error?.message,
            })
        }
        outcomesRef.current = outcomes
        setOutcomes(outcomes)
    }

    const handlePush = async () => {
        if (selected.size === 0 || isPushing) return
        setIsPushing(true)
        setError(null)
        setOutcomes(null)
        outcomesRef.current = []
        lastSnapshotRef.current = null
        const total = persons.length

        try {
            const res = await client.post({
                url: '/api/v1/personnel/push-bulk',
                body: {
                    personnel_ids: persons.map((p) => p.id),
                    device_ids: Array.from(selected),
                    include_photo: includePhoto,
                },
                headers: { 'Content-Type': 'application/json' },
            })
            throwIfError(res.error)
            const data = (res.data as { data?: { job_id: string; total: number } })?.data
            if (!data) throw new Error('Empty response')
            jobIdRef.current = data.job_id

            const abort = new AbortController()
            abortRef.current = abort
            await subscribeToPushJob(data.job_id, { onSnapshot: applySnapshot, signal: abort.signal })
        } catch (err) {
            if (abortRef.current?.signal.aborted) return // modal unmounted mid-job
            if (err instanceof PushJobLostError) {
                // Job vanished server-side (restart/prune) — flag unresolved persons
                const resolved = new Set(outcomesRef.current.map((o) => o.person.id))
                for (const person of persons) {
                    if (!resolved.has(person.id)) {
                        outcomesRef.current.push({ person, ok: false, errorMsg: err.message })
                    }
                }
                setOutcomes([...outcomesRef.current])
            }
            setError(err instanceof Error ? err.message : 'Push failed')
        }

        setProgress(null)
        setIsPushing(false)
        jobIdRef.current = null
        onPushed?.(outcomesRef.current)

        // TS narrows the ref to null from the reset above; the subscribe callback mutates it
        const finalSnapshot = lastSnapshotRef.current as PushJobSnapshot | null
        if (finalSnapshot) {
            const okCount = outcomesRef.current.filter((o) => o.ok).length
            if (finalSnapshot.status === 'cancelled') {
                useToastStore.getState().push({
                    variant: 'error',
                    title: `${t('nav.personnel.push.stopped')}: ${okCount}/${total}`,
                })
            } else if (okCount === total) {
                useToastStore.getState().push({ variant: 'success', title: t('nav.personnel.push.successToast') })
            } else {
                useToastStore.getState().push({
                    variant: 'error',
                    title: `${t('nav.personnel.push.partialToast')}: ${okCount}/${total}`,
                })
            }
        }
    }

    const handleCancel = () => {
        if (isPushing) {
            if (jobIdRef.current) {
                client.post({
                    url: `/api/v1/personnel/push-jobs/${jobIdRef.current}/cancel`,
                    ...silent(),
                }).catch(() => {})
            }
        } else {
            onClose()
        }
    }

    const renderResultBadge = (ok: number, attempts: number) => {
        if (attempts === 0) return null
        if (ok === attempts) {
            return <HiOutlineCheckCircle className="text-[16px] shrink-0" style={{ color: 'var(--success)' }} />
        }
        return (
            <span className="flex items-center gap-1 shrink-0">
                {attempts > 1 && (
                    <span className="text-xs" dir="ltr" style={{ color: 'var(--danger)' }}>{ok}/{attempts}</span>
                )}
                <HiOutlineXCircle className="text-[16px]" style={{ color: 'var(--danger)' }} />
            </span>
        )
    }

    return (
        <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => { if (!isPushing) onClose() }}
        >
            <div
                className="bg-surface rounded-2xl border border-bd shadow-elevated w-[90%] max-w-md max-h-[85vh] overflow-hidden flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div
                    className="px-6 py-4 flex items-center gap-2.5 shrink-0"
                    style={{ background: 'linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%)' }}
                >
                    <HiOutlineArrowUpTray className="text-[18px] text-white/80" />
                    <div>
                        <p className="text-[13px] font-bold text-white">{t('nav.personnel.push.title')}</p>
                        <p className="text-[11px] text-white/50 mt-px">
                            {isBulk
                                ? `${persons.length} ${t('nav.personnel.push.personsSelected')}`
                                : `${persons[0].full_name} · ${persons[0].emp_no}`}
                        </p>
                    </div>
                </div>

                {/* Body */}
                <div className="p-6 overflow-y-auto flex-1 flex flex-col gap-4">
                    {isLoading ? (
                        <p className="text-sm text-muted text-center py-6">…</p>
                    ) : devices.length === 0 ? (
                        <p className="text-sm text-muted text-center py-6">{t('nav.personnel.push.noDevices')}</p>
                    ) : (
                        <div className={`flex flex-col gap-4 ${isPushing ? 'pointer-events-none opacity-60' : ''}`}>
                            <div className="flex rounded-lg border border-bd p-0.5 bg-surface-2">
                                {(['location', 'device'] as const).map((m) => (
                                    <button
                                        key={m}
                                        type="button"
                                        className={`flex-1 py-1.5 px-3 rounded-md text-xs font-semibold border-none cursor-pointer font-sans transition-colors ${
                                            mode === m ? 'bg-accent text-white' : 'bg-transparent text-secondary hover:text-primary'
                                        }`}
                                        onClick={() => switchMode(m)}
                                    >
                                        {m === 'location' ? t('nav.personnel.push.byLocation') : t('nav.personnel.push.byDevice')}
                                    </button>
                                ))}
                            </div>

                            <SearchBar
                                key={mode}
                                placeholder={mode === 'location' ? t('nav.personnel.push.searchLocations') : t('nav.personnel.push.searchDevices')}
                                onSearch={setSearch}
                            />

                            <div className="flex items-center justify-between">
                                <p className="text-sm font-semibold text-primary">
                                    {mode === 'location' ? t('nav.personnel.push.selectLocations') : t('nav.personnel.push.selectDevices')}
                                </p>
                                <div className="flex items-center gap-2.5">
                                    {selected.size > 0 && (
                                        <span className="text-xs text-muted">
                                            {selected.size} {t('nav.personnel.push.selectedCount')}
                                        </span>
                                    )}
                                    {visibleDeviceIds.length > 0 && (
                                        <button
                                            type="button"
                                            className="text-xs font-semibold text-accent bg-transparent border-none cursor-pointer font-sans hover:opacity-80"
                                            onClick={toggleAll}
                                        >
                                            {allVisibleSelected
                                                ? t('nav.personnel.push.clearAll')
                                                : t('nav.personnel.push.selectAll')}
                                        </button>
                                    )}
                                </div>
                            </div>

                            <div className="flex flex-col gap-1 border border-bd rounded-xl p-2 max-h-56 overflow-y-auto">
                                {mode === 'location' ? (
                                    locationGroups.length === 0 ? (
                                        <p className="text-sm text-muted text-center py-4">{t('nav.personnel.push.noLocations')}</p>
                                    ) : visibleLocations.length === 0 ? (
                                        <p className="text-sm text-muted text-center py-4">{t('nav.personnel.push.noResults')}</p>
                                    ) : (
                                        visibleLocations.map((g) => {
                                            const selectedCount = g.deviceIds.filter((id) => selected.has(id)).length
                                            const allSelected = selectedCount === g.deviceIds.length
                                            let okSum = 0
                                            let attemptSum = 0
                                            for (const id of g.deviceIds) {
                                                const agg = deviceAgg.get(id)
                                                if (agg) { okSum += agg.ok; attemptSum += agg.attempts }
                                            }
                                            return (
                                                <label
                                                    key={g.id}
                                                    className="flex items-center gap-2.5 px-2 py-1.5 rounded-lg hover:bg-surface-2 cursor-pointer"
                                                >
                                                    <input
                                                        type="checkbox"
                                                        checked={allSelected}
                                                        ref={(el) => { if (el) el.indeterminate = selectedCount > 0 && !allSelected }}
                                                        onChange={() => toggleLocation(g)}
                                                        className="accent-[var(--accent)]"
                                                    />
                                                    <span className="text-sm text-primary flex-1 truncate text-start" dir="ltr">{g.name}</span>
                                                    <span className="text-xs text-muted" dir="ltr">({g.deviceIds.length})</span>
                                                    {renderResultBadge(okSum, attemptSum)}
                                                </label>
                                            )
                                        })
                                    )
                                ) : visibleDevices.length === 0 ? (
                                    <p className="text-sm text-muted text-center py-4">{t('nav.personnel.push.noResults')}</p>
                                ) : (
                                    visibleDevices.map((d) => {
                                        const agg = deviceAgg.get(d.id)
                                        return (
                                            <label
                                                key={d.id}
                                                className="flex items-center gap-2.5 px-2 py-1.5 rounded-lg hover:bg-surface-2 cursor-pointer"
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={selected.has(d.id)}
                                                    onChange={() => toggleDevice(d.id)}
                                                    className="accent-[var(--accent)]"
                                                />
                                                <span className="text-sm text-primary flex-1 truncate">{d.device_name}</span>
                                                <span className="text-xs text-muted" dir="ltr">{d.ip_address}</span>
                                                {agg && (
                                                    <span title={agg.lastMsg ?? undefined}>
                                                        {renderResultBadge(agg.ok, agg.attempts)}
                                                    </span>
                                                )}
                                            </label>
                                        )
                                    })
                                )}
                            </div>

                            <label className="flex items-center gap-2.5 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={includePhoto}
                                    onChange={(e) => setIncludePhoto(e.target.checked)}
                                    className="accent-[var(--accent)]"
                                />
                                <span className="text-sm text-primary">{t('nav.personnel.push.includePhoto')}</span>
                            </label>
                        </div>
                    )}

                    {progress && isBulk && (
                        <p className="text-sm text-secondary text-center">
                            {t('nav.personnel.push.pushing')} {progress.done + 1}/{progress.total} — {progress.currentName}
                        </p>
                    )}

                    {outcomes && outcomes.some((o) => !o.ok) && (
                        <div className="flex flex-col gap-2 text-xs text-secondary">
                            {outcomes.filter((o) => !o.ok).map((o) => (
                                <div key={o.person.id} className="flex flex-col gap-0.5">
                                    <p className="font-semibold text-primary">{o.person.full_name} · {o.person.emp_no}</p>
                                    {o.errorMsg ? (
                                        <p>{o.errorMsg}</p>
                                    ) : (
                                        o.response?.results.filter((r) => !r.success).map((r) => (
                                            <p key={r.device_id}>
                                                <span className="font-semibold">{r.device_name ?? `#${r.device_id}`}:</span> {r.msg ?? r.code ?? 'failed'}
                                            </p>
                                        ))
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {error && (
                        <div className="flex items-start gap-2 px-3 py-2.5 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
                            <HiOutlineExclamationCircle className="text-[16px] shrink-0 mt-px" />
                            <span>{error}</span>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-bd bg-surface-2 flex justify-end gap-2 shrink-0">
                    <button
                        type="button"
                        className="py-2 px-4 rounded-lg text-sm font-medium text-secondary border border-bd bg-surface hover:bg-surface-2 transition-colors cursor-pointer font-sans"
                        onClick={handleCancel}
                    >
                        {t('common.cancel')}
                    </button>
                    <button
                        type="button"
                        disabled={selected.size === 0 || isPushing}
                        className="py-2 px-4 rounded-lg text-sm font-semibold bg-accent text-white hover:opacity-90 transition-opacity border-none cursor-pointer font-sans disabled:opacity-50 disabled:cursor-not-allowed"
                        onClick={handlePush}
                    >
                        {isPushing && isBulk && progress
                            ? `${t('nav.personnel.push.pushing')} ${progress.done + 1}/${progress.total}`
                            : isPushing
                                ? t('nav.personnel.push.pushing')
                                : t('nav.personnel.push.submit')}
                    </button>
                </div>
            </div>
        </div>
    )
}
