import type { FeatureManifest } from '../../../infra/shared/types/permissions'
import TimingPage from './TimingPage'

const manifest: FeatureManifest = {
    i18n: 'nav.master.timings.title',
    path: 'timings',
    page: TimingPage,
    order: 30,
    permissions: ['timing:read'],
}

export default manifest
