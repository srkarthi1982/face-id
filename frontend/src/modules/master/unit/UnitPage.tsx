import { useCallback, useEffect, useState } from 'react'
import { useShallow } from 'zustand/react/shallow'
import { useI18n } from '../../../infra/locales/I18nContext'
import { useUnitStore } from './store'
import SectionHeader from '../../../infra/shared/components/SectionHeader'
import { SearchableCombobox } from '../../../infra/shared/components/SearchableCombobox'
import { CreateUnitChainDialog } from '../../../infra/shared/components/CreateUnitChainDialog'
import type { UnitCreate, UnitUpdate, UnitType, UnitChainItem, UnitChainCreate } from '../types'
import type { UnitItem as StoreUnitItem } from './store'

import React from 'react'
import { HiOutlineUserGroup, HiOutlinePlus, HiOutlinePencil, HiOutlineTrash, HiOutlineChevronRight } from 'react-icons/hi2'



export default function UnitPage() {
    const { t } = useI18n()
    const { treeItems, flatItems, itemsByType, isLoading, fetchTree, fetch, fetchByType, create, update, remove, createWithFullChain } = useUnitStore(
        useShallow((s) => ({
            treeItems: s.treeItems,
            flatItems: s.flatItems,
            itemsByType: s.itemsByType,
            isLoading: s.isLoading,
            fetchTree: s.fetchTree,
            fetch: s.fetch,
            fetchByType: s.fetchByType,
            create: s.create,
            update: s.update,
            remove: s.remove,
            createWithFullChain: s.createWithFullChain,
        }))
    )

    const [showModal, setShowModal] = useState(false)
    const [editingId, setEditingId] = useState<number | null>(null)
    const [formData, setFormData] = useState({
        name: '',
        code: '',
        description: '',
        type: 'unit' as UnitType,
        parent_id: null as number | null,
        sort_order: 0,
    })
    const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [showChainDialog, setShowChainDialog] = useState(false)
    const [selectedType, setSelectedType] = useState<UnitType>('unit')

    const forces = (itemsByType?.force ?? []).sort((a, b) => a.name.localeCompare(b.name)).map(f => ({ id: f.id, name: f.name, code: f.code ?? '', description: f.description, parent_id: f.parent_id }))
    const commands = (itemsByType?.command ?? []).sort((a, b) => a.name.localeCompare(b.name)).map(c => ({ id: c.id, name: c.name, code: c.code ?? '', description: c.description, parent_id: c.parent_id }))
    const battalions = (itemsByType?.battalion ?? []).sort((a, b) => a.name.localeCompare(b.name)).map(b => ({ id: b.id, name: b.name, code: b.code ?? '', description: b.description, parent_id: b.parent_id }))
    const units = (itemsByType?.unit ?? []).sort((a, b) => a.name.localeCompare(b.name)).map(u => ({ id: u.id, name: u.name, code: u.code ?? '', description: u.description, parent_id: u.parent_id }))

    useEffect(() => {
        fetchTree()
        fetch()
        fetchByType('force')
        fetchByType('command')
        fetchByType('battalion')
        fetchByType('unit')
    }, [])



    const openCreate = () => {
        setEditingId(null)
        setFormData({ name: '', code: '', description: '', type: selectedType, parent_id: null, sort_order: 0 })
        setError(null)
        setShowModal(true)
    }

    const openEdit = (item: UnitCreate & { id: number; type: UnitType }) => {
        // Look up the full item from flatItems to get parent_id
        const fullItem = flatItems?.find(f => f.id === item.id)
        const parentId = fullItem?.parent_id ?? item.parent_id ?? null
        
        setEditingId(item.id)
        setFormData({
            name: item.name,
            code: item.code ?? '',
            description: item.description ?? '',
            type: item.type ?? 'unit',
            parent_id: parentId,
            sort_order: item.sort_order ?? 0,
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
            setError((err as { message?: string }).message || 'Failed to save unit')
        }
    }

    const handleDelete = async (id: number) => {
        try {
            await remove(id)
            setConfirmDeleteId(null)
        } catch (err: unknown) {
            setError((err as { message?: string }).message || 'Failed to delete unit')
        }
    }

    const handleChainSubmit = async (chain: UnitChainCreate) => {
        await createWithFullChain(chain)
        // Dialog auto-closes on success
    }

    const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())

    const toggleRow = (id: number) => {
        setExpandedRows(prev => {
            const next = new Set(prev)
            if (next.has(id)) {
                next.delete(id)
            } else {
                next.add(id)
            }
            return next
        })
    }

    const renderTableRow = (item: StoreUnitItem, level = 0) => {
        const hasChildren = item.children && item.children.length > 0
        const isExpanded = expandedRows.has(item.id)

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
                            <HiOutlineUserGroup className="text-accent text-lg shrink-0" />
                            <p className="font-semibold text-primary">{item.code || '—'}</p>
                        </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-secondary">{item.name}</td>
                    <td className="py-3 px-4 text-sm text-secondary max-w-xs truncate">{item.description || '—'}</td>
                    <td className="py-3 px-4">
                        <span className="px-2 py-1 rounded-full text-[10px] font-semibold bg-accent/10 text-accent uppercase">
                            {item.type}
                        </span>
                    </td>
                    <td className="py-3 px-4">
                        <div className="flex items-center gap-1 justify-end">
                            <button
                                onClick={() => openEdit(item as any)}
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
    }

    const inputClass = 'w-full px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20'

    const parentOptions = (() => {
        const options: Array<{ id: number | string; value: string; group: string; meta: { typeId: number } }> = []
        
        // Build options from itemsByType based on selected type
        if (selectedType === 'command') {
            options.push(...(itemsByType?.force ?? []).map(f => ({
                id: f.id,
                value: `${f.name} (force)`,
                group: 'force',
                meta: { typeId: f.id },
            })))
        } else if (selectedType === 'battalion') {
            options.push(...(itemsByType?.force ?? []).map(f => ({
                id: f.id,
                value: `${f.name} (force)`,
                group: 'force',
                meta: { typeId: f.id },
            })))
            options.push(...(itemsByType?.command ?? []).map(c => ({
                id: c.id,
                value: `${c.name} (command)`,
                group: 'command',
                meta: { typeId: c.id },
            })))
        } else if (selectedType === 'unit') {
            options.push(...(itemsByType?.force ?? []).map(f => ({
                id: f.id,
                value: `${f.name} (force)`,
                group: 'force',
                meta: { typeId: f.id },
            })))
            options.push(...(itemsByType?.command ?? []).map(c => ({
                id: c.id,
                value: `${c.name} (command)`,
                group: 'command',
                meta: { typeId: c.id },
            })))
            options.push(...(itemsByType?.battalion ?? []).map(b => ({
                id: b.id,
                value: `${b.name} (battalion)`,
                group: 'battalion',
                meta: { typeId: b.id },
            })))
        }
        
        // If editing and current parent is not in the list, add it
        if (editingId && formData.parent_id && !options.some(opt => opt.id === formData.parent_id)) {
            const currentParent = itemsByType?.force?.find(f => f.id === formData.parent_id) ||
                                 itemsByType?.command?.find(c => c.id === formData.parent_id) ||
                                 itemsByType?.battalion?.find(b => b.id === formData.parent_id) ||
                                 itemsByType?.unit?.find(u => u.id === formData.parent_id)
            if (currentParent) {
                options.push({
                    id: currentParent.id,
                    value: `${currentParent.name} (${currentParent.type})`,
                    group: currentParent.type,
                    meta: { typeId: currentParent.id },
                })
            }
        }
        
        return options.sort((a, b) => a.value.localeCompare(b.value, undefined, { sensitivity: 'base' }))
    })()

    return (
        <div className="flex flex-col gap-5 overflow-hidden h-[100%]">
            <SectionHeader
                eyebrow={t('common.management')}
                title={t('nav.master.units.title')}
                description={t('nav.master.units.description')}
                actions={
                    <button
                        onClick={() => setShowChainDialog(true)}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-[9px] text-sm font-semibold text-white bg-accent hover:opacity-90 transition-opacity border-none cursor-pointer"
                    >
                        <HiOutlinePlus className="text-lg" />
                        {t('nav.master.dialogs.createUnit') || 'Create Unit'}
                    </button>
                }
            />

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
                            <p className="text-[16px] font-semibold text-primary">{t('nav.master.units.noUnits')}</p>
                        </div>
                    )}
                    {!isLoading && treeItems.length > 0 && (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-surface-2 sticky top-0 z-10">
                                    <tr>
                                        <th className="text-left text-xs font-semibold text-secondary uppercase tracking-wider py-3 px-4 w-[220px]">Code</th>
                                        <th className="text-left text-xs font-semibold text-secondary uppercase tracking-wider py-3 px-4 w-[200px]">Name</th>
                                        <th className="text-left text-xs font-semibold text-secondary uppercase tracking-wider py-3 px-4">Description</th>
                                        <th className="text-left text-xs font-semibold text-secondary uppercase tracking-wider py-3 px-4 w-[120px]">Type</th>
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
                            <p className="text-lg font-bold text-primary">{editingId ? t('nav.master.units.editUnit') : t('nav.master.units.addUnit')}</p>
                        </div>
                        <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-4">
                            <div>
                                <label htmlFor="unit-parent" className="block text-sm font-medium text-secondary mb-1">{t('nav.master.units.parent')}</label>
                                {editingId ? (
                                    <div className="px-3 py-2 bg-surface-2 border border-bd rounded-lg text-sm text-secondary">
                                        {formData.parent_id ? parentOptions.find(opt => opt.id === formData.parent_id)?.value : 'None'}
                                    </div>
                                ) : (
                                    <SearchableCombobox
                                        options={parentOptions}
                                        placeholder="Select parent unit"
                                        selected={formData.parent_id ? parentOptions.find(opt => opt.id === formData.parent_id) || { id: formData.parent_id, value: 'Loading...' } : null}
                                        onChange={(selected) => {
                                            setFormData({ ...formData, parent_id: selected ? (selected.id as number) : null })
                                        }}
                                        groupBy={(opt) => opt.group}
                                        renderGroupHeader={(group, count) => (
                                            <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider bg-gray-50 border-b border-gray-100 sticky top-0">
                                                {group} ({count})
                                            </div>
                                        )}
                                        className="w-full"
                                    />
                                )}
                            </div>
                            <div>
                                <label htmlFor="unit-code" className="block text-sm font-medium text-secondary mb-1">{t('nav.master.units.code')}</label>
                                <input
                                    id="unit-code"
                                    type="text"
                                    value={formData.code}
                                    onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                                    className={inputClass}
                                />
                            </div>
                            <div>
                                <label htmlFor="unit-name" className="block text-sm font-medium text-secondary mb-1">{t('nav.master.units.name')}</label>
                                <input
                                    id="unit-name"
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    required
                                    className={inputClass}
                                />
                            </div>
                            <div>
                                <label htmlFor="unit-description" className="block text-sm font-medium text-secondary mb-1">{t('nav.master.units.descriptionField')}</label>
                                <textarea
                                    id="unit-description"
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    rows={3}
                                    className={inputClass}
                                />
                            </div>
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
                                    {t('nav.master.common.saveUnit')}
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
                            <p className="text-sm font-bold text-primary mb-2">{t('nav.master.units.deleteUnit')}</p>
                            <p className="text-sm text-secondary mb-6">{t('nav.master.units.confirmDeleteMessage')}</p>
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

            <CreateUnitChainDialog
                isOpen={showChainDialog}
                onClose={() => setShowChainDialog(false)}
                onSubmit={handleChainSubmit}
                existingForces={forces}
                existingCommands={commands}
                existingBattalions={battalions}
                existingUnits={units}
            />
        </div>
    )
}
