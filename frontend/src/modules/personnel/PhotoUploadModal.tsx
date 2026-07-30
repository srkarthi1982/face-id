import { useEffect, useRef, useState } from 'react'
import { HiOutlineCamera, HiOutlineExclamationCircle } from 'react-icons/hi2'
import { useI18n } from '../../infra/locales/I18nContext'
import useToastStore from '../../infra/shared/store/useToastStore'
import type { PersonnelItem } from './store'

const ALLOWED_TYPES = ['image/jpeg', 'image/png']
const MAX_BYTES = 5 * 1024 * 1024

interface PhotoInfo {
    id: number
    device_id: number | null
    has_image: boolean
}

// Multipart upload and binary image download are not covered by the generated
// JSON client, so this modal talks to the API with fetch + the stored token.
function authHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token')
    return token ? { Authorization: `Bearer ${token}` } : {}
}

interface PhotoUploadModalProps {
    person: PersonnelItem
    onClose: () => void
}

export default function PhotoUploadModal({ person, onClose }: PhotoUploadModalProps) {
    const { t } = useI18n()
    const [currentUrl, setCurrentUrl] = useState<string | null>(null)
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [isUploading, setIsUploading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const fileInputRef = useRef<HTMLInputElement | null>(null)

    const loadCurrentPhoto = async () => {
        if (!person.person_id_internal) {
            setIsLoading(false)
            return
        }
        setIsLoading(true)
        try {
            const res = await fetch(
                `/api/v1/photo/?person_id=${encodeURIComponent(person.person_id_internal)}&page_size=50`,
                { headers: authHeaders() },
            )
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            const json = await res.json() as { data?: PhotoInfo[] }
            const photos = json.data ?? []
            const master = photos.find((p) => p.device_id === null && p.has_image)
                ?? photos.find((p) => p.has_image)
            if (master) {
                const imgRes = await fetch(`/api/v1/photo/${master.id}/image`, { headers: authHeaders() })
                if (imgRes.ok) {
                    const blob = await imgRes.blob()
                    setCurrentUrl((prev) => {
                        if (prev) URL.revokeObjectURL(prev)
                        return URL.createObjectURL(blob)
                    })
                }
            }
        } catch {
            // No current photo to show — the upload flow still works.
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        loadCurrentPhoto()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [person.person_id_internal])

    useEffect(() => () => {
        if (currentUrl) URL.revokeObjectURL(currentUrl)
        if (previewUrl) URL.revokeObjectURL(previewUrl)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    const handleFileChange = (files: FileList | null) => {
        setError(null)
        const file = files?.[0]
        if (!file) return
        if (!ALLOWED_TYPES.includes(file.type)) {
            setError(t('nav.personnel.photo.invalidType'))
            return
        }
        if (file.size > MAX_BYTES) {
            setError(t('nav.personnel.photo.tooLarge'))
            return
        }
        setSelectedFile(file)
        setPreviewUrl((prev) => {
            if (prev) URL.revokeObjectURL(prev)
            return URL.createObjectURL(file)
        })
    }

    const handleUpload = async () => {
        if (!selectedFile || !person.person_id_internal) return
        setIsUploading(true)
        setError(null)
        try {
            const formData = new FormData()
            formData.append('file', selectedFile)
            formData.append('person_id_internal', person.person_id_internal)
            const res = await fetch('/api/v1/photo/upload', {
                method: 'POST',
                headers: authHeaders(),
                body: formData,
            })
            if (!res.ok) {
                let detail = `HTTP ${res.status}`
                try {
                    const json = await res.json()
                    detail = json?.detail || json?.error?.message || detail
                } catch { /* non-JSON body */ }
                throw new Error(detail)
            }
            useToastStore.getState().push({ variant: 'success', title: t('nav.personnel.photo.success') })
            setSelectedFile(null)
            setPreviewUrl((prev) => {
                if (prev) URL.revokeObjectURL(prev)
                return null
            })
            if (fileInputRef.current) fileInputRef.current.value = ''
            await loadCurrentPhoto()
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Upload failed')
        } finally {
            setIsUploading(false)
        }
    }

    const shownUrl = previewUrl ?? currentUrl

    return (
        <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={onClose}
        >
            <div
                className="bg-surface rounded-2xl border border-bd shadow-elevated w-[90%] max-w-md overflow-hidden flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div
                    className="px-6 py-4 flex items-center gap-2.5 shrink-0"
                    style={{ background: 'linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%)' }}
                >
                    <HiOutlineCamera className="text-[18px] text-white/80" />
                    <div>
                        <p className="text-[13px] font-bold text-white">{t('nav.personnel.photo.title')}</p>
                        <p className="text-[11px] text-white/50 mt-px">{person.full_name} · {person.emp_no}</p>
                    </div>
                </div>

                {/* Body */}
                <div className="p-6 flex flex-col items-center gap-4">
                    <div className="w-40 h-40 rounded-xl border border-bd bg-surface-2 overflow-hidden flex items-center justify-center">
                        {isLoading ? (
                            <span className="text-xs text-muted">…</span>
                        ) : shownUrl ? (
                            <img src={shownUrl} alt={person.full_name} className="w-full h-full object-cover" />
                        ) : (
                            <span className="text-xs text-muted text-center px-3">{t('nav.personnel.photo.noPhoto')}</span>
                        )}
                    </div>

                    <p className="text-xs text-secondary text-center">{t('nav.personnel.photo.replaceHint')}</p>

                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/jpeg,image/png"
                        onChange={(e) => handleFileChange(e.target.files)}
                        className="block w-full text-sm text-secondary file:me-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-accent file:text-white file:cursor-pointer hover:file:opacity-90"
                    />

                    {error && (
                        <div className="w-full flex items-start gap-2 px-3 py-2.5 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
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
                        onClick={onClose}
                    >
                        {t('common.cancel')}
                    </button>
                    <button
                        type="button"
                        disabled={!selectedFile || isUploading}
                        className="py-2 px-4 rounded-lg text-sm font-semibold bg-accent text-white hover:opacity-90 transition-opacity border-none cursor-pointer font-sans disabled:opacity-50 disabled:cursor-not-allowed"
                        onClick={handleUpload}
                    >
                        {isUploading ? t('nav.personnel.photo.uploading') : t('nav.personnel.photo.upload')}
                    </button>
                </div>
            </div>
        </div>
    )
}
