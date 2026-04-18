"use client"

import { AlertTriangle, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

export function AlertPanel({ config }: { config?: { target_col: string, sensitive_col: string } }) {
  const sensitive = config?.sensitive_col || "Sex"
  return (
    <div className="glass rounded-xl border-l-4 border-l-warning p-6">
      <div className="flex flex-col lg:flex-row lg:items-center gap-4">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-warning/20">
          <AlertTriangle className="h-6 w-6 text-warning" />
        </div>
        
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center rounded-full bg-warning/20 px-2.5 py-0.5 text-xs font-semibold text-warning">
              Action Required
            </span>
          </div>
          <p className="text-sm text-foreground leading-relaxed">
            The current baseline model exhibits high proxy correlation. The
            Post-Processing Threshold Optimizer has actively redefined decision
            boundaries to enforce '{sensitive}' demographic parity.
          </p>
          <p className="text-xs text-muted-foreground">
            Review the correlation matrix and consider feature exclusion or reweighting strategies.
          </p>
        </div>

        <div className="flex shrink-0 gap-3">
          <Button variant="outline" className="border-warning/50 text-warning hover:bg-warning/10 hover:text-warning">
            View Details
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
