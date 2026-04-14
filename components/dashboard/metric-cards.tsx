"use client"

import { TrendingUp, AlertTriangle, CheckCircle2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface MetricCardProps {
  title: string
  value: string
  icon: React.ElementType
  status: "neutral" | "warning" | "success"
  description?: string
}

function MetricCard({ title, value, icon: Icon, status, description }: MetricCardProps) {
  return (
    <div className={cn(
      "glass rounded-xl p-6 transition-all duration-300 hover:scale-[1.02]",
      status === "success" && "border-l-4 border-l-success",
      status === "warning" && "border-l-4 border-l-warning",
      status === "neutral" && "border-l-4 border-l-primary"
    )}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className={cn(
              "text-3xl font-bold",
              status === "success" && "text-success",
              status === "warning" && "text-warning",
              status === "neutral" && "text-foreground"
            )}>
              {value}
            </span>
            {status === "warning" && <span className="text-2xl">🚨</span>}
            {status === "success" && <span className="text-2xl">✅</span>}
          </div>
          {description && (
            <p className="mt-2 text-xs text-muted-foreground">{description}</p>
          )}
        </div>
        <div className={cn(
          "flex h-12 w-12 items-center justify-center rounded-lg",
          status === "success" && "bg-success/20",
          status === "warning" && "bg-warning/20",
          status === "neutral" && "bg-primary/20"
        )}>
          <Icon className={cn(
            "h-6 w-6",
            status === "success" && "text-success",
            status === "warning" && "text-warning",
            status === "neutral" && "text-primary"
          )} />
        </div>
      </div>
    </div>
  )
}

interface MetricCardsProps {
  metrics: {
    base_acc: number
    base_dp: number
    mit_acc: number
    mit_dp: number
  } | null
}

export function MetricCards({ metrics }: MetricCardsProps) {
  // Safe defaults if API hasn't loaded
  const baseAccDisplay = metrics ? `${metrics.base_acc}%` : "..."
  const dpDisplay = metrics ? `${metrics.base_dp}` : "..."
  const optDpDisplay = metrics ? `${metrics.mit_dp}` : "..."

  return (
    <div className="grid gap-6 md:grid-cols-3">
      <MetricCard
        title="Baseline Accuracy"
        value={baseAccDisplay}
        icon={TrendingUp}
        status="neutral"
        description="Model performance on test set"
      />
      <MetricCard
        title="Demographic Parity Disparity"
        value={dpDisplay}
        icon={AlertTriangle}
        status="warning"
        description="Pre-mitigation fairness gap"
      />
      <MetricCard
        title="Optimized Parity"
        value={optDpDisplay}
        icon={CheckCircle2}
        status="success"
        description="Post-mitigation fairness gap"
      />
    </div>
  )
}
