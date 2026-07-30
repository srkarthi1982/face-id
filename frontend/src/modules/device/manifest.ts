import { HiMiniDeviceTablet } from 'react-icons/hi2'
import type { ModuleManifest } from '../../infra/shared/types/permissions'

const manifest: ModuleManifest = {
  i18n: 'nav.device.title',
  icon: HiMiniDeviceTablet,
  path: '/device',
  order: 15,
}
export default manifest
