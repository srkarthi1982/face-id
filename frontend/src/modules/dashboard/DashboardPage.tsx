import { HiMiniCubeTransparent } from 'react-icons/hi2'
import SectionHeader from '../../infra/shared/components/SectionHeader'
import { useI18n } from '../../infra/locales/I18nContext'

export default function DashboardPage() {
  const { t } = useI18n()

  return (
    <div className="flex flex-col gap-3">
      <SectionHeader
        icon={<HiMiniCubeTransparent />}
        title={t('nav.dashboard.title')}
      />
    </div>
  )
}
