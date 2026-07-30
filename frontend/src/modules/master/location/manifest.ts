import type { FeatureManifest } from '../../../infra/shared/types/permissions'
import LocationPage from './LocationPage'

const manifest: FeatureManifest = {
    i18n: 'nav.master.locations.title',
    path: 'locations',
    page: LocationPage,
    order: 10,
}

export default manifest
