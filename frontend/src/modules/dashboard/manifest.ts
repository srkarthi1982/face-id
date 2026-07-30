import { HiMiniCubeTransparent } from 'react-icons/hi2'
import type { ModuleManifest } from '../../infra/shared/types/permissions'
import DashboardPage from './DashboardPage'

const manifest: ModuleManifest = {
  i18n: 'nav.dashboard.title',
  icon: HiMiniCubeTransparent,
  path: '/dashboard',
  page: DashboardPage,
  order: 0,
}
export default manifest
