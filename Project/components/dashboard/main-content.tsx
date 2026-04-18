"use client"

import { useState, useEffect } from "react"
import { Download, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { MetricCards } from "./metric-cards"
import { BiasCharts } from "./bias-charts"
import { AlertPanel } from "./alert-panel"
import { useConfig } from "@/hooks/use-config"

export function MainContent() {
  const [apiData, setApiData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { config } = useConfig()

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch("http://localhost:8001/api/mitigate")
        if (!response.ok) throw new Error("Failed to fetch API")
        const json = await response.json()
        setApiData(json)
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  return (
    <main className="flex-1 overflow-auto p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">
            Algorithmic Mitigation & Audit
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Enforcing parity for protected attribute '{config.sensitive_col}' on '{config.target_col}' predictions
          </p>
        </div>
        <Button className="bg-primary text-primary-foreground hover:bg-primary/90 glow-cyan">
          <Download className="mr-2 h-4 w-4" />
          Export Compliance Report
        </Button>
      </div>

      {loading ? (
        <div className="flex h-[400px] items-center justify-center rounded-xl glass">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-muted-foreground">Running Threshold Optimizer algorithms via Python API...</p>
          </div>
        </div>
      ) : error ? (
        <div className="flex h-[400px] items-center justify-center rounded-xl glass border border-destructive/50">
          <p className="text-destructive">Backend API Offline. Did you run <code className="bg-background px-1 py-0.5 rounded">uvicorn api:app</code>?</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Metric Cards */}
          <MetricCards metrics={apiData?.metrics} />

          {/* Charts */}
          <BiasCharts 
            chartsBefore={apiData?.charts_before || []} 
            chartsAfter={apiData?.charts_after || []} 
          />

          {/* Alert Panel */}
          <AlertPanel config={config} />
        </div>
      )}
    </main>
  )
}
