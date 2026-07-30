import { useCallback, useRef, useState } from 'react'
import { HiOutlineUserGroup } from 'react-icons/hi2'
import { useShallow } from 'zustand/react/shallow'
import { useI18n } from '../../infra/locales/I18nContext'
import { usePersonnelStore } from './store'
import CrudPage, { type Column, type FormField } from '../../infra/shared/components/CrudPage'
import SectionHeader from '../../infra/shared/components/SectionHeader'
import PhotoUploadModal from './PhotoUploadModal'
import PushToDeviceModal, { type PersonPushOutcome } from './PushToDeviceModal'
import type { PersonnelItem } from './store'

export default function PersonnelListPage() {
    const { t } = useI18n()
    const [photoPerson, setPhotoPerson] = useState<PersonnelItem | null>(null)
    const [pushPersons, setPushPersons] = useState<PersonnelItem[] | null>(null)
    const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())
    // Store only holds the current page, so cache selected persons across pagination
    const selectedPersonsRef = useRef<Map<number, PersonnelItem>>(new Map())
    const lastFetchParamsRef = useRef<{ filters: Record<string, string> } | undefined>(undefined)
    const pushOutcomesRef = useRef<PersonPushOutcome[] | null>(null)
    const { items, pagination, fetch, create, update, remove } = usePersonnelStore(
        useShallow((s) => ({
            items: s.items,
            pagination: s.pagination,
            fetch: s.fetch,
            create: s.create,
            update: s.update,
            remove: s.remove,
        }))
    )

    const handleFetch = useCallback(async (page: number, params?: any) => {
        lastFetchParamsRef.current = params?.filters ? { filters: params.filters } : undefined
        await fetch(page, lastFetchParamsRef.current)
    }, [fetch])

    const handleSelectionChange = useCallback((next: Set<number>) => {
        const map = selectedPersonsRef.current
        for (const item of usePersonnelStore.getState().items) {
            if (next.has(item.id)) map.set(item.id, item)
        }
        for (const id of Array.from(map.keys())) {
            if (!next.has(id)) map.delete(id)
        }
        setSelectedIds(next)
    }, [])

    const handleBulkPush = useCallback(() => {
        const persons = Array.from(selectedIds)
            .map((id) => selectedPersonsRef.current.get(id))
            .filter((p): p is PersonnelItem => !!p)
        if (persons.length > 0) setPushPersons(persons)
    }, [selectedIds])

    const handlePushModalClose = useCallback(() => {
        const outcomes = pushOutcomesRef.current
        pushOutcomesRef.current = null
        setPushPersons(null)
        if (!outcomes || outcomes.length === 0) return
        // Fully successful persons drop out of the selection; failures stay for retry
        const okIds = outcomes.filter((o) => o.ok).map((o) => o.person.id)
        if (okIds.length > 0) {
            setSelectedIds((prev) => {
                const next = new Set(prev)
                for (const id of okIds) {
                    next.delete(id)
                    selectedPersonsRef.current.delete(id)
                }
                return next
            })
        }
        const anyDeviceSuccess = outcomes.some((o) => (o.response?.pushed ?? 0) > 0)
        if (anyDeviceSuccess) {
            fetch(usePersonnelStore.getState().pagination.page, lastFetchParamsRef.current)
        }
    }, [fetch])

    const handleCreate = useCallback(async (payload: Record<string, unknown>) => {
        // Convert string values back to proper types
        const converted = { ...payload }
        if (typeof converted.is_active === 'string') {
            converted.is_active = converted.is_active === 'true'
        }
        if (typeof converted.push_to_device === 'string') {
            converted.push_to_device = converted.push_to_device === 'true'
        }
        if (typeof converted.gender === 'string') {
            converted.gender = parseInt(converted.gender as string, 10)
        }
        await create(converted as any)
    }, [create])

    const handleUpdate = useCallback(async (id: number, payload: Record<string, unknown>) => {
        // Convert string values back to proper types
        const converted = { ...payload }
        if (typeof converted.is_active === 'string') {
            converted.is_active = converted.is_active === 'true'
        }
        if (typeof converted.push_to_device === 'string') {
            converted.push_to_device = converted.push_to_device === 'true'
        }
        if (typeof converted.gender === 'string') {
            converted.gender = parseInt(converted.gender as string, 10)
        }
        await update(id, converted as any)
    }, [update])

    const handleDelete = useCallback(async (id: number) => {
        await remove(id)
    }, [remove])

    const columns: Column<PersonnelItem>[] = [
        { key: 'id', label: t('common.id'), sortable: true },
        { 
            key: 'emp_no', 
            label: t('nav.personnel.fields.emp_no'), 
            sortable: true,
            filterable: true,
        },
        { 
            key: 'full_name', 
            label: t('nav.personnel.fields.full_name'), 
            sortable: true,
            filterable: true,
        },
        { 
            key: 'gender', 
            label: t('nav.personnel.fields.gender'), 
            sortable: true,
            render: (value) => {
                const num = value as number
                if (num === 1) return t('nav.personnel.gender.male')
                if (num === 2) return t('nav.personnel.gender.female')
                return t('nav.personnel.gender.unknown')
            },
        },
        { key: 'email', label: t('nav.personnel.fields.email'), sortable: true },
        { key: 'phone', label: t('nav.personnel.fields.phone'), sortable: true },
        { 
            key: 'is_active', 
            label: t('nav.personnel.fields.is_active'), 
            sortable: true,
            render: (value) => value ? t('common.active') : t('common.inactive'),
        },
        { 
            key: 'push_to_device', 
            label: t('nav.personnel.fields.push_to_device'), 
            sortable: true,
            render: (value) => value ? t('common.yes') : t('common.no'),
        },
    ]

    const formFields: FormField[] = [
        // Employee Information Section
        { name: 'emp_no', label: t('nav.personnel.fields.emp_no'), required: true, section: t('nav.personnel.fields.emp_no'), minLength: 1, maxLength: 64 },
        { name: 'full_name', label: t('nav.personnel.fields.full_name'), required: true, minLength: 1, maxLength: 200 },
        
        // Personal Details Section
        { 
            name: 'gender', 
            label: t('nav.personnel.fields.gender'), 
            type: 'select',
            required: false,
            default: '0',
            section: t('common.personalDetails'),
            options: [
                { value: '0', label: t('nav.personnel.gender.unknown') },
                { value: '1', label: t('nav.personnel.gender.male') },
                { value: '2', label: t('nav.personnel.gender.female') },
            ],
        },
        { 
            name: 'date_of_birth', 
            label: t('nav.personnel.fields.date_of_birth'), 
            type: 'date',
            required: false,
            min: '1900-01-01',
            max: new Date().toISOString().split('T')[0],
        },
        
        // Contact Information Section
        { 
            name: 'email', 
            label: t('nav.personnel.fields.email'), 
            type: 'email', 
            required: false,
            pattern: '.+@.+\\..+',
            maxLength: 255,
            section: t('common.contactInfo'),
        },
        { 
            name: 'phone', 
            label: t('nav.personnel.fields.phone'), 
            type: 'tel',
            required: false,
            pattern: '[0-9+\\-\\s()]{7,20}',
            maxLength: 50,
        },
        
        // Identification Section
        { 
            name: 'nationality', 
            label: t('nav.personnel.fields.nationality'), 
            type: 'text', 
            required: false,
            maxLength: 100,
            section: t('common.identification'),
        },
        { 
            name: 'idcard_num', 
            label: t('nav.personnel.fields.idcard_num'), 
            type: 'text', 
            required: false,
            maxLength: 50,
        },
        { 
            name: 'id_number', 
            label: t('nav.personnel.fields.id_number'), 
            type: 'text', 
            required: false,
            maxLength: 50,
        },
        { 
            name: 'card_no', 
            label: t('nav.personnel.fields.card_no'), 
            type: 'text', 
            required: false,
            maxLength: 100,
        },
        
        // Employment Section
        { 
            name: 'position', 
            label: t('nav.personnel.fields.position'), 
            type: 'text', 
            required: false,
            maxLength: 200,
            section: t('common.employment'),
        },
        { 
            name: 'hire_date', 
            label: t('nav.personnel.fields.hire_date'), 
            type: 'date',
            required: false,
            min: '1950-01-01',
            max: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString().split('T')[0],
        },
        
        // System Settings Section
        { 
            name: 'is_active', 
            label: t('nav.personnel.fields.is_active'), 
            type: 'select',
            required: false,
            default: 'true',
            section: t('nav.settings'),
            options: [
                { value: 'true', label: t('common.active') },
                { value: 'false', label: t('common.inactive') },
            ],
        },
        { 
            name: 'push_to_device', 
            label: t('nav.personnel.fields.push_to_device'), 
            type: 'select',
            required: false,
            default: 'false',
            options: [
                { value: 'true', label: t('common.yes') },
                { value: 'false', label: t('common.no') },
            ],
        },
    ]

    return (
        <div className="flex flex-col gap-6">
            <SectionHeader 
                icon={<HiOutlineUserGroup />} 
                title={t('nav.personnel.title')} 
            />
            
            <CrudPage<PersonnelItem>
                title={t('nav.personnel.title')}
                items={items}
                columns={columns}
                formFields={formFields}
                onFetch={handleFetch}
                totalPages={pagination.pages}
                onCreate={handleCreate}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
                formColumns={2}
                formGridClass="grid grid-cols-1 md:grid-cols-2 gap-4"
                selectedIds={selectedIds}
                onSelectionChange={handleSelectionChange}
                selectionActions={(
                    <button
                        type="button"
                        className="px-2.5 py-1 rounded-[7px] text-xs font-semibold bg-accent text-white hover:opacity-90 transition-opacity border-none cursor-pointer font-sans"
                        onClick={handleBulkPush}
                    >
                        {t('nav.personnel.push.bulkAction')} ({selectedIds.size})
                    </button>
                )}
                rowActions={(item) => (
                    <>
                        <button
                            className="px-2.5 py-1 rounded-[7px] text-xs font-semibold bg-surface-2 text-primary border border-bd hover:border-accent transition-colors cursor-pointer font-sans"
                            onClick={() => setPhotoPerson(item)}
                        >
                            {t('nav.personnel.photo.action')}
                        </button>
                        <button
                            className="px-2.5 py-1 rounded-[7px] text-xs font-semibold bg-surface-2 text-accent border border-bd hover:border-accent transition-colors cursor-pointer font-sans"
                            onClick={() => setPushPersons([item])}
                        >
                            {t('nav.personnel.push.action')}
                        </button>
                    </>
                )}
            />

            {photoPerson && (
                <PhotoUploadModal person={photoPerson} onClose={() => setPhotoPerson(null)} />
            )}

            {pushPersons && (
                <PushToDeviceModal
                    persons={pushPersons}
                    onClose={handlePushModalClose}
                    onPushed={(outcomes) => { pushOutcomesRef.current = outcomes }}
                />
            )}
        </div>
    )
}
