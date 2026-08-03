import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { HiOutlineClock, HiOutlinePencil, HiOutlinePlus, HiOutlineTrash } from 'react-icons/hi2'
import { useShallow } from 'zustand/react/shallow'
import SectionHeader from '../../../infra/shared/components/SectionHeader'
import { useI18n } from '../../../infra/locales/I18nContext'
import { useTimingStore } from './store'
import type { TimingCreate, Weekday } from '../types'
import type { TimingResponse } from '../api'

type TimingForm = {
    department_id: string
    start_day: Weekday
    end_day: Weekday
    start_time: string
    end_time: string
    is_active: boolean
}

const weekdays: Weekday[] = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
const weekdayLabelKeys = {
    monday: 'nav.master.timings.weekdays.monday',
    tuesday: 'nav.master.timings.weekdays.tuesday',
    wednesday: 'nav.master.timings.weekdays.wednesday',
    thursday: 'nav.master.timings.weekdays.thursday',
    friday: 'nav.master.timings.weekdays.friday',
    saturday: 'nav.master.timings.weekdays.saturday',
    sunday: 'nav.master.timings.weekdays.sunday',
} as const
const columns = [
    { key: 'department', label: 'nav.master.timings.department' },
    { key: 'startDay', label: 'nav.master.timings.startDay' },
    { key: 'endDay', label: 'nav.master.timings.endDay' },
    { key: 'startTime', label: 'nav.master.timings.startTime' },
    { key: 'endTime', label: 'nav.master.timings.endTime' },
] as const
const emptyForm = (): TimingForm => ({
    department_id: '',
    start_day: 'monday',
    end_day: 'friday',
    start_time: '08:00',
    end_time: '16:00',
    is_active: true,
})

function normalizeTime(value: string) {
    return value.length === 5 ? `${value}:00` : value
}

function shortTime(value: string) {
    return value.slice(0, 5)
}

export default function TimingPage() {
    const { t } = useI18n()
    const { items, departments, isLoading, fetch, create, update, remove } = useTimingStore(useShallow((state) => ({
        items: state.items,
        departments: state.departments,
        isLoading: state.isLoading,
        fetch: state.fetch,
        create: state.create,
        update: state.update,
        remove: state.remove,
    })))
    const [showModal, setShowModal] = useState(false)
    const [editing, setEditing] = useState<TimingResponse | null>(null)
    const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null)
    const [form, setForm] = useState<TimingForm>(emptyForm)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => { void fetch() }, [fetch])

    const departmentOptions = useMemo(() => departments.map((department) => ({
        id: department.id,
        label: department.code ? `${department.name} (${department.code})` : department.name,
    })), [departments])

    const openCreate = () => {
        setEditing(null)
        setForm({ ...emptyForm(), department_id: departmentOptions[0]?.id ? String(departmentOptions[0].id) : '' })
        setError(null)
        setShowModal(true)
    }

    const openEdit = (item: TimingResponse) => {
        setEditing(item)
        setForm({
            department_id: String(item.department_id),
            start_day: item.start_day as Weekday,
            end_day: item.end_day as Weekday,
            start_time: shortTime(item.start_time),
            end_time: shortTime(item.end_time),
            is_active: item.is_active,
        })
        setError(null)
        setShowModal(true)
    }

    const submit = async (event: FormEvent) => {
        event.preventDefault()
        setError(null)
        if (!form.department_id) {
            setError(t('nav.master.timings.department'))
            return
        }
        if (form.start_time >= form.end_time) {
            setError(t('nav.master.timings.sameDayRequired'))
            return
        }
        const payload: TimingCreate = {
            department_id: Number(form.department_id),
            start_day: form.start_day,
            end_day: form.end_day,
            start_time: normalizeTime(form.start_time),
            end_time: normalizeTime(form.end_time),
            is_active: form.is_active,
        }
        try {
            if (editing) {
                await update(editing.id, payload)
            } else {
                await create(payload)
            }
            setShowModal(false)
        } catch (err: unknown) {
            setError((err as { message?: string }).message || t('nav.master.timings.sameDayRequired'))
        }
    }

    const inputClass = 'w-full rounded-lg border border-bd bg-surface-2 px-3 py-2 text-sm text-primary focus:outline-none focus:ring-2 focus:ring-accent'

    return (
        <div className="flex h-full flex-col gap-5 overflow-hidden">
            <SectionHeader
                icon={<HiOutlineClock />}
                eyebrow={t('common.management')}
                title={t('nav.master.timings.title')}
                description={t('nav.master.timings.description')}
                actions={<button onClick={openCreate} className="inline-flex items-center gap-2 rounded-[9px] bg-accent px-4 py-2 text-sm font-semibold text-white"><HiOutlinePlus />{t('nav.master.timings.addTiming')}</button>}
            />

            <div className="card h-full overflow-auto p-0">
                {isLoading && <div className="p-6 text-sm text-muted">{t('common.loading')}</div>}
                {!isLoading && items.length === 0 && <div className="p-6 text-center text-sm text-muted">{t('nav.master.timings.noTimings')}</div>}
                {!isLoading && items.length > 0 && (
                    <table className="w-full min-w-[760px] text-sm">
                        <thead className="sticky top-0 bg-surface-2 text-secondary">
                            <tr>
                                {columns.map((column) => <th key={column.key} className="px-4 py-3 text-start font-medium">{t(column.label)}</th>)}
                                <th className="px-4 py-3 text-start font-medium">{t('nav.master.common.active')}</th>
                                <th className="px-4 py-3 text-end font-medium">{t('common.actions')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items.map((item) => (
                                <tr key={item.id} className="border-t border-bd">
                                    <td className="px-4 py-3 font-medium">{item.department_name}</td>
                                    <td className="px-4 py-3">{t(weekdayLabelKeys[item.start_day as Weekday])}</td>
                                    <td className="px-4 py-3">{t(weekdayLabelKeys[item.end_day as Weekday])}</td>
                                    <td className="px-4 py-3">{shortTime(item.start_time)}</td>
                                    <td className="px-4 py-3">{shortTime(item.end_time)}</td>
                                    <td className="px-4 py-3">{item.is_active ? t('common.active') : t('common.inactive')}</td>
                                    <td className="px-4 py-3">
                                        <div className="flex justify-end gap-1">
                                            <button aria-label={t('common.edit')} title={t('common.edit')} onClick={() => openEdit(item)} className="rounded-lg p-2 hover:bg-surface-2"><HiOutlinePencil /></button>
                                            <button aria-label={t('common.delete')} title={t('common.delete')} onClick={() => setConfirmDeleteId(item.id)} className="rounded-lg p-2 text-red-500 hover:bg-red-500/10"><HiOutlineTrash /></button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
                    <div className="w-full max-w-lg overflow-hidden rounded-2xl border border-bd bg-surface shadow-elevated">
                        <div className="border-b border-bd px-6 py-4"><p className="text-lg font-bold text-primary">{editing ? t('nav.master.timings.editTiming') : t('nav.master.timings.addTiming')}</p></div>
                        <form onSubmit={submit} className="flex flex-col gap-4 p-6">
                            {error && <div role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-500">{error}</div>}
                            <label className="text-sm text-secondary">{t('nav.master.timings.department')}<select className={inputClass} value={form.department_id} onChange={(event) => setForm({ ...form, department_id: event.target.value })}>{departmentOptions.map((department) => <option key={department.id} value={department.id}>{department.label}</option>)}</select></label>
                            <div className="grid gap-4 sm:grid-cols-2">
                                <label className="text-sm text-secondary">{t('nav.master.timings.startDay')}<select className={inputClass} value={form.start_day} onChange={(event) => setForm({ ...form, start_day: event.target.value as Weekday })}>{weekdays.map((day) => <option key={day} value={day}>{t(weekdayLabelKeys[day])}</option>)}</select></label>
                                <label className="text-sm text-secondary">{t('nav.master.timings.endDay')}<select className={inputClass} value={form.end_day} onChange={(event) => setForm({ ...form, end_day: event.target.value as Weekday })}>{weekdays.map((day) => <option key={day} value={day}>{t(weekdayLabelKeys[day])}</option>)}</select></label>
                                <label className="text-sm text-secondary">{t('nav.master.timings.startTime')}<input className={inputClass} type="time" value={form.start_time} onChange={(event) => setForm({ ...form, start_time: event.target.value })} required /></label>
                                <label className="text-sm text-secondary">{t('nav.master.timings.endTime')}<input className={inputClass} type="time" value={form.end_time} onChange={(event) => setForm({ ...form, end_time: event.target.value })} required /></label>
                            </div>
                            <label className="flex items-center gap-2 text-sm text-secondary"><input type="checkbox" checked={form.is_active} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} />{t('nav.master.common.active')}</label>
                            <div className="flex justify-end gap-2 pt-2"><button type="button" onClick={() => setShowModal(false)} className="rounded-lg border border-bd px-4 py-2 text-sm">{t('common.cancel')}</button><button type="submit" className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white">{t('common.save')}</button></div>
                        </form>
                    </div>
                </div>
            )}

            {confirmDeleteId !== null && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
                    <div className="w-full max-w-md rounded-2xl border border-bd bg-surface p-6 shadow-elevated">
                        <p className="font-semibold text-primary">{t('nav.master.timings.deleteTiming')}</p>
                        <p className="mt-2 text-sm text-secondary">{t('nav.master.timings.confirmDeleteMessage')}</p>
                        <div className="mt-5 flex justify-end gap-2"><button onClick={() => setConfirmDeleteId(null)} className="rounded-lg border border-bd px-4 py-2 text-sm">{t('common.cancel')}</button><button onClick={() => void remove(confirmDeleteId).then(() => setConfirmDeleteId(null))} className="rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white">{t('common.delete')}</button></div>
                    </div>
                </div>
            )}
        </div>
    )
}
