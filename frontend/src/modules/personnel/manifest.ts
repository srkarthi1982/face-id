import { HiOutlineUserGroup } from 'react-icons/hi2'
import type { ModuleManifest } from '../../infra/shared/types/permissions'
import PersonnelPage from './PersonnelPage'

const manifest: ModuleManifest = {
  i18n: 'nav.personnel.title',
  icon: HiOutlineUserGroup,
  path: '/personnel',
  page: PersonnelPage,
  permissions: ['personnel:read'],
  order: 10,
}
export default manifest
