import { useEffect } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import LoginPage from './infra/auth/LoginPage'
import RegisterPage from './infra/auth/RegisterPage'
import useAuthStore, {
  selectInitialize,
} from './infra/auth/useAuthStore'
import { MENU_CONFIG } from './infra/config/menu.config'
import { flattenRoutes } from './infra/shared/utils/menuUtils'
import ErrorBoundary from './infra/shared/components/ErrorBoundary'
import Layout from './infra/shared/components/Layout'
import ModuleRedirect from './infra/shared/components/ModuleRedirect'
import ProtectedRoute from './infra/shared/components/ProtectedRoute'
import PermissionGuard from './infra/shared/components/PermissionGuard'
import UnauthorizedPage from './infra/shared/pages/UnauthorizedPage'
import NotFoundPage from './infra/shared/pages/NotFoundPage'
import DesignSystemPage from './modules/profile-general-info/design-system/DesignSystemPage'
import ToastContainer from './infra/shared/components/NotificationToastContainer'
import TopLoadingBar from './infra/shared/components/TopLoadingBar'

const allRoutes = flattenRoutes(MENU_CONFIG)

export default function App() {
  const initialize = useAuthStore(selectInitialize)

  useEffect(() => {
    initialize()
  }, [initialize])

  return (
    <ErrorBoundary>
      <TopLoadingBar />
      <ToastContainer></ToastContainer>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          {/* Hidden static routes */}
          <Route path="/" element={<Navigate to="/device" replace />} />
          {/* Access Denied renders inside the layout (sidebar stays visible) so a
              denied route only swaps the content area, not the whole screen. */}
          <Route path="/unauthorized" element={<UnauthorizedPage />} />
          <Route
            path="/design-system"
            element={
              <ErrorBoundary>
                <PermissionGuard >
                  <DesignSystemPage />
                </PermissionGuard>
              </ErrorBoundary>
            }
          />
          {/* Generated routes from MENU_CONFIG */}
          {allRoutes.map((route) => {
            const element =
              route.kind === 'module-redirect'
                ? <ModuleRedirect
                    basePath={route.basePath}
                    children={route.children}
                    parentPermissions={route.parentPermissions}
                  />
                : <route.page />

            const needsGuard = route.kind === 'page' && !!route.permissions?.length
            const guarded = needsGuard
              ? <PermissionGuard permissions={route.permissions}>{element}</PermissionGuard>
              : element

            return (
              <Route
                key={route.path}
                path={route.path}
                element={<ErrorBoundary>{guarded}</ErrorBoundary>}
              />
            )
          })}

          {/* Legacy alias redirect */}
          <Route path="/common/dashboard" element={<Navigate to="/" replace />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  )
}
