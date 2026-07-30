import type { FeatureManifest } from '../../../infra/shared/types/permissions'
import DeviceManagementPage from './DeviceManagementPage'

const manifest: FeatureManifest = {
    i18n: 'nav.device.devices.title',
    path: 'device-management',
    order: 10,
    page: DeviceManagementPage,
}
export default manifest
