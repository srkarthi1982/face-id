import { useShallow } from "zustand/react/shallow";
import { useProfileInfoStore } from "./store";
import { HiKey, HiOutlineBackward, HiOutlineExclamationCircle, HiOutlinePencilSquare, HiOutlineUserCircle } from "react-icons/hi2";
import { useI18n } from "../../infra/locales/I18nContext";
import SectionHeader from "../../infra/shared/components/SectionHeader";
import EmptyState from "../../infra/shared/components/EmptyState";
import React, { ChangeEvent, FormEvent, ReactNode, useCallback, useEffect, useState } from "react";
import useAuthStore, { refreshUserInfo, selectUser } from "../../infra/auth/useAuthStore";
import type { UserProfileUpdate } from "./store";
import { useLocation, useNavigate } from "react-router-dom";
import DateTimePicker from "../../infra/shared/components/DateTimePicker";
import { CountryLookup } from "../../infra/shared/components/CountryLookup";

function formatDate(strDate?: string | null): string {
    if (!strDate) return ''

    const date = new Date(strDate)
    const day = String(date.getDate()).padStart(2, '0');
    const month = date.toLocaleString('en-US', { month: 'short' });
    const year = date.getFullYear();
    return `${day}-${month}-${year}`
}

interface UserProfileCardProps {
    children: ReactNode
    title: string
    /** Grid placement / extra classes, e.g. "lg:col-span-3". */
    className?: string
    /** Override the body padding (e.g. "p-0" for edge-to-edge tables). */
    bodyClassName?: string
}

const UserProfileCard: React.FC<UserProfileCardProps> = ({ title, className = '', bodyClassName, children }) => {
    return (
        <div className={`card p-0 overflow-hidden flex flex-col ${className}`}>
            <div
                className="px-3.5 py-1.5 flex items-center gap-2 shrink-0"
                style={{ background: 'linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%)' }}
            >
                <p className="text-[11px] font-bold text-white uppercase tracking-[0.05em]">{title}</p>
            </div>
            <div className={bodyClassName ?? "flex flex-col gap-3 text-[13px] px-4 py-3 flex-1"}>
                {children}
            </div>
        </div>
    )
}

const CircularImage: React.FC<{ photo: string | null | undefined, fullName: string }> = ({ photo, fullName }) => {
    const names = fullName.trim().split(/\s+/);

    let firstLast = ''
    if (names.length > 0 && names[0].length > 0) {
        firstLast = `${names[0][0]}${names[names.length - 1][0]}`
    }

    return (
        <div className="w-[56px] h-[56px] rounded-full flex items-center justify-center overflow-hidden shrink-0"
            style={{ background: 'var(--navy)' }}
        >
            {!photo && <label className="text-[20px] font-bold text-white">{firstLast}</label>}
            {photo && (
                <img src={`data:image/png;base64,${photo}`} />
            )}
        </div>

    )
}

const LabelValueField: React.FC<{ label: string, value: string | null | undefined, separator?: string, valueClassName?: string }> = ({ label, value, separator = ":", valueClassName }) => {
    const labelClassName = 'w-[88px] shrink-0 text-start text-[10px] font-bold text-muted uppercase tracking-[0.04em]'
    const _valueClassName = 'text-[12px] text-primary leading-tight flex-1 min-w-0 truncate ' + (valueClassName ?? '')
    return (
        <div className="flex items-center gap-1.5">
            <div className={labelClassName}>{`${label}${separator}`}</div>
            <div className={_valueClassName} title={typeof value === 'string' ? value : undefined}>{value ? value : <span className="text-muted">—</span>}</div>
        </div>
    )
}

export default function UserProfileInfoPage() {
    const { t } = useI18n();
    const navigate = useNavigate();
    const activeUser = useAuthStore(selectUser);
    const refreshUser = useAuthStore(refreshUserInfo)
    const { user: forUser, toEdit } = useLocation().state || { user: null, toEdit: false }
    const user = forUser ?? activeUser
    const isFromOutside = !!forUser
    const isEditingForOtherUser = toEdit && forUser && forUser.username !== activeUser?.username

    const [editProfile, setEditProfile] = useState<boolean>(false);
    const [refresh, setRefresh] = useState<boolean>(false);
    const [changePassword, setChangePassword] = useState(false);

    const { userProfile, getProfileInfo, reset, isLoaded, update } = useProfileInfoStore(useShallow(s => ({
        userProfile: s.userProfile,
        isLoaded: s.isLoaded,
        getProfileInfo: s.getProfileInfo,
        reset: s.reset,
        update: s.update
    })))
    const { firstName, middleName, lastName, email, mobileNo, extNo, rank, command, qualification } = userProfile;

    const onEditClose = (refresh: boolean = false) => {
        setEditProfile(false);
        if (isEditingForOtherUser) {
            navigate(-1)
            return;
        }
        if (refresh) {
            (async () => await refreshUser())()
            setRefresh(r => !r)
        }
    }

    useEffect(() => {
        (async () => {
            if (user) {
                await getProfileInfo(user?.username)
                if (isEditingForOtherUser) {
                    setEditProfile(true)
                }
            }
        })()
        return () => reset()
    }, [refresh, isFromOutside])

    if (!user) {
        return null
    }

    const fullName = [firstName, middleName, lastName].filter(Boolean).join(' ') || ''

    return (
        <div className="flex flex-col gap-3 lg:h-full lg:min-h-0">
            <SectionHeader icon={<HiOutlineUserCircle />} title={t('nav.profileGeneralInfo.title')} divider={false} />
            <div className="card px-4 py-2.5 flex flex-wrap items-center gap-3 shrink-0">
                <CircularImage fullName={fullName} photo={null} />
                <div className="flex-1 min-w-0">
                    <h3 className="text-[16px] font-bold text-primary tracking-[-0.02em] uppercase">
                        {fullName}
                    </h3>
                    <p className="text-[13px] text-muted mt-0.5 flex gap-2 py-0.5 items-center">
                        {isLoaded && (
                            <>
                                <label>{qualification}</label>
                            </>
                        )}
                    </p>
                </div>
                {
                    !isFromOutside && (
                        <div className="flex items-center gap-2 ms-auto">
                            {
                                'LDAP' !== user.auth_provider && (
                                    <button
                                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-[7px] font-semibold text-sm bg-accent text-white hover:opacity-90 transition-opacity border-none cursor-pointer font-sans"
                                        onClick={() => setChangePassword(true)}
                                    >
                                        <HiKey className="text-[13px]" />
                                        {t("profile.changePassword")}
                                    </button>
                                )
                            }
                            <button
                                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-[7px] font-semibold text-sm bg-accent text-white hover:opacity-90 transition-opacity border-none cursor-pointer font-sans"
                                onClick={() => setEditProfile(true)}
                            >
                                <HiOutlinePencilSquare className="text-[13px]" />
                                {t("profile.editProfile")}
                            </button>
                        </div>
                    )
                }
                {
                    isFromOutside && !toEdit && (
                        <div className="flex items-center gap-2 ms-auto">
                            <button onClick={() => navigate(-1)}
                                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-[7px] font-semibold text-sm bg-accent text-white hover:opacity-90 transition-opacity border-none cursor-pointer font-sans">
                                <HiOutlineBackward /> Back
                            </button>
                        </div>
                    )
                }
            </div>
            <div className="flex flex-col gap-3">
                <UserProfileCard title={t("profile.basicInfo")} className="flex-1 min-w-0">
                    <div className="grid grid-cols-2 gap-x-3 gap-y-1.5 text-[13px]">
                        <LabelValueField label={t("profile.email")} value={email} />
                        <LabelValueField label={t("profile.mobileNo")} value={mobileNo} />
                        <LabelValueField label={t("profile.extNo")} value={extNo} />
                    </div>
                </UserProfileCard>
            </div>
            {editProfile && <EditProfileModal onClose={onEditClose} userId={user?.username} />}
            {changePassword && <ChangePasswordModal onClose={() => setChangePassword(false)} id={user?.id} />}
        </div >
    )
}


function EditProfileModal({ onClose, userId }: { onClose: (refresh: boolean) => void, userId: string | undefined }) {
    const { profile, update } = useProfileInfoStore(useShallow(s => ({
        profile: s.userProfile,
        update: s.update
    })))

    const [form, setForm] = useState<UserProfileUpdate>({
        profileId: profile.profileId,
        version: profile.version,
        firstName: profile.firstName ?? '',
        middleName: profile.middleName,
        lastName: profile.lastName ?? '',
        dateOfBirth: null
    });
    const [submitting, setSubmitting] = useState<boolean>(false)
    const [error, setError] = useState<string>()

    const updateField = useCallback<(fieldName: string) => (e: ChangeEvent<HTMLInputElement>) => void>((fieldName: string) => (e: ChangeEvent<HTMLInputElement>) => {
        setForm(prev => ({ ...prev, [fieldName]: e.target.value }))
    }, [])

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        (async () => {
            try {
                await update(form, userId!)
                onClose(true);
            } catch (e: any) {
                setError(e?.message || 'Failed to update user')
            } finally {
                setSubmitting(false)
            }
        })()
    }

    const inputClass =
        'w-full px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20'
    return (
        // Overlay
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => onClose(false)}>
            {/* Container */}
            <div className="bg-surface rounded-2xl border border-bd shadow-elevated w-[90%] max-w-lg max-h-[90vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
                {/* Title */}
                <div
                    className="px-4 py-4 flex items-center justify-between shrink-0"
                    style={{ background: 'linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%)' }}>
                    <div>
                        <p className="text-sm font-bold text-white ">Edit Profile</p>
                        <p className="text-xs text-white/50 mt-[3px]">{userId}</p>
                    </div>
                    <button className="text-white/50 hover:text-white text-xl leading-none border-none bg-transparent cursor-pointer" onClick={() => onClose(false)}>&times;</button>
                </div>
                <div className="p-6 overflow-y-auto flex-1">
                    <form id="edit-profile" className="flex flex-col gap-4" onSubmit={handleSubmit}>
                        <div>
                            <label className="block text-sm font-medium text-secondary mb-1">First Name</label>
                            <input className={inputClass} value={form.firstName} required onChange={updateField('firstName')} />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-secondary mb-1">Middle Name</label>
                            <input className={inputClass} value={form.middleName ?? ''} onChange={updateField('middleName')} />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-secondary mb-1">Last Name</label>
                            <input className={inputClass} value={form.lastName} required onChange={updateField('lastName')} />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-secondary mb-1">Date of Birth</label>
                            <DateTimePicker value={form.dateOfBirth ?? ''} onChange={value => setForm((prev) => ({ ...prev, dateOfBirth: value }))} dateOnly={true} required={true} />
                        </div>
                        {error && (
                            <div
                                className="flex items-start gap-2 px-3 py-2.5 rounded-lg bg-red-500/10 border border-red-500/20">
                                <HiOutlineExclamationCircle className="text-red-500 text-[15px] mt-px shrink-0" />
                                <p className="text-sm text-red-500">{error}</p>
                            </div>
                        )}
                    </form>
                </div>
                <div className="px-6 py-4 flex justify-end gap-2 border-t border-bd shrink-0">
                    <button
                        type="button"
                        onClick={() => onClose(false)}
                        className="px-4 py-2 rounded-[9px] text-sm font-semibold text-secondary bg-surface-2 border border-bd hover:bg-surface transition-colors cursor-pointer font-sans"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        form="edit-profile"
                        className="px-4 py-2 rounded-[9px] text-sm font-semibold text-white bg-accent hover:opacity-90 transition-opacity border-none cursor-pointer font-sans disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {!submitting ? 'Save Changes' : 'Saving...'}
                    </button>
                </div>

            </div>
        </div>
    )
}

function ChangePasswordModal({ onClose, id }: { onClose: (refresh: boolean) => void, id: number }) {
    const doChangePassword = useProfileInfoStore(useShallow(s => s.changePassword))

    const [form, setForm] = useState({
        oldPassword: '',
        newPassword1: '',
        newPassword2: ''
    })
    const [error, setError] = useState('')
    const [submitting, setSubmitting] = useState(false)

    const updateField = useCallback((name: string) => (e: ChangeEvent<HTMLInputElement>) => {
        setForm(prev => ({ ...prev, [name]: e.target.value }))
    }, [])

    const { oldPassword, newPassword1, newPassword2 } = form

    const handleSubmit = useCallback((e: FormEvent) => {
        e.preventDefault();
        setSubmitting(true);

        (async () => {
            try {
                await doChangePassword({ old_password: form.oldPassword, new_password: newPassword1 }, id)
                onClose(true)
            } catch (e: any) {
                setError(e.message || 'Failed to save changes')
            } finally {
                setSubmitting(false)
            }
        })()
    }, [oldPassword, newPassword1, doChangePassword])

    const validatePassword2 = useCallback(() => {
        if (!newPassword1 || !newPassword2) {
            setError('')
            return;
        }

        if (newPassword1 !== newPassword2) {
            setError("Password doesn't match");
            return;
        }

        if (newPassword1.length < 8) {
            setError("Password should have at least 8 characters");
            return;
        }
        setError('')
    }, [newPassword1, newPassword2])

    const inputClass =
        'w-full px-3 py-2 bg-surface-2 border border-bd rounded-lg text-primary text-sm focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20'
    return (
        // Overlay
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => onClose(false)}>
            {/* Container */}
            <div className="bg-surface rounded-2xl border border-bd shadow-elevated w-[90%] max-w-lg max-h-[90vh] overflow-hidden flex flex-col" onClick={e => e.stopPropagation()}>
                {/* Title */}
                <div
                    className="px-4 py-4 flex items-center justify-between shrink-0"
                    style={{ background: 'linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%)' }}>
                    <div>
                        <p className="text-sm font-bold text-white ">Change Password</p>
                    </div>
                    <button className="text-white/50 hover:text-white text-xl leading-none border-none bg-transparent cursor-pointer" onClick={() => onClose(false)}>&times;</button>
                </div>
                <div className="p-6 overflow-y-auto flex-1">
                    <form id="edit-profile" className="flex flex-col gap-4" onSubmit={handleSubmit}>
                        <div>
                            <label className="block text-sm font-medium text-secondary mb-1">Old Password</label>
                            <input
                                type="password"
                                value={form.oldPassword}
                                onChange={updateField('oldPassword')}
                                className={inputClass}
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-secondary mb-1">New Password</label>
                            <input
                                type="password"
                                value={form.newPassword1}
                                onChange={updateField('newPassword1')}
                                placeholder="Min 8 characters"
                                className={inputClass}
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-secondary mb-1">Confirm New Password</label>
                            <input
                                type="password"
                                value={form.newPassword2}
                                onChange={updateField('newPassword2')}
                                onBlur={validatePassword2}
                                className={inputClass}
                                required
                            />
                        </div>
                        {error && (
                            <div
                                className="flex items-start gap-2 px-3 py-2.5 rounded-lg bg-red-500/10 border border-red-500/20">
                                <HiOutlineExclamationCircle className="text-red-500 text-[15px] mt-px shrink-0" />
                                <p className="text-sm text-red-500">{error}</p>
                            </div>
                        )}
                    </form>
                </div>
                <div className="px-6 py-4 flex justify-end gap-2 border-t border-bd shrink-0">
                    <button
                        type="button"
                        onClick={() => onClose(false)}
                        className="px-4 py-2 rounded-[9px] text-sm font-semibold text-secondary bg-surface-2 border border-bd hover:bg-surface transition-colors cursor-pointer font-sans"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        form="edit-profile"
                        className="px-4 py-2 rounded-[9px] text-sm font-semibold text-white bg-accent hover:opacity-90 transition-opacity border-none cursor-pointer font-sans disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={!!submitting}
                    >
                        {!submitting ? 'Change Password' : 'Updating ...'}
                    </button>
                </div>

            </div>
        </div>
    )
}
