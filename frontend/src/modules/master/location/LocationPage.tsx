import React, { useCallback, useEffect, useState } from 'react'
import { useShallow } from 'zustand/react/shallow'
import { HiOutlineBuildingOffice2, HiOutlinePlus, HiOutlinePencil, HiOutlineTrash, HiOutlineChevronRight } from 'react-icons/hi2'
import { useI18n } from '../../../infra/locales/I18nContext'
import { useLocationStore } from './store'
import SectionHeader from '../../../infra/shared/components/SectionHeader'
import { CreateLocationChainDialog } from '../../../infra/shared/components/CreateLocationChainDialog'
import type { LocationCreate, LocationUpdate, LocationType, LocationChainItem } from '../types'
import { getValidParentLocations } from '../api'

interface LocationForm {
    name: string
    type: LocationType
    parent_id: number | null
    unit_id: number | null
    sort_order?: number
}

export default function LocationPage() {
    const { t } = useI18n()
    const { treeItems, flatItems, commandUnits, selectedUnitId, isLoading, fetchTree, fetch, create, update, remove, createWithFullChain, fetchCommandUnits, setSelectedUnitId } = useLocationStore(
        useShallow((s) => ({
            treeItems: s.treeItems,
            flatItems: s.flatItems,
            commandUnits: s.commandUnits,
            selectedUnitId: s.selectedUnitId,
            isLoading: s.isLoading,
            fetchTree: s.fetchTree,
            fetch: s.fetch,
            create: s.create,
            update: s.update,
            remove: s.remove,
            createWithFullChain: s.createWithFullChain,
            fetchCommandUnits: s.fetchCommandUnits,
            setSelectedUnitId: s.setSelectedUnitId,
        }))
    )

    const [showModal, setShowModal] = useState(false)
    const [editingId, setEditingId] = useState<number | null>(null)
    const [formData, setFormData] = useState<LocationForm>({
        name: '',
        type: 'location',
        parent_id: null,
        unit_id: null,
    })
    const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [showChainDialog, setShowChainDialog] = useState(false)
    const [parentLocations, setParentLocations] = useState<any[]>([])
    const [selectedType, setSelectedType] = useState<LocationType>('location')
    const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set())

    const emirates = (flatItems?.filter(i => i.type === 'emirate') ?? []).map(l => ({ id: l.id, name: l.name, parent_id: l.parent_id }))
    const bases = (flatItems?.filter(i => i.type === 'base') ?? []).map(l => ({ id: l.id, name: l.name, parent_id: l.parent_id }))
    const locations = (flatItems?.filter(i => i.type === 'location') ?? []).map(l => ({ id: l.id, name: l.name, parent_id: l.parent_id }))
    const buildings = (flatItems?.filter(i => i.type === 'building') ?? []).map(l => ({ id: l.id, name: l.name, parent_id: l.parent_id }))
    const areas = (flatItems?.filter(i => i.type === 'area') ?? []).map(l => ({ id: l.id, name: l.name, parent_id: l.parent_id }))

    useEffect(() => {
        fetchCommandUnits()
        fetchTree(null)
        fetch()
    }, [])

    useEffect(() => {
        const fetchParents = async () => {
            const { data, error } = await getValidParentLocations(selectedType)
            if (!error && data) {
                setParentLocations(data)
            }
        }
        fetchParents()
    }, [selectedType])

    useEffect(() => {
        if (treeItems.length > 0) {
            const allIds = new Set<number>()
            const collectIds = (items: typeof treeItems) => {
                items.forEach(item => {
                    allIds.add(item.id)
                    if (item.children && item.children.length > 0) {
                        collectIds(item.children)
                    }
                })
            }
            collectIds(treeItems)
            setExpandedIds(allIds)
        }
    }, [treeItems])

    const openCreate = () => {
        setEditingId(null)
        setFormData({ name: '', type: selectedType, parent_id: null, unit_id: null })
        setError(null)
        setShowModal(true)
    }

    const openEdit = (item: LocationCreate & { id: number; type: LocationType }) => {
        setEditingId(item.id)
        setFormData({
            name: item.name,
            type: item.type,
            parent_id: item.parent_id ?? null,
            unit_id: item.unit_id ?? null,
        })
        setSelectedType(item.type)
        setError(null)
        setShowModal(true)
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError(null)
        try {
            if (editingId) {
                await update(editingId, formData)
            } else {
                await create(formData)
            }
            setShowModal(false)
        } catch (err: unknown) {
            setError((err as { message?: string }).message || 'Failed to save location')
        }
    }

    const handleDelete = async (id: number) => {
        try {
            await remove(id)
            setConfirmDeleteId(null)
        } catch (err: unknown) {
            setError((err as { message?: string }).message || 'Failed to delete location')
        }
    }

    const handleChainSubmit = async (chainData: { chain: Array<{ type: LocationType; id?: number; name: string }> }) => {
        const chain = chainData.chain.map(step => ({
            type: step.type,
            name: step.name,
            sort_order: 0,
            ...(step.id !== undefined && { id: step.id }),
        }))

        await createWithFullChain({
            chain,
            skip_indices: [],
            unit_id: selectedUnitId,
        })
        setShowChainDialog(false)
    }

    const toggleRow = (id: number) => {
        const newExpanded = new Set(expandedIds)
        if (newExpanded.has(id)) {
            newExpanded.delete(id)
        } else {
            newExpanded.add(id)
        }
        setExpandedIds(newExpanded)
    }

    const renderTableRow = useCallback((item: typeof treeItems[number], level = 0) => {
        const hasChildren = item.children && item.children.length > 0
        const isExpanded = expandedIds.has(item.id)

        return (
            <React.Fragment key={item.id}>
                <tr className="border-b border-bd hover:bg-surface-2/50 transition-colors">
                    <td className="py-3 px-4" style={{ paddingLeft: `${level * 24 + 16}px` }}>
                        <div className="flex items-center gap-2">
                            {hasChildren ? (
                                <button
                                    onClick={() => toggleRow(item.id)}
                                    className="p-1 hover:bg-surface-2 rounded transition-colors"
                                    title={isExpanded ? 'Collapse' : 'Expand'}
                                >
                                    <HiOutlineChevronRight
                                        className={`text-secondary transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`}
                                    />
                                </button>
                            ) : (
                                <span className="w-6" />
                            )}
                            <HiOutlineBuildingOffice2 className="text-accent text-lg shrink-0" />
                            <p className="font-semibold text-primary">{item.name}</p>
                        </div>
                    </td>
                    <td className="py-3 px-4">
                        <span className="px-2 py-1 rounded-full text-[10px] font-semibold bg-accent/10 text-accent uppercase">
                            {item.type}
                        </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-secondary">{item.path || '—'}</td>
                    <td className="py-3 px-4 text-sm text-secondary">
                        {item.unit_name || '—'}
                    </td>
                    <td className="py-3 px-4">
                        <div className="flex items-center gap-1 justify-end">
                            <button
                                onClick={() => openEdit(item as LocationCreate & { id: number; type: LocationType })}
                                className="p-2 rounded-lg hover:bg-surface-2 transition-colors"
                                title={t('common.edit')}
                            >
                                <HiOutlinePencil className="text-secondary" />
                            </button>
                            <button
                                onClick={() => setConfirmDeleteId(item.id)}
                                className="p-2 rounded-lg hover:bg-red-500/10 transition-colors"
                                title={t('common.delete')}
                            >
                                <HiOutlineTrash className="text-red-500" />
                            </button>
                        </div>
                    </td>
                </tr>
                {hasChildren && isExpanded && item.children?.map(child => renderTableRow(child, level + 1))}
            </React.Fragment>
        )
    }, [t, openEdit, expandedIds])

    const inputClass = 'w-full px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20'

    const typeOptions = [
        { id: 'emirate', value: 'Emirate', group: 'Root' },
        { id: 'base', value: 'Base', group: 'Level 2' },
        { id: 'location', value: 'Location', group: 'Level 3' },
        { id: 'building', value: 'Building', group: 'Level 4' },
        { id: 'area', value: 'Area', group: 'Level 5' },
    ]

    const parentOptions = parentLocations.map((loc) => ({
        id: loc.id,
        value: `${loc.name} (${loc.type})`,
        group: loc.type,
        meta: { typeId: loc.id },
    }))

    return (
        <div className="flex flex-col gap-5 overflow-hidden h-[100%]">
            <SectionHeader
                eyebrow={t('common.management')}
                title={t('nav.master.locations.title')}
                description={t('nav.master.locations.description')}
                actions={
                    <button
                        onClick={() => setShowChainDialog(true)}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-[9px] text-sm font-semibold text-white bg-accent hover:opacity-90 transition-opacity border-none cursor-pointer"
                    >
                        <HiOutlinePlus className="text-lg" />
                        {t('nav.master.locations.createLocation')}
                    </button>
                }
            />

            <div className="flex items-center gap-3">
                <label htmlFor="unit-filter" className="text-sm font-medium text-secondary">
                    {t('nav.master.locations.unitFilter')}:
                </label>
                <select
                    id="unit-filter"
                    value={selectedUnitId === null ? 'ALL' : selectedUnitId.toString()}
                    onChange={(e) => {
                        const value = e.target.value
                        const unitId = value === 'ALL' ? null : parseInt(value, 10)
                        setSelectedUnitId(unitId)
                    }}
                    className="px-3 py-2 bg-surface border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent"
                >
                    <option value="ALL">{t('nav.master.locations.allUnits')}</option>
                    {commandUnits.map((unit) => (
                        <option key={unit.id} value={unit.id}>
                            {unit.name}
                        </option>
                    ))}
                </select>
            </div>

            <div className="flex flex-col gap-2 overflow-auto h-full">
                <div className="card p-0 h-full overflow-auto">
                    {isLoading && (
                        <div className="flex items-center justify-center py-12">
                            <p className="text-sm text-muted">Loading…</p>
                        </div>
                    )}
                    {!isLoading && treeItems.length === 0 && (
                        <div className="flex flex-col items-center justify-center text-center px-6 py-12">
                            <span className="rounded-2xl flex items-center justify-center shrink-0 w-16 h-16 text-[30px] mb-4"
                                  style={{ background: 'var(--accent-light)', color: 'var(--accent)' }}>✦</span>
                            <p className="text-[16px] font-semibold text-primary">{t('nav.master.locations.noLocations')}</p>
                        </div>
                    )}
                    {!isLoading && treeItems.length > 0 && (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                  <thead className="bg-surface-2 sticky top-0 z-10">
                                      <tr>
                                          <th className="text-left text-xs font-semibold text-secondary uppercase tracking-wider py-3 px-4 w-[220px]">Name</th>
                                          <th className="text-left text-xs font-semibold text-secondary uppercase tracking-wider py-3 px-4 w-[120px]">Type</th>
                                          <th className="text-left text-xs font-semibold text-secondary uppercase tracking-wider py-3 px-4 w-[280px]">Path</th>
                                          <th className="text-left text-xs font-semibold text-secondary uppercase tracking-wider py-3 px-4 w-[180px]">Unit</th>
                                          <th className="text-right text-xs font-semibold text-secondary uppercase tracking-wider py-3 px-4 w-[100px]">Actions</th>
                                      </tr>
                                  </thead>
                                <tbody>
                                    {treeItems.map(item => renderTableRow(item))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            {showModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-surface rounded-2xl border border-bd shadow-elevated w-full max-w-lg overflow-hidden" onClick={(e) => e.stopPropagation()}>
                        <div className="px-6 py-4 border-b border-bd">
                            <p className="text-lg font-bold text-primary">{editingId ? t('nav.master.locations.editLocation') : t('nav.master.locations.addLocation')}</p>
                        </div>
                        <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-4">
                            {editingId && (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium text-secondary mb-1">Type</label>
                                        <div className="px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm">
                                            {formData.type.charAt(0).toUpperCase() + formData.type.slice(1)}
                                        </div>
                                    </div>
                                    {formData.parent_id !== null && (
                                        <div>
                                            <label className="block text-sm font-medium text-secondary mb-1">Parent</label>
                                            <div className="px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm">
                                                {parentOptions.find(p => p.id === formData.parent_id)?.value || t('nav.master.locations.noParent')}
                                            </div>
                                        </div>
                                    )}
                                </>
                            )}
                            {!editingId && (
                                <>
                                    <div>
                                        <label htmlFor="location-type" className="block text-sm font-medium text-secondary mb-1">Type</label>
                                        <select
                                            id="location-type"
                                            value={formData.type}
                                            onChange={(e) => {
                                                const newType = e.target.value as LocationType
                                                setFormData({ ...formData, type: newType, parent_id: null })
                                                setSelectedType(newType)
                                            }}
                                            className={inputClass}
                                        >
                                            <option value="emirate">Emirate</option>
                                            <option value="base">Base</option>
                                            <option value="location">Location</option>
                                            <option value="building">Building</option>
                                            <option value="area">Area</option>
                                        </select>
                                    </div>
                                    {formData.type !== 'emirate' && (
                                        <div>
                                            <label htmlFor="location-parent" className="block text-sm font-medium text-secondary mb-1">{t('nav.master.locations.parent')}</label>
                                            <select
                                                id="location-parent"
                                                value={formData.parent_id ?? ''}
                                                onChange={(e) => setFormData({ ...formData, parent_id: e.target.value ? Number(e.target.value) : null })}
                                                className={inputClass}
                                            >
                                                <option value="">{t('nav.master.locations.noParent')}</option>
                                                {parentOptions.map((opt) => (
                                                    <option key={opt.id} value={opt.id}>{opt.value}</option>
                                                ))}
                                            </select>
                                        </div>
                                    )}
                                </>
                            )}
                            <div>
                                <label htmlFor="location-name" className="block text-sm font-medium text-secondary mb-1">{t('nav.master.locations.name')}</label>
                                <input
                                    id="location-name"
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    required
                                    className={inputClass}
                                />
                            </div>
                            {(formData.type === 'location' || formData.type === 'building' || formData.type === 'area') && (
                                <div>
                                    <label htmlFor="location-unit" className="block text-sm font-medium text-secondary mb-1">Unit</label>
                                    <select
                                        id="location-unit"
                                        value={formData.unit_id ?? ''}
                                        onChange={(e) => setFormData({ ...formData, unit_id: e.target.value ? Number(e.target.value) : null })}
                                        className={inputClass}
                                    >
                                        <option value="">None</option>
                                        {commandUnits.map((unit) => (
                                            <option key={unit.id} value={unit.id}>{unit.name}</option>
                                        ))}
                                    </select>
                                </div>
                            )}
                            {error && (
                                <div className="flex items-start gap-2 px-3 py-2.5 rounded-lg bg-red-500/10 border border-red-500/20">
                                    <p className="text-sm text-red-500">{error}</p>
                                </div>
                            )}
                            <div className="flex justify-end gap-2 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="px-4 py-2 rounded-[9px] text-sm font-semibold text-secondary bg-surface-2 border border-bd hover:bg-surface transition-colors cursor-pointer"
                                >
                                    {t('common.cancel')}
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 rounded-[9px] text-sm font-semibold text-white bg-accent hover:opacity-90 transition-opacity border-none cursor-pointer"
                                >
                                    {t('nav.master.common.saveLocation')}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {confirmDeleteId && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setConfirmDeleteId(null)}>
                    <div className="bg-surface rounded-2xl border border-bd shadow-elevated w-full max-w-sm overflow-hidden" onClick={(e) => e.stopPropagation()}>
                        <div className="p-6 text-center">
                            <p className="text-sm font-bold text-primary mb-2">{t('nav.master.locations.deleteLocation')}</p>
                            <p className="text-sm text-secondary mb-6">{t('nav.master.locations.confirmDeleteMessage')}</p>
                            <div className="flex justify-center gap-2">
                                <button
                                    onClick={() => setConfirmDeleteId(null)}
                                    className="px-4 py-2 rounded-[9px] text-sm font-semibold text-secondary bg-surface-2 border border-bd hover:bg-surface transition-colors cursor-pointer"
                                >
                                    {t('common.cancel')}
                                </button>
                                <button
                                    onClick={() => handleDelete(confirmDeleteId)}
                                    className="px-4 py-2 rounded-[9px] text-sm font-semibold text-white bg-red-500 hover:opacity-90 transition-opacity border-none cursor-pointer"
                                >
                                    {t('common.delete')}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <CreateLocationChainDialog
                isOpen={showChainDialog}
                onClose={() => setShowChainDialog(false)}
                onSubmit={handleChainSubmit}
                existingEmirates={emirates}
                existingBases={bases}
                existingLocations={locations}
                existingBuildings={buildings}
                existingAreas={areas}
            />
        </div>
    )
}
