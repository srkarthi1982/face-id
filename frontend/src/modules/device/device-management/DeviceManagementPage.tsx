import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import {
    HiOutlinePencilSquare,
    HiOutlineTrash,
    HiMiniChevronUpDown,
    HiOutlineChevronUp,
    HiOutlineChevronDown,
    HiOutlineArrowPath,
    HiOutlinePlus,
} from 'react-icons/hi2'
import { useI18n } from '../../../infra/locales/I18nContext'
import {
    listDevices,
    editDevice,
    removeDevice,
    refreshDevice,
    scanDevices,
    saveDevice,
} from '../api'
import type { DeviceResponse, DiscoveredDevice } from '../../../api/generated'
import SearchBar from '../../../infra/shared/components/SearchBar'
import SectionHeader from '../../../infra/shared/components/SectionHeader'
import Paginator2 from '../../../infra/shared/components/Paginator2'
import { SearchableCombobox } from '../../../infra/shared/components/SearchableCombobox'
import { getLocationsByType } from '../../master/api'
import type { LocationType } from '../../master/types'

interface EditForm {
    device_name: string
    ip_address: string
    location_id?: number | null
    serial_number?: string
    firmware_version?: string
}

type ModalStep = 'list' | 'manual' | 'discover'

function DeviceModal({
    initial,
    onClose,
    onSave,
    titleNew,
    titleEdit,
    titleSave,
    titleSaving,
    closeOnBackdropClick = false,
}: {
    initial?: EditForm
    onClose: () => void
    onSave: (form: EditForm) => Promise<void>
    titleNew: string
    titleEdit: string
    titleSave: string
    titleSaving: string
    closeOnBackdropClick?: boolean
}) {
    const { t } = useI18n()
    const [form, setForm] = useState<EditForm>(
        initial ?? { device_name: '', ip_address: '', location_id: null, serial_number: '', firmware_version: '' },
    )
    const [submitting, setSubmitting] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [locationOptions, setLocationOptions] = useState<Array<{ id: number; value: string }>>([])
    const [selectedLocation, setSelectedLocation] = useState<{ id: string | number; value: string } | null>(null)

    const formatLocationPath = (path: string): string => {
        if (!path || path === '/') return '';
        const parts = path.split('/').filter(p => p);
        // Skip emirate (first element) if we have more than 1 level
        if (parts.length > 1) {
            return parts.slice(1).join(' - ');
        }
        return parts.join(' - ');
    };

    useEffect(() => {
        // Initialize selectedLocation from initial prop immediately
        if (initial?.location_id) {
            setForm(prev => ({ ...prev, location_id: initial.location_id }))
        }
        
        const loadLocations = async () => {
            const types: LocationType[] = ['building', 'area', 'location']
            const allLocations: Array<{ id: number; value: string }> = []
            
            for (const type of types) {
                try {
                    const { data } = await getLocationsByType(type)
                    if (data) {
                        data.forEach(loc => {
                            allLocations.push({
                                id: loc.id,
                                value: formatLocationPath(loc.path),
                            })
                        })
                    }
                } catch (e) {
                    console.error(`Failed to load locations of type ${type}:`, e)
                }
            }
            
            // Sort alphabetically by value
            allLocations.sort((a, b) => a.value.localeCompare(b.value))
            setLocationOptions(allLocations)
            
            // Set selected location display when locations are loaded
            if (initial?.location_id) {
                const existingLocation = allLocations.find(loc => loc.id === initial.location_id)
                if (existingLocation) {
                    setSelectedLocation(existingLocation)
                }
            }
        }
        
        loadLocations()
    }, [initial])

    const updateField =
        (field: keyof EditForm) => (e: React.ChangeEvent<HTMLInputElement>) =>
            setForm((prev) => ({ ...prev, [field]: e.target.value }))

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()
        setError(null)
        setSubmitting(true)
        try {
            await onSave(form)
            onClose()
        } catch (err: unknown) {
            setError((err as { message?: string }).message || 'Failed to save device')
        } finally {
            setSubmitting(false)
        }
    }

    useEffect(() => {
        const handleEsc = (e: KeyboardEvent) => {
            if (e.key === 'Escape' && closeOnBackdropClick) {
                e.preventDefault()
                onClose()
            }
        }
        document.addEventListener('keydown', handleEsc)
        return () => document.removeEventListener('keydown', handleEsc)
    }, [closeOnBackdropClick, onClose])

    const inputClass =
        'w-full px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20'

    return (
        <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={closeOnBackdropClick ? onClose : undefined}
        >
            <div
                className="bg-surface rounded-2xl border border-bd shadow-elevated w-full max-w-xl overflow-hidden flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                <div
                    className="px-6 py-4 flex items-center justify-between shrink-0"
                    style={{ background: 'linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%)' }}
                >
                    <div>
                        <p className="text-[13px] font-bold text-white">
                            {initial ? titleEdit : titleNew}
                        </p>
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        className="text-white/50 hover:text-white text-xl leading-none border-none bg-transparent cursor-pointer"
                    >
                        &times;
                    </button>
                </div>

                <div className="p-6 overflow-y-auto flex-1 max-h-[75vh]">
                    <form id="device-form" onSubmit={handleSubmit} className="flex flex-col gap-4">
                        <div>
                            <label htmlFor="modal-device-name" className="block text-sm font-medium text-secondary mb-1">{t('nav.device.devices.deviceName')}</label>
                            <input id="modal-device-name" type="text" value={form.device_name} onChange={updateField('device_name')} required
                                   className={inputClass} />
                        </div>
                        <div>
                            <label htmlFor="modal-location" className="block text-sm font-medium text-secondary mb-1">{t('nav.device.devices.location')}</label>
                            <SearchableCombobox
                                key={selectedLocation?.id || 'none'}
                                options={locationOptions}
                                placeholder="Select location..."
                                selected={selectedLocation}
                                onChange={(selected) => {
                                    setSelectedLocation(selected)
                                    setForm((prev) => ({ ...prev, location_id: selected ? Number(selected.id) : null }))
                                }}
                                className="w-full"
                            />
                        </div>
                        <div>
                            <label htmlFor="modal-ip-address" className="block text-sm font-medium text-secondary mb-1">{t('nav.device.devices.ipAddress')}</label>
                            <input id="modal-ip-address" type="text" value={form.ip_address} disabled
                                   className={`${inputClass} bg-surface-2 cursor-not-allowed opacity-60`} />
                        </div>
                        <div>
                            <label htmlFor="modal-serial-number" className="block text-sm font-medium text-secondary mb-1">Serial Number</label>
                            <input id="modal-serial-number" type="text" value={form.serial_number || ''} disabled
                                   className={`${inputClass} bg-surface-2 cursor-not-allowed opacity-60`} />
                        </div>
                        <div>
                            <label htmlFor="modal-firmware-version" className="block text-sm font-medium text-secondary mb-1">Firmware Version</label>
                            <input id="modal-firmware-version" type="text" value={form.firmware_version || ''} disabled
                                   className={`${inputClass} bg-surface-2 cursor-not-allowed opacity-60`} />
                        </div>

                        {error && (
                            <div className="flex items-start gap-2 px-3 py-2.5 rounded-lg bg-red-500/10 border border-red-500/20">
                                <p className="text-sm text-red-500">{error}</p>
                            </div>
                        )}
                    </form>
                </div>

                <div className="px-6 py-4 flex justify-end gap-2 border-t border-bd shrink-0">
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-2 rounded-[9px] text-sm font-semibold text-secondary bg-surface-2 border border-bd hover:bg-surface transition-colors cursor-pointer font-sans"
                    >
                        {t('common.cancel')}
                    </button>
                    <button
                        type="submit"
                        form="device-form"
                        disabled={submitting}
                        className="px-4 py-2 rounded-[9px] text-sm font-semibold text-white bg-accent hover:opacity-90 transition-opacity border-none cursor-pointer font-sans disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {submitting ? titleSaving : titleSave}
                    </button>
                </div>
            </div>
        </div>
    )
}

type SortKey = 'id' | 'device_name' | 'ip_address' | 'serial_number' | 'location_name' | 'status'

export default function DeviceManagementPage() {
    const { t } = useI18n()
    const [devices, setDevices] = useState<DeviceResponse[]>([])
    const [loading, setLoading] = useState(true)
    const [totalPages, setTotalPages] = useState(1)
    const [total, setTotal] = useState(0)
    const [page, setPage] = useState(0)
    const [searchText, setSearchText] = useState('')
    const [filterState, setFilterState] = useState<string>('')
    const [editingDevice, setEditingDevice] = useState<{ item: DeviceResponse; form: EditForm } | null>(null)
    const [confirmDelete, setConfirmDelete] = useState<number | null>(null)
    const [listKey, setListKey] = useState(0)
    const [sortKey, setSortKey] = useState<SortKey>('device_name')
    const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')
    const [refreshingId, setRefreshingId] = useState<number | null>(null)
    const [showAddMenu, setShowAddMenu] = useState(false)
    const [addStep, setAddStep] = useState<ModalStep>('list')
    const [savingDevice, setSavingDevice] = useState(false)
    const [isDiscovering, setIsDiscovering] = useState(false)
    const [discoveredDevices, setDiscoveredDevices] = useState<DiscoveredDevice[]>([])
    const [subnetInput, setSubnetInput] = useState('192.168.1.0/24')
    const [successMessage, setSuccessMessage] = useState<string | null>(null)
    const [errorMessage, setErrorMessage] = useState<string | null>(null)
    const [manualLocationOptions, setManualLocationOptions] = useState<Array<{ id: number; value: string }>>([])
    const [manualSelectedLocation, setManualSelectedLocation] = useState<{ id: string | number; value: string } | null>(null)
    const modalCloseTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
    const abortControllerRef = useRef<AbortController | null>(null)

    const PAGE_SIZE = 10

    const formatLocationPath = (path: string): string => {
        if (!path || path === '/') return '';
        const parts = path.split('/').filter(p => p);
        if (parts.length > 1) {
            return parts.slice(1).join(' - ');
        }
        return parts.join(' - ');
    };

    useEffect(() => {
        if (addStep !== 'manual') {
            setManualLocationOptions([])
            setManualSelectedLocation(null)
            return
        }
        
        const loadLocations = async () => {
            const types: LocationType[] = ['building', 'area', 'location']
            const allLocations: Array<{ id: number; value: string }> = []
            
            for (const type of types) {
                try {
                    const { data } = await getLocationsByType(type)
                    if (data) {
                        data.forEach(loc => {
                            allLocations.push({
                                id: loc.id,
                                value: formatLocationPath(loc.path),
                            })
                        })
                    }
                } catch (e) {
                    console.error(`Failed to load locations of type ${type}:`, e)
                }
            }
            
            allLocations.sort((a, b) => a.value.localeCompare(b.value))
            setManualLocationOptions(allLocations)
        }
        
        loadLocations()
    }, [addStep])

    const toggleSort = useCallback((col: SortKey) => {
        if (sortKey === col) {
            setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
        } else {
            setSortKey(col)
            setSortDir('asc')
        }
    }, [sortKey])

    const SortIcon = ({ col }: { col: SortKey }) => {
        if (sortKey !== col) return <HiMiniChevronUpDown className="text-[14px] text-muted opacity-50" />
        return sortDir === 'asc' ? <HiOutlineChevronUp className="text-[12px] text-accent" /> : <HiOutlineChevronDown className="text-[12px] text-accent" />
    }

    useEffect(() => {
        let cancelled = false
        const load = async () => {
            setLoading(true)
            try {
                const res = await listDevices({ page: page + 1, page_size: PAGE_SIZE, search_text: searchText, status: filterState || undefined })
                if (cancelled) return
                setDevices(res.data)
                setTotal(Number(res.meta.total))
                setTotalPages(Number(res.meta.pages))
                setTimeout(() => {
                    setSuccessMessage(null)
                    setErrorMessage(null)
                }, 5000)
            } catch (err: unknown) {
                if (!cancelled) console.error(err)
            } finally {
                if (!cancelled) setLoading(false)
            }
        }
        load()
        return () => { cancelled = true }
    }, [page, searchText, filterState, PAGE_SIZE, listKey])

    const forceRefresh = useCallback(() => {
        setListKey(k => k + 1)
    }, [])

    const sortedDevices = useMemo(() => {
        return [...devices].sort((a, b) => {
            const cmp = String((a as any)[sortKey] ?? '').localeCompare(String((b as any)[sortKey] ?? ''))
            return sortDir === 'asc' ? cmp : -cmp
        })
    }, [devices, sortKey, sortDir])

    const handleEditSave = async (form: EditForm) => {
        if (!editingDevice) return
        await editDevice(editingDevice.item.id, form)
        setEditingDevice(null)
        forceRefresh()
    }

    const handleDelete = async (id: number) => {
        try {
            await removeDevice(id)
        } catch (err: unknown) {
            console.error('Delete failed:', err)
        } finally {
            setConfirmDelete(null)
            forceRefresh()
        }
    }

    const handleRefresh = async (id: number, e: React.MouseEvent) => {
        e.stopPropagation()
        setRefreshingId(id)
        try {
            const updated = await refreshDevice(id)
            setDevices(prev => prev.map(d => d.id === id ? updated : d))
        } catch (err) {
            console.error(err)
        } finally {
            setRefreshingId(null)
            setListKey(k => k + 1)
        }
    }

    const showSuccess = (msg: string) => {
        setSuccessMessage(msg)
        setErrorMessage(null)
    }

    const showError = (msg: string) => {
        setErrorMessage(msg)
        setSuccessMessage(null)
    }

    const openAddManual = () => {
        setAddStep('manual')
        setErrorMessage(null)
        setSuccessMessage(null)
        setShowAddMenu(false)
    }

    const openAddDiscover = () => {
        setSubnetInput('192.168.1.0/24')
        setAddStep('discover')
        setErrorMessage(null)
        setSuccessMessage(null)
        setShowAddMenu(false)
        setDiscoveredDevices([])
    }

    const [selectedDevices, setSelectedDevices] = useState<Set<string>>(new Set())

    const toggleSelection = (ip: string) => {
        setSelectedDevices(prev => {
            const next = new Set(prev)
            if (next.has(ip)) {
                next.delete(ip)
            } else {
                next.add(ip)
            }
            return next
        })
    }

    const selectAll = () => {
        if (selectedDevices.size === discoveredDevices.length) {
            setSelectedDevices(new Set())
        } else {
            setSelectedDevices(new Set(discoveredDevices.map(d => d.ip_address)))
        }
    }

    const handleBulkConnect = async () => {
        if (selectedDevices.size === 0) return
        setSavingDevice(true)
        setErrorMessage(null)
        setSuccessMessage(null)
        const selected = discoveredDevices.filter(d => selectedDevices.has(d.ip_address))
        for (const device of selected) {
            try {
                const res = await saveDevice({
                    device_name: device.device_name,
                    ip_address: device.ip_address,
                    location_id: null,
                    serial_number: device.serial_number || undefined,
                    firmware_version: device.firmware_version || undefined,
                })
                showSuccess(res.message)
                await waitForAndRefreshDevice(device.device_name, device.ip_address)
            } catch (err: unknown) {
                showError((err as { message?: string }).message || `Failed to connect ${device.ip_address}`)
                break
            }
        }
        setSavingDevice(false)
        setAddStep('list')
    }

    const closeModal = () => {
        if (modalCloseTimerRef.current) clearTimeout(modalCloseTimerRef.current)
        setAddStep('list')
        setErrorMessage(null)
        setSuccessMessage(null)
    }

    /**
     * After saveDevice() which returns only { message } (no device back),
     * poll listDevices (no filters) until the new device appears, call
     * refreshDevice(id), then reload the table.
     */
    const waitForAndRefreshDevice = useCallback(
        async (expectedName: string, expectedIp: string) => {
            let found: DeviceResponse | undefined
            for (let attempt = 0; attempt < 6; attempt++) {
                await new Promise(resolve => setTimeout(resolve, 1000))
                try {
                    const res = await listDevices({ page: 1, page_size: 100 })
                    found = res.data.find(
                        d => d.device_name === expectedName && d.ip_address === expectedIp,
                    )
                    if (found?.id) break
                } catch {
                    // ignore
                }
            }
            if (found?.id) {
                try {
                    await refreshDevice(found.id)
                } catch {
                    // ignore — table reload will happen anyway
                }
            }
            setListKey(k => k + 1)
        },
        [],
    )

    const handleManualSubmit = async (e: FormEvent) => {
        e.preventDefault()
        const formData = new FormData(e.target as HTMLFormElement)
        const deviceName = formData.get('device_name') as string
        const ipAddress = formData.get('ip_address') as string
        const locationId = manualSelectedLocation ? Number(manualSelectedLocation.id) : null
        setSavingDevice(true)
        setErrorMessage(null)
        setSuccessMessage(null)
        try {
            const res = await saveDevice({ device_name: deviceName, ip_address: ipAddress, location_id: locationId, serial_number: null, firmware_version: null })
            showSuccess(res.message)
            await waitForAndRefreshDevice(deviceName, ipAddress)
            setAddStep('list')
        } catch (err: unknown) {
            showError((err as { message?: string }).message || 'Failed to connect device')
        } finally {
            setSavingDevice(false)
        }
    }

    const startDiscover = async (subnet?: string) => {
        const controller = new AbortController()
        abortControllerRef.current = controller
        setIsDiscovering(true)
        setDiscoveredDevices([])
        setErrorMessage(null)
        setSuccessMessage(null)
        try {
            const res = await scanDevices({ subnet: subnet || subnetInput }, controller.signal)
            setDiscoveredDevices(res.devices)
        } catch (err: unknown) {
            if (err instanceof Error && (err.name === 'AbortError' || err.message.includes('abort'))) {
                // cancelled — don't show error
            } else {
                showError((err as { message?: string }).message || 'Failed to discover devices')
            }
        } finally {
            setIsDiscovering(false)
            if (abortControllerRef.current === controller) {
                abortControllerRef.current = null
            }
        }
    }

    const stopDiscover = () => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort()
        }
    }

    const handleConnectDiscovered = async (device: DiscoveredDevice) => {
        setSavingDevice(true)
        setErrorMessage(null)
        setSuccessMessage(null)
        try {
            const res = await saveDevice({
                device_name: device.device_name,
                ip_address: device.ip_address,
                location_id: null,
                serial_number: device.serial_number || undefined,
                firmware_version: device.firmware_version || undefined,
            })
            showSuccess(res.message)
            await waitForAndRefreshDevice(device.device_name, device.ip_address)
            setAddStep('list')
        } catch (err: unknown) {
            showError((err as { message?: string }).message || 'Failed to connect device')
        } finally {
            setSavingDevice(false)
        }
    }

    const inputClass =
        'w-full px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20'

    return (
        <div className='flex flex-col gap-5 overflow-hidden h-[100%]'>
            <SectionHeader
                eyebrow={t('common.management')}
                title={t('nav.device.devices.title')}
                description={t('nav.device.devices.description')}
                actions={
                    <div className="relative">
                        <button
                            onClick={() => setShowAddMenu(!showAddMenu)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-[9px] text-sm font-semibold text-white bg-accent hover:opacity-90 transition-opacity border-none cursor-pointer font-sans"
                        >
                            <HiOutlinePlus className="text-[14px]" />
                            {t('nav.device.devices.addDevice')}
                        </button>
                        {showAddMenu && (
                            <>
                                <div className="fixed inset-0 z-10" onClick={() => setShowAddMenu(false)} />
                                <div className="absolute right-0 top-full mt-2 w-56 bg-surface border border-bd rounded-xl shadow-elevated z-20 overflow-hidden">
                                    <button
                                        onClick={openAddManual}
                                        className="w-full px-4 py-3 text-left text-sm text-primary hover:bg-surface-2 transition-colors flex items-center gap-3"
                                    >
                                        <svg className="w-5 h-5 text-accent shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                        </svg>
                                        {t('nav.device.devices.manualSetup')}
                                    </button>
                                    <button
                                        onClick={openAddDiscover}
                                        className="w-full px-4 py-3 text-left text-sm text-primary hover:bg-surface-2 transition-colors flex items-center gap-3"
                                    >
                                        <svg className="w-5 h-5 text-accent shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                                        </svg>
                                        {t('nav.device.devices.autoDiscover')}
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                }
            />

            <div className='flex flex-col gap-2 overflow-auto h-full'>
                <div className='flex gap-2 items-center'>
                    <SearchBar onSearch={(v) => setSearchText(v)} />
                    <select value={filterState} onChange={(e) => setFilterState(e.target.value)}
                            className="h-9 px-3 rounded-[9px] bg-[var(--surface-2)] border border-[var(--border)] text-text-primary text-3.4 font-sans outline-none focus:border-[var(--accent)] transition-[border-color] duration-150">
                        <option value="">All Statuses</option>
                        <option value="online">Online</option>
                        <option value="offline">Offline</option>
                        <option value="unknown">Unknown</option>
                    </select>
                </div>

                <div className="card p-0 h-full overflow-auto">
                    {loading && (
                        <div className="flex items-center justify-center py-12">
                            <p className="text-sm text-muted">Loading…</p>
                        </div>
                    )}
                    {!loading && (
                        <div className="overflow-auto">
                            <table className="w-full border-collapse">
                                <thead>
                                <tr className="border-b border-bd" style={{ background: 'var(--navy)' }}>
                                    {[
                                        { key: 'device_name' as SortKey, label: 'Device Name' },
                                        { key: 'ip_address' as SortKey, label: 'IP Address' },
                                        { key: 'serial_number' as SortKey, label: 'Serial Number' },
                                        { key: 'location_name' as SortKey, label: 'Location' },
                                        { key: 'status' as SortKey, label: 'Status' },
                                    ].map((col) => (
                                        <th key={`header-${col.key}`}
                                            className="px-4 py-3 text-[11px] font-bold text-white/60 tracking-[0.06em] uppercase">
                                            <button onClick={() => toggleSort(col.key)}
                                                    className="flex items-center gap-1 hover:text-white transition-colors uppercase">
                                                {col.label}
                                                <SortIcon col={col.key} />
                                            </button>
                                        </th>
                                    ))}
                                    <th key={'actions'}
                                        className="px-4 py-3 text-center text-[11px] font-bold text-white/60 uppercase tracking-[0.06em]">
                                        Actions
                                    </th>
                                </tr>
                                </thead>
                                <tbody className="divide-y divide-bd">
                                {sortedDevices.map((d) => (
                                    <tr key={d.id} className="hover:bg-surface-2 transition-colors duration-100">
                                        <td className="px-4 py-3 text-sm font-semibold text-primary">{d.device_name}</td>
                                        <td className="px-4 py-3 text-sm text-secondary">{d.ip_address}</td>
                                        <td className="px-4 py-3 text-sm text-secondary">{d.serial_number || '�'}</td>
                                        <td className="px-4 py-3 text-sm text-secondary">{d.location_name || ''}</td>
                                        <td className="px-4 py-3">
                                            <span
                                                className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold"
                                                style={{
                                                    background: d.status === 'online' ? 'rgba(34,197,94,0.1)' : 'rgba(220,38,38,0.1)',
                                                    color: d.status === 'online' ? '#16A34A' : '#DC2626',
                                                }}
                                            >
                                                <span className="w-1.5 h-1.5 rounded-full" style={{ background: d.status === 'online' ? '#16A34A' : '#DC2626' }} />
                                                {d.status === 'online' ? 'Online' : 'Offline'}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex gap-2 justify-center">
                                                <button
                                                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-[7px] text-xs font-semibold bg-blue-500 text-white hover:opacity-90 transition-opacity border-none cursor-pointer font-sans"
                                                    onClick={(e) => handleRefresh(d.id, e)}
                                                    disabled={refreshingId === d.id}
                                                    title={t('nav.device.devices.refreshStatus')}
                                                >
                                                    <HiOutlineArrowPath className={`text-[13px] ${refreshingId === d.id ? 'animate-spin' : ''}`} />
                                                    {t('nav.device.devices.refresh')}
                                                </button>
                                                <button
                                                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-[7px] text-xs font-semibold bg-accent text-white hover:opacity-90 transition-opacity border-none cursor-pointer font-sans"
                                                    onClick={() => setEditingDevice({ item: d, form: { device_name: d.device_name, ip_address: d.ip_address, location_id: d.location_id ?? undefined, serial_number: d.serial_number ?? undefined, firmware_version: d.firmware_version ?? undefined } })}
                                                >
                                                    <HiOutlinePencilSquare className="text-[13px]" />
                                                    {t('common.edit')}
                                                </button>
                                                <button
                                                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-[7px] text-xs font-semibold bg-red-500 text-white hover:opacity-90 transition-opacity border-none cursor-pointer font-sans"
                                                    onClick={() => setConfirmDelete(d.id)}
                                                >
                                                    <HiOutlineTrash className="text-[13px]" />
                                                    {t('common.delete')}
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                                {sortedDevices.length === 0 && (
                                    <tr>
                                        <td colSpan={5}>
                                            <div className="flex flex-col items-center justify-center text-center px-6 py-12">
                                                <span className="rounded-2xl flex items-center justify-center shrink-0 w-16 h-16 text-[30px] mb-4"
                                                      style={{ background: 'var(--accent-light)', color: 'var(--accent)' }}>✦</span>
                                                <p className="text-[16px] font-semibold text-primary">{t('nav.device.devices.noDevices')}</p>
                                                <p className="text-xs text-secondary mt-2">{t('nav.device.devices.description')}</p>
                                            </div>
                                        </td>
                                    </tr>
                                )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            <div className="shrink-0">
                <Paginator2 page={page} totalPages={totalPages} onPageChanged={setPage} dataLength={total}
                            pageSize={PAGE_SIZE} />
            </div>

            {editingDevice && (
                <DeviceModal
                    initial={editingDevice.form}
                    onClose={() => setEditingDevice(null)}
                    onSave={handleEditSave}
                    titleEdit={t('nav.device.devices.editDevice')}
                    titleNew={t('nav.device.devices.editDevice')}
                    titleSave={t('nav.device.devices.saveChanges')}
                    titleSaving={t('nav.device.devices.saving')}
                />
            )}
            {confirmDelete && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={undefined}>
                    <div className="bg-surface rounded-2xl border border-bd shadow-elevated w-full max-w-sm overflow-hidden"
                         onClick={(e) => e.stopPropagation()}>
                        <div className="p-6 text-center">
                            <p className="text-sm font-bold text-primary mb-2">{t('nav.device.devices.confirmDelete')}</p>
                            <p className="text-sm text-secondary mb-6">{t('nav.device.devices.confirmDeleteMessage')}</p>
                            <div className="flex justify-center gap-2">
                                <button
                                    onClick={() => setConfirmDelete(null)}
                                    className="px-4 py-2 rounded-[9px] text-sm font-semibold text-secondary bg-surface-2 border border-bd hover:bg-surface transition-colors cursor-pointer font-sans"
                                >
                                    {t('common.cancel')}
                                </button>
                                <button
                                    onClick={() => handleDelete(confirmDelete)}
                                    className="px-4 py-2 rounded-[9px] text-sm font-semibold text-white bg-red-500 hover:opacity-90 transition-opacity border-none cursor-pointer font-sans"
                                >
                                    {t('common.delete')}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {addStep !== 'list' && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={undefined}>
                    <div
                        className="bg-surface rounded-2xl border border-bd shadow-elevated w-full max-w-2xl overflow-hidden flex flex-col mx-4"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div
                            className="px-6 py-3 flex items-center justify-between shrink-0"
                            style={{ background: 'linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%)' }}
                        >
                            <p className="text-[13px] font-bold text-white">
                                {addStep === 'manual' ? t('nav.device.devices.manualSetup') : t('nav.device.devices.discoveredDevices')}
                            </p>
                            <button
                                type="button"
                                onClick={closeModal}
                                className="text-white/50 hover:text-white text-xl leading-none border-none bg-transparent cursor-pointer"
                            >
                                &times;
                            </button>
                        </div>
                <div className="p-6 overflow-y-auto flex-1 max-h-[70vh]">
                    {addStep === 'manual' && (
                        <form onSubmit={handleManualSubmit} className="flex flex-col gap-4">
                                    <div>
                                        <label htmlFor="setup-device-name" className="block text-sm font-medium text-secondary mb-1">{t('nav.device.devices.deviceName')}</label>
                                        <input id="setup-device-name" name="device_name" type="text" required className="w-full px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20" />
                                    </div>
                                    <div>
                                        <label htmlFor="setup-ip-address" className="block text-sm font-medium text-secondary mb-1">{t('nav.device.devices.ipAddress')}</label>
                                        <input id="setup-ip-address" name="ip_address" type="text" required className="w-full px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20" />
                                    </div>
                                    <div>
                                        <label htmlFor="setup-location" className="block text-sm font-medium text-secondary mb-1">{t('nav.device.devices.location')}</label>
                                        <SearchableCombobox
                                            key={manualSelectedLocation?.id || 'none'}
                                            options={manualLocationOptions}
                                            placeholder="Select location..."
                                            selected={manualSelectedLocation}
                                            onChange={(selected) => {
                                                setManualSelectedLocation(selected)
                                            }}
                                            className="w-full"
                                        />
                                        <input type="hidden" name="location_id" value={manualSelectedLocation?.id ?? ''} />
                                    </div>

                                    {errorMessage && (
                                        <div className="flex items-start gap-2 px-3 py-2.5 rounded-lg bg-red-500/10 border border-red-500/20">
                                            <p className="text-sm text-red-500">{errorMessage}</p>
                                        </div>
                                    )}

                                    {successMessage && (
                                        <div className="flex items-start gap-2 px-3 py-2.5 rounded-lg bg-green-500/10 border border-green-500/20">
                                            <p className="text-sm text-green-600">{successMessage}</p>
                                        </div>
                                    )}

                                    <div className="flex justify-end gap-2 pt-4 mt-2">
                                        <button
                                            type="button"
                                            onClick={closeModal}
                                            className="px-4 py-2 rounded-[9px] text-sm font-semibold text-secondary bg-surface-2 border border-bd hover:bg-surface transition-colors cursor-pointer font-sans"
                                        >
                                            {t('common.cancel')}
                                        </button>
                                        <button
                                            type="submit"
                                            disabled={savingDevice}
                                            className="px-6 py-2 rounded-[9px] text-sm font-semibold text-white bg-accent hover:opacity-90 transition-opacity border-none cursor-pointer font-sans disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            {savingDevice ? t('nav.device.devices.connecting') : t('nav.device.devices.connectDevice')}
                                        </button>
                                    </div>
                                </form>
                            )}

                            {addStep === 'discover' && (
                                <>
                                    <div>
                                        <label htmlFor="subnet-input" className="block text-sm font-medium text-secondary mb-1">Subnet Range</label>
                                        <div className="flex gap-2">
                                            <input id="subnet-input"
                                                type="text"
                                                value={subnetInput}
                                                onChange={(e) => setSubnetInput(e.target.value)}
                                                placeholder="e.g. 192.168.1.0/24"
                                                className="flex-1 px-3 py-2 border border-bd rounded-lg text-sm text-primary bg-surface-2 focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
                                            />
                                            {!isDiscovering ? (
                                                <button
                                                    onClick={() => startDiscover(subnetInput)}
                                                    className="px-4 py-2 rounded-lg text-sm font-semibold text-white bg-accent hover:opacity-90 transition-opacity border-none cursor-pointer"
                                                >
                                                    {t('nav.device.devices.scan')}
                                                </button>
                                            ) : (
                                                <button
                                                    onClick={stopDiscover}
                                                    className="px-4 py-2 rounded-lg text-sm font-semibold text-white bg-red-500 hover:opacity-90 transition-opacity border-none cursor-pointer"
                                                >
                                                    Stop
                                                </button>
                                            )}
                                        </div>
                                    </div>

                                    {isDiscovering && (
                                        <div className="flex items-center justify-center py-12">
                                            <p className="text-sm text-muted">{t('nav.device.devices.discoveringDevices')}</p>
                                        </div>
                                    )}

                                    {!isDiscovering && discoveredDevices.length === 0 && !errorMessage && !successMessage && (
                                        <div className="flex flex-col items-center justify-center text-center px-6 py-12">
                                            <svg className="w-16 h-16 text-accent mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                            </svg>
                                            <p className="text-[16px] font-semibold text-primary">{t('nav.device.devices.noDevicesDiscovered')}</p>
                                        </div>
                                    )}

                                    {errorMessage && (
                                        <div className="flex items-start gap-2 mt-2 px-3 py-2.5 rounded-lg bg-red-500/10 border border-red-500/20">
                                            <p className="text-sm text-red-500">{errorMessage}</p>
                                        </div>
                                    )}

                                    {successMessage && (
                                        <div className="flex items-start gap-2 mt-2 px-3 py-2.5 rounded-lg bg-green-500/10 border border-green-500/20">
                                            <p className="text-sm text-green-600">{successMessage}</p>
                                        </div>
                                    )}

                                    {!isDiscovering && discoveredDevices.length > 0 && (
                                        <div className="overflow-auto mt-4" style={{ maxHeight: '300px' }}>
                                            <table className="w-full border-collapse">
                                                <thead>
                                                <tr className="border-b border-bd" style={{ background: 'var(--navy)' }}>
                                                    <th className="px-4 py-3 text-[11px] font-bold text-white/60 tracking-[0.06em] uppercase text-center">
                                                        <input type="checkbox" checked={selectedDevices.size === discoveredDevices.length && discoveredDevices.length > 0}
                                                            onChange={selectAll} className="w-4 h-4 rounded border-bd text-accent focus:ring-accent cursor-pointer" />
                                                    </th>
                                                    <th className="px-4 py-3 text-[11px] font-bold text-white/60 tracking-[0.06em] uppercase text-center">Device Name</th>
                                                    <th className="px-4 py-3 text-[11px] font-bold text-white/60 tracking-[0.06em] uppercase text-center">IP Address</th>
                                                    <th className="px-4 py-3 text-[11px] font-bold text-white/60 tracking-[0.06em] uppercase text-center">Serial Number</th>
                                                    <th className="px-4 py-3 text-[11px] font-bold text-white/60 tracking-[0.06em] uppercase text-center">Firmware</th>
                                                    <th className="px-4 py-3 text-[11px] font-bold text-white/60 tracking-[0.06em] uppercase text-center">State</th>
                                                </tr>
                                                </thead>
                                                <tbody className="divide-y divide-bd">
                                                {discoveredDevices.map((d) => (
                                                    <tr key={d.ip_address} className="hover:bg-surface-2 transition-colors duration-100">
                                                        <td className="px-4 py-3 text-center">
                                                            <input type="checkbox" checked={selectedDevices.has(d.ip_address)}
                                                                onChange={() => toggleSelection(d.ip_address)}
                                                                className="w-4 h-4 rounded border-bd text-accent focus:ring-accent cursor-pointer" />
                                                        </td>
                                                        <td className="px-4 py-3 text-sm font-semibold text-primary text-center">{d.device_name}</td>
                                                        <td className="px-4 py-3 text-sm text-secondary text-center">{d.ip_address}</td>
                                                        <td className="px-4 py-3 text-sm text-secondary text-center">{d.serial_number ?? '�'}</td>
                                                        <td className="px-4 py-3 text-sm text-secondary text-center">{d.firmware_version ?? '�'}</td>
                                                        <td className="px-4 py-3 text-center">
                                                            <span
                                                                className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold"
                                                                style={{
                                                                    background: d.state === 'online' ? 'rgba(34,197,94,0.1)' : 'rgba(220,38,38,0.1)',
                                                                    color: d.state === 'online' ? '#16A34A' : '#DC2626',
                                                                }}
                                                            >
                                                                <span className="w-1.5 h-1.5 rounded-full" style={{ background: d.state === 'online' ? '#16A34A' : '#DC2626' }} />
                                                                {d.state === 'online' ? 'Online' : 'Offline'}
                                                            </span>
                                                        </td>
                                                    </tr>
                                                ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    )}

                                    {discoveredDevices.length > 0 && (
                                        <div className="mt-4 pt-4 border-t border-bd flex justify-end">
                                            <button
                                                onClick={handleBulkConnect}
                                                disabled={savingDevice || selectedDevices.size === 0}
                                                className="px-4 py-2 rounded-[9px] text-sm font-semibold text-white bg-accent hover:opacity-90 transition-opacity border-none cursor-pointer font-sans disabled:opacity-50 disabled:cursor-not-allowed"
                                            >
                                                {savingDevice ? t('nav.device.devices.connecting') : `Connect (${selectedDevices.size})`}
                                            </button>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

