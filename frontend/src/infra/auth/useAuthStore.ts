import { create } from 'zustand'
import { client } from '../../api/client'
import {
  getMeApiV1AuthMeGet as getMe,
  loginApiV1AuthLoginPost as loginApi,
  registerApiV1AuthRegisterPost as registerApi,
} from '../../api/generated'
import type { UserResponse } from '../../api/generated'
import type { PermissionCode } from '../shared/types/permissions'

/**
 * Zustand store for managing authentication state, including user data,
 * login/logout flows, token management, and registration.
 */
interface AuthState {
  user: UserResponse | null
  loading: boolean
  permissions: ReadonlySet<PermissionCode>
  initialize: () => Promise<void>
  login: (username: string, password: string) => Promise<string>
  register: (email: string, username: string, password: string, fullName: string) => Promise<void>
  logout: () => void
  refreshUserInfo:() => Promise<void>
}

// Stable references — fresh `new Set()` from selectors break Zustand's
// getSnapshot identity check and triggers infinite re-renders.
const EMPTY_PERMS: ReadonlySet<PermissionCode> = new Set<PermissionCode>()


async function fetchPermissions(): Promise<ReadonlySet<PermissionCode>> {
  try {
    const { data } = await (client as any).get({
      url: '/api/v1/auth/me/permissions',
      headers: { 'Content-Type': 'application/json' },
    })
    const perms = (data as any)?.data as string[] | undefined
    if (!perms || perms.length === 0) return EMPTY_PERMS
    return new Set<PermissionCode>(perms as PermissionCode[])
  } catch {
    return EMPTY_PERMS
  }
}

const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: true,
  permissions: EMPTY_PERMS,

  initialize: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ loading: false })
      return
    }
    const { data, error } = await getMe()
    if (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ user: null, permissions: EMPTY_PERMS, loading: false })
    } else {
      const user = (data as any)?.data ?? null
      const permissions = user ? await fetchPermissions() : EMPTY_PERMS
      set({ user, permissions, loading: false })
    }
  },

  login: async (username, password):Promise<string> => {
    const { data, error } = await loginApi({ body: { username, password } } as any)
    if (error) throw error
    const tokens = data as any
    if(!tokens) return "REG_SUCCESS"

    if (tokens.access_token) {
      localStorage.setItem('access_token', tokens.access_token)
    }
    const me = await getMe()
    if (me.data) {
      const user = (me.data as any).data
      const permissions = await fetchPermissions()
      set({ user, permissions })
    }
    return "AUTH_SUCCESS"
  },

  register: async (email, username, password, fullName) => {
    const { error } = await registerApi({
      body: { email, username, password, full_name: fullName },
    })
    if (error) throw error
  },

  logout: () => {
    localStorage.removeItem('access_token')
    set({ user: null, permissions: EMPTY_PERMS })
    fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'include' }).catch(() => {})
  },

  refreshUserInfo: async () => {
    const me = await getMe()
    if (me.data) {
      const user = (me.data as any).data
      set({ user })
    }
  }
}))

export const selectUser = (state: AuthState) => state.user
export const selectLoading = (state: AuthState) => state.loading
export const selectIsAuthenticated = (state: AuthState) => !!state.user
export const refreshUserInfo = (s: AuthState) => s.refreshUserInfo

/**
 * Selector: set of permission codes the user is allowed to perform.
 * Backend source: GET /api/v1/auth/me/permissions.
 * Use this for any gating decision (sidebar, route guards, feature toggles).
 */
export const selectUserPermissions = (state: AuthState): ReadonlySet<PermissionCode> =>
  state.permissions

export const selectLogin = (state: AuthState) => state.login
export const selectLogout = (state: AuthState) => state.logout
export const selectRegister = (state: AuthState) => state.register
export const selectInitialize = (state: AuthState) => state.initialize

export default useAuthStore
