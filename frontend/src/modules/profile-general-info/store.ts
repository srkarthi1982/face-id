import { create } from "zustand"
import { extractErrorMessage } from "../../infra/shared/utils/apiError"
import { getProfileApiV1ProfileInfoUserIdGet, changePasswordApiV1UsersUserIdPasswdPut, updateProfileApiV1ProfileInfoPut } from "../../api/generated"

export interface UserProfileResponse {
    profileId: number
    version: number
    firstName: string
    middleName: string | null
    lastName: string
    dateOfBirth: string | null
    email: string
    mobileNo: string | null
    extNo: string | null
    rank: string
    command: string | null
    qualification: string | null
}

export interface UserProfileUpdate {
    profileId: number
    version: number
    firstName: string
    middleName: string | null
    lastName: string
    dateOfBirth: string | null
}

export interface PasswordChange {
    old_password: string
    new_password: string
}

interface ProfileInfoState {
    userProfile: UserProfileResponse
    isLoaded: boolean
    getProfileInfo: (userId: string) => Promise<void>
    reset: () => void
    update: (o: UserProfileUpdate, userId: string) => Promise<void>
    changePassword: (o: PasswordChange, id: number) => Promise<void>
}

const defaultUserProfile: UserProfileResponse = {
    profileId: 0,
    version: 0,
    firstName: '',
    middleName: null,
    lastName: '',
    dateOfBirth: null,
    email: '',
    mobileNo: null,
    extNo: null,
    rank: '',
    command: null,
    qualification: ''
}

export const useProfileInfoStore = create<ProfileInfoState>((set, get) => ({
    userProfile: defaultUserProfile,
    isLoaded: false,
    getProfileInfo: async (userId: string) => {
        try {
            const { data, error } = await getProfileApiV1ProfileInfoUserIdGet({
                path: { user_id: userId },
            })
            if (error) {
                throw new Error(extractErrorMessage(error))
            }
            if (data) {
                const mapped = data as any
                const d = mapped?.data
                if (d) {
                    set({
                        userProfile: {
                            profileId: d.profile_id,
                            version: d.version,
                            firstName: d.first_name,
                            middleName: d.middle_name ?? null,
                            lastName: d.last_name,
                            dateOfBirth: d.date_of_birth ?? null,
                            email: d.email,
                            mobileNo: d.mobile_no ?? null,
                            extNo: d.ext_no ?? null,
                            rank: d.rank,
                            command: d.command ?? null,
                            qualification: d.qualification ?? null,
                        },
                        isLoaded: true,
                    })
                }
            }
        } catch (e: any) {
            if (e?.message) throw e
        }
    },
    reset: () => {
        set({ userProfile: { ...defaultUserProfile }, isLoaded: false })
    },
    update: async (o: UserProfileUpdate, userId: string) => {
        try {
            const { data, error } = await updateProfileApiV1ProfileInfoPut({
                body: {
                    profile_id: o.profileId,
                    version: o.version,
                    first_name: o.firstName,
                    middle_name: o.middleName,
                    last_name: o.lastName,
                    date_of_birth: o.dateOfBirth,
                },
            })
            if (error) {
                throw new Error(extractErrorMessage(error))
            }
        } catch (e: any) {
            throw new Error(e?.message || 'Failed to update user')
        }
    },
    changePassword: async (o: PasswordChange, id: number) => {
        try {
            const { data, error } = await changePasswordApiV1UsersUserIdPasswdPut({
                path: { user_id: id },
                body: o,
            })
            if (error) {
                throw new Error(extractErrorMessage(error))
            }
        } catch (e: any) {
            throw new Error(e?.message || 'Failed to save changes')
        }
    }
}))
