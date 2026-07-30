import { Fragment, useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react'
import {
  HiOutlinePlus,
  HiOutlineChevronUp,
  HiOutlineChevronDown,
  HiMiniChevronUpDown,
  HiOutlineMagnifyingGlass,
  HiOutlineExclamationCircle,
} from 'react-icons/hi2'
import Paginator from './Paginator'
import { useI18n } from '../../locales/I18nContext'
import { confirmDialog } from '../store/useConfirmStore'
import useToastStore from '../store/useToastStore'

export interface SelectOption {
  value: string | number
  label: string
}

export interface FormField {
  name: string
  label: string
  type?: 'text' | 'number' | 'date' | 'select' | 'email' | 'password' | 'tel'
  required?: boolean
  default?: string | number
  options?: SelectOption[]
  section?: string  // Optional section header for grouping
  pattern?: string
  minLength?: number
  maxLength?: number
  min?: string | number
  max?: string | number
}

export interface SortFilterParams {
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  filters?: Record<string, string>
}

export interface Column<T> {
  key: keyof T & string
  label: string
  render?: (value: T[keyof T], item: T) => ReactNode
  sortable?: boolean
  filterable?: boolean
}

interface CrudPageProps<T extends { id: number }> {
  title: string
  items: T[]
  columns: Column<T>[]
  formFields: FormField[]
  onFetch: (page: number, params?: SortFilterParams) => Promise<void>
  totalPages?: number
  onCreate: (payload: Record<string, unknown>) => Promise<void>
  onUpdate: (id: number, payload: Record<string, unknown>) => Promise<void>
  onDelete: (id: number) => Promise<void>
  formColumns?: 1 | 2 | 3
  formGridClass?: string
  rowActions?: (item: T) => ReactNode
  selectedIds?: Set<number>
  onSelectionChange?: (next: Set<number>) => void
  selectionActions?: ReactNode
}

const inputClass = 'w-full px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20'

export default function CrudPage<T extends { id: number }>({
  title,
  items,
  columns,
  formFields,
  onFetch,
  totalPages,
  onCreate,
  onUpdate,
  onDelete,
  formColumns = 1,
  formGridClass,
  rowActions,
  selectedIds,
  onSelectionChange,
  selectionActions,
}: CrudPageProps<T>) {
  const { t } = useI18n()
  const [showModal, setShowModal]     = useState(false)
  const [editing, setEditing]         = useState<T | null>(null)
  const [form, setForm]               = useState<Record<string, string | number>>({})
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [page, setPage]               = useState(1)
  const [sortBy, setSortBy]           = useState<string | undefined>()
  const [sortOrder, setSortOrder]     = useState<'asc' | 'desc'>('asc')
  const [filterInputs, setFilterInputs]       = useState<Record<string, string>>({})
  const [debouncedFilters, setDebouncedFilters] = useState<Record<string, string>>({})
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    const params: SortFilterParams = {}
    if (sortBy) { params.sortBy = sortBy; params.sortOrder = sortOrder }
    const activeFilters = Object.fromEntries(Object.entries(debouncedFilters).filter(([, v]) => v !== ''))
    if (Object.keys(activeFilters).length) params.filters = activeFilters
    onFetch(page, Object.keys(params).length ? params : undefined)
  }, [page, sortBy, sortOrder, debouncedFilters]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSort = (key: string) => {
    const newOrder = sortBy === key && sortOrder === 'asc' ? 'desc' : 'asc'
    setSortBy(key)
    setSortOrder(newOrder)
    setPage(1)
  }

  const handleFilterChange = (key: string, value: string) => {
    const newInputs = { ...filterInputs, [key]: value }
    setFilterInputs(newInputs)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      setDebouncedFilters(newInputs)
      setPage(1)
    }, 400)
  }

  const openCreate = () => {
    setEditing(null)
    setSubmitError(null)
    const initial: Record<string, string | number> = {}
    formFields.forEach((f) => { initial[f.name] = f.default ?? '' })
    setForm(initial)
    setShowModal(true)
  }

  const openEdit = (item: T) => {
    setEditing(item)
    setSubmitError(null)
    const initial: Record<string, string | number> = {}
    formFields.forEach((f) => { initial[f.name] = (item as Record<string, unknown>)[f.name] as string | number ?? '' })
    setForm(initial)
    setShowModal(true)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSubmitError(null)
    
    // Client-side validation
    const errors: string[] = []
    formFields.forEach((f) => {
      const value = form[f.name]
      
      // Skip empty optional fields
      if (!value && f.required !== true) return
      
      // Email pattern validation
      if (f.type === 'email' && value && !/.+@.+\..+/.test(String(value))) {
        errors.push(t('common.validation.invalidEmail'))
      }
      
      // Phone pattern validation
      if (f.type === 'tel' && value && !/[0-9+\-\s()]{7,20}/.test(String(value))) {
        errors.push(t('common.validation.invalidPhone'))
      }
      
      // Date of birth validation (must be in past)
      if (f.name === 'date_of_birth' && value) {
        const dob = new Date(String(value))
        if (dob > new Date()) {
          errors.push(t('common.validation.dateOfBirthInFuture'))
        }
      }
      
      // Max length validation
      if (f.maxLength && typeof value === 'string' && value.length > f.maxLength) {
        errors.push(`${f.label}: ${t('common.validation.fieldTooLong')} (max: ${f.maxLength})`)
      }
    })
    
    if (errors.length > 0) {
      setSubmitError(errors.join('; '))
      return
    }
    
    try {
      const payload: Record<string, unknown> = { ...form }
      formFields.forEach((f) => { if (f.type === 'number') payload[f.name] = Number(payload[f.name]) })
      if (editing) await onUpdate(editing.id, payload)
      else await onCreate(payload)
      setShowModal(false)
    } catch (err: any) {
      setSubmitError(err?.message || 'An unexpected error occurred')
    }
  }

  const handleDelete = async (id: number) => {
    const ok = await confirmDialog({
      title: t('common.confirmDelete'),
      confirmLabel: t('common.delete'),
      tone: 'danger',
    })
    if (!ok) return
    try {
      await onDelete(id)
    } catch (err: any) {
      useToastStore.getState().push({ variant: 'error', title: err?.message || 'Failed to delete record' })
    }
  }

  const filterableCols = columns.filter((c) => c.filterable)
  const hasFilters     = filterableCols.length > 0

  const selectionEnabled = !!(selectedIds && onSelectionChange)
  const allChecked  = selectionEnabled && items.length > 0 && items.every((i) => selectedIds.has(i.id))
  const someChecked = selectionEnabled && items.some((i) => selectedIds.has(i.id))

  const toggleRow = (id: number) => {
    if (!selectionEnabled) return
    const next = new Set(selectedIds)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    onSelectionChange(next)
  }

  const toggleAllOnPage = () => {
    if (!selectionEnabled) return
    const next = new Set(selectedIds)
    for (const item of items) {
      if (allChecked) next.delete(item.id)
      else next.add(item.id)
    }
    onSelectionChange(next)
  }

  const SortIcon = ({ col }: { col: string }) => {
    if (sortBy !== col) return <HiMiniChevronUpDown className="text-[13px] text-white/40 shrink-0" />
    return sortOrder === 'asc'
      ? <HiOutlineChevronUp className="text-[11px] text-white shrink-0" />
      : <HiOutlineChevronDown className="text-[11px] text-white shrink-0" />
  }

  return (
    <div>
      {/* ── Page header ── */}
      <div className="px-6 py-5 flex items-start justify-between gap-4 mb-4">
        <div>
          <p className="text-[11px] font-bold text-accent tracking-[0.09em] uppercase mb-1">
            {t('common.management')}
          </p>
          <h1 className="text-2xl font-bold text-primary tracking-[-0.02em]">{title}</h1>
        </div>
        <button
          className="inline-flex items-center gap-1.5 bg-accent text-white text-sm font-semibold py-[9px] px-4 rounded-[10px] hover:opacity-90 transition-opacity border-none cursor-pointer font-sans shrink-0"
          onClick={openCreate}
        >
          <HiOutlinePlus className="text-[15px]" />
          {t('common.addNew')}
        </button>
      </div>

      {/* ── Toolbar (filters + bulk actions) ── */}
      {(hasFilters || (selectionEnabled && selectedIds.size > 0)) && (
        <div className="card px-4 py-3 flex flex-wrap items-center gap-3 mb-4">
          {hasFilters && filterableCols.map((c) => (
            <div key={c.key} className="relative min-w-[180px] flex-1">
              <HiOutlineMagnifyingGlass className="absolute start-3 top-1/2 -translate-y-1/2 text-[14px] text-muted pointer-events-none" />
              <input
                type="text"
                placeholder={c.label}
                value={filterInputs[c.key] ?? ''}
                onChange={(e) => handleFilterChange(c.key, e.target.value)}
                className="w-full h-9 ps-8 pe-3 rounded-[9px] bg-surface-2 text-primary text-sm border border-bd focus:outline-none focus:border-accent transition-[border-color] duration-150"
              />
            </div>
          ))}
          {selectionEnabled && selectedIds.size > 0 && (
            <div className="ms-auto flex items-center gap-2">
              <span className="text-xs font-semibold text-secondary whitespace-nowrap">
                {selectedIds.size} {t('common.selectedCount')}
              </span>
              <button
                type="button"
                className="px-2.5 py-1 rounded-[7px] text-xs font-semibold bg-surface-2 text-secondary border border-bd hover:border-accent transition-colors cursor-pointer font-sans"
                onClick={() => onSelectionChange(new Set())}
              >
                {t('common.clearSelection')}
              </button>
              {selectionActions}
            </div>
          )}
        </div>
      )}

      {/* ── Table ── */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-bd" style={{ background: 'var(--navy)' }}>
                {selectionEnabled && (
                  <th className="w-10 px-4 py-3">
                    <input
                      type="checkbox"
                      checked={allChecked}
                      ref={(el) => { if (el) el.indeterminate = someChecked && !allChecked }}
                      onChange={toggleAllOnPage}
                      className="w-3.5 h-3.5 accent-[var(--accent)] cursor-pointer"
                    />
                  </th>
                )}
                {columns.map((c) => (
                  <th
                    key={c.key}
                    onClick={c.sortable ? () => handleSort(c.key) : undefined}
                    className={[
                      'px-4 py-3 text-start text-[11px] font-bold text-white/60 uppercase tracking-[0.06em] whitespace-nowrap',
                      c.sortable ? 'cursor-pointer select-none hover:text-white transition-colors' : '',
                      sortBy === c.key ? 'text-white' : '',
                    ].filter(Boolean).join(' ')}
                  >
                    <span className="inline-flex items-center gap-1">
                      {c.label}
                      {c.sortable && <SortIcon col={c.key} />}
                    </span>
                  </th>
                ))}
                <th className="px-4 py-3 text-start text-[11px] font-bold text-white/60 uppercase tracking-[0.06em]">
                  {t('common.actions')}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-bd">
              {items.map((item) => (
                <tr
                  key={item.id}
                  className={`${selectionEnabled && selectedIds.has(item.id) ? 'bg-accent-light' : 'hover:bg-surface-2'} transition-colors duration-100`}
                >
                  {selectionEnabled && (
                    <td className="w-10 px-4 py-3">
                      <input
                        type="checkbox"
                        checked={selectedIds.has(item.id)}
                        onChange={() => toggleRow(item.id)}
                        className="w-3.5 h-3.5 accent-[var(--accent)] cursor-pointer"
                      />
                    </td>
                  )}
                  {columns.map((c) => (
                    <td key={c.key} className="px-4 py-3 text-sm text-primary text-start">
                      {c.render ? c.render(item[c.key], item) : String(item[c.key] ?? '')}
                    </td>
                  ))}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5">
                      {rowActions?.(item)}
                      <button
                        className="px-2.5 py-1 rounded-[7px] text-xs font-semibold bg-accent text-white hover:opacity-90 transition-opacity border-none cursor-pointer font-sans"
                        onClick={() => openEdit(item)}
                      >
                        {t('common.edit')}
                      </button>
                      <button
                        className="px-2.5 py-1 rounded-[7px] text-xs font-semibold bg-red-500 text-white hover:opacity-90 transition-opacity border-none cursor-pointer font-sans"
                        onClick={() => handleDelete(item.id)}
                      >
                        {t('common.delete')}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td colSpan={columns.length + 1 + (selectionEnabled ? 1 : 0)} className="text-center py-12 text-muted text-sm">
                    {t('common.noRecords')}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <Paginator page={page} totalPages={totalPages ?? 1} onPageChange={setPage} />

      {/* ── Modal ── */}
      {showModal && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setShowModal(false)}
        >
          <div
            className="bg-surface rounded-2xl border border-bd shadow-elevated w-[90%] max-w-lg max-h-[85vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal header — navy */}
            <div
              className="px-6 py-4 flex items-center gap-2.5 shrink-0"
              style={{ background: 'linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%)' }}
            >
              <div>
                <p className="text-[13px] font-bold text-white">
                  {editing ? t('common.edit') : t('common.create')} {title.replace(/s$/, '')}
                </p>
                <p className="text-[11px] text-white/50 mt-px">
                  {editing ? t('common.updateRecordHint') : t('common.fillFieldsHint')}
                </p>
              </div>
            </div>

            {/* Modal body */}
            <div className="p-6 overflow-y-auto flex-1">
              <form id="crud-form" onSubmit={handleSubmit}>
                <div className={formGridClass ?? `grid grid-cols-${formColumns} gap-4`}>
                  {formFields.map((f, index) => {
                    // Show section header if this field starts a new section
                    const showSection = f.section && (index === 0 || formFields[index - 1]?.section !== f.section)
                    return (
                      <Fragment key={f.name}>
                        {showSection && (
                          <div className="col-span-full mt-2 mb-1">
                            <h3 className="text-sm font-semibold text-accent uppercase tracking-wide border-b border-bd pb-1">
                              {f.section}
                            </h3>
                          </div>
                        )}
                        <div>
                          <label className="block text-sm font-medium text-secondary mb-1">
                            {f.label}
                            {f.required === true && (
                              <span className="text-red-500 ml-1" aria-label="required">*</span>
                            )}
                          </label>
                          {f.type === 'select' ? (
                            <select
                              value={form[f.name] ?? ''}
                              onChange={(e) => setForm({ ...form, [f.name]: e.target.value })}
                              required={f.required === true}
                              className={inputClass}
                            >
                              <option value="">{t('common.selectPlaceholder')}</option>
                              {(f.options || []).map((o) => (
                                <option key={o.value} value={o.value}>{o.label}</option>
                              ))}
                            </select>
                          ) : (
                            <input
                              type={f.type || 'text'}
                              value={form[f.name] ?? ''}
                              onChange={(e) => setForm({ ...form, [f.name]: e.target.value })}
                              required={f.required === true}
                              maxLength={f.maxLength}
                              pattern={f.pattern}
                              min={f.min}
                              max={f.max}
                              className={inputClass}
                            />
                          )}
                        </div>
                      </Fragment>
                    )
                  })}
                </div>
                {submitError && (
                  <div className="mt-4 flex items-start gap-2 px-3 py-2.5 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
                    <HiOutlineExclamationCircle className="text-[16px] shrink-0 mt-px" />
                    <span>{submitError}</span>
                  </div>
                )}
                <div className="mt-4 text-xs text-secondary">
                  <span className="text-red-500">*</span> {t('common.requiredField')}
                </div>
              </form>
            </div>

            {/* Modal footer */}
            <div className="px-6 py-4 border-t border-bd bg-surface-2 flex justify-end gap-2 shrink-0">
              <button
                type="button"
                className="py-2 px-4 rounded-lg text-sm font-medium text-secondary border border-bd bg-surface hover:bg-surface-2 transition-colors cursor-pointer font-sans"
                onClick={() => setShowModal(false)}
              >
                {t('common.cancel')}
              </button>
              <button
                type="submit"
                form="crud-form"
                className="py-2 px-4 rounded-lg text-sm font-semibold bg-accent text-white hover:opacity-90 transition-opacity border-none cursor-pointer font-sans"
              >
                {editing ? t('common.save') : t('common.create')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
