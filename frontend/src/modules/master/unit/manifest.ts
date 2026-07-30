import type { FeatureManifest } from '../../../infra/shared/types/permissions'
import UnitPage from './UnitPage'

const manifest: FeatureManifest = {
    i18n: 'nav.master.units.title',
    path: 'units',
    page: UnitPage,
    order: 20,
}

export default manifest
