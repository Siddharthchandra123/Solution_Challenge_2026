import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { DatasetConfigurator } from "@/components/upload/dataset-configurator"

export default function DatasetUploadPage() {
  return (
    <DashboardLayout>
      <div className="flex-1 overflow-auto p-6 lg:p-8 flex items-center justify-center">
        <DatasetConfigurator />
      </div>
    </DashboardLayout>
  )
}
