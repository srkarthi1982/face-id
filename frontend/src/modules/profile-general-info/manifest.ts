import { HiOutlineUserCircle } from 'react-icons/hi2'
import type { ModuleManifest } from '../../infra/shared/types/permissions'
import UserProfileInfoPage from './UserProfileInfoPage'
// import ProfileGeneralInfoDefaultPage from './ProfileGeneralInfoDefaultPage'

const manifest: ModuleManifest = {
  i18n: 'nav.profileGeneralInfo.title',
  icon: HiOutlineUserCircle,
  path: '/profile-general-info',
  page: UserProfileInfoPage,
  permissions: ["hide:*"],
  order: 1,
}
export default manifest
