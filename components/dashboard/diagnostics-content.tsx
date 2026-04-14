"use client"

import { useState, useEffect } from "react"
import { Upload, FileText, Database, AlertCircle, CheckCircle2, Info, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts"

export function DiagnosticsContent() {
  const [dataQualityStats, setDataQualityStats] = useState<any[]>([])
  const [featureDistribution, setFeatureDistribution] = useState<any[]>([])
  const [protectedAttributes, setProtectedAttributes] = useState<any[]>([])
  const [warnings, setWarnings] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [datasetInfo, setDatasetInfo] = useState({ records: 0, feature_count: 0 })

  useEffect(() => {
    async function fetchData() {
      try {
        const resp = await fetch("http://127.0.0.1:8000/api/diagnostics")
        if (resp.ok) {
          const json = await resp.json()
          setDataQualityStats(json.quality_stats)
          setFeatureDistribution(json.feature_dist)
          setProtectedAttributes(json.protected_attributes)
          setWarnings(json.warnings)
          setDatasetInfo({ records: json.records, feature_count: json.feature_count })
        }
      } catch (err) {
        console.error("API Error")
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
          <h1 className="text-2xl font-bold text-foreground">Data Diagnostics</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Dataset quality analysis and protected attribute detection
          </p>
        </div>
        <Button className="bg-primary text-primary-foreground hover:bg-primary/90 glow-cyan">
          <Upload className="mr-2 h-4 w-4" />
          Upload New Dataset
        </Button>
      </div>

      {/* Dataset Info */}
      <div className="mb-6 glass rounded-xl p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/20">
            <Database className="h-6 w-6 text-primary" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-foreground">mock_income_dataset_v1.csv</h2>
            <p className="text-sm text-muted-foreground">{datasetInfo.records.toLocaleString()} records | {datasetInfo.feature_count} features | Indexed natively</p>
          </div>
          <div className="flex gap-2">
            <span className="inline-flex items-center rounded-full bg-success/20 px-3 py-1 text-xs font-semibold text-success">
              <CheckCircle2 className="mr-1 h-3 w-3" />
              Validated
            </span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex h-[400px] items-center justify-center rounded-xl glass w-full mb-6">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-muted-foreground">Ingesting Pandas metadata via FastAPI...</p>
          </div>
        </div>
      ) : (
        <>
      {/* Stats Grid */}
      <div className="mb-6 grid gap-6 md:grid-cols-3">
        {/* Data Quality Pie */}
        <div className="glass rounded-xl p-6">
          <h3 className="mb-4 text-sm font-semibold text-foreground">Data Completeness</h3>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={dataQualityStats}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  dataKey="value"
                  stroke="none"
                >
                  {dataQualityStats.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "oklch(0.18 0.02 260)",
                    border: "1px solid oklch(0.30 0.03 260)",
                    borderRadius: "8px",
                  }}
                  itemStyle={{ color: "oklch(0.95 0.01 260)" }}
                  labelStyle={{ color: "oklch(0.95 0.01 260)" }}
                  formatter={(value: number) => [`${value}%`, ""]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 flex justify-center gap-4">
            {dataQualityStats.map((stat) => (
              <div key={stat.name} className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full" style={{ backgroundColor: stat.color }} />
                <span className="text-xs text-muted-foreground">{stat.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Feature Distribution */}
        <div className="glass rounded-xl p-6 md:col-span-2">
          <h3 className="mb-4 text-sm font-semibold text-foreground">Feature Completeness</h3>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureDistribution} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.30 0.03 260)" horizontal={false} />
                <XAxis type="number" tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 11 }} />
                <YAxis
                  dataKey="feature"
                  type="category"
                  tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 11 }}
                  width={80}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "oklch(0.18 0.02 260)",
                    border: "1px solid oklch(0.30 0.03 260)",
                    borderRadius: "8px",
                  }}
                  itemStyle={{ color: "oklch(0.95 0.01 260)" }}
                  labelStyle={{ color: "oklch(0.95 0.01 260)" }}
                />
                <Bar dataKey="count" fill="oklch(0.75 0.15 195)" radius={[0, 4, 4, 0]} name="Records" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Protected Attributes */}
      <div className="glass rounded-xl p-6">
        <div className="mb-4 flex items-center gap-2">
          <h3 className="text-sm font-semibold text-foreground">Detected Protected Attributes</h3>
          <div className="group relative">
            <Info className="h-4 w-4 text-muted-foreground cursor-help" />
            <div className="absolute bottom-full left-1/2 mb-2 hidden -translate-x-1/2 whitespace-nowrap rounded-lg bg-popover px-3 py-2 text-xs text-popover-foreground shadow-lg group-hover:block">
              Attributes identified for fairness analysis
            </div>
          </div>
        </div>
        <div className="space-y-4">
          {protectedAttributes.map((attr) => (
            <div
              key={attr.attribute}
              className="flex flex-col gap-2 rounded-lg bg-secondary/50 p-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <p className="font-medium text-foreground">{attr.attribute}</p>
                <p className="text-xs text-muted-foreground">
                  Groups: {attr.groups.join(", ")}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-24 overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full bg-primary"
                      style={{ width: `${attr.coverage}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium text-foreground">{attr.coverage}%</span>
                </div>
                <span className="inline-flex items-center rounded-full bg-primary/20 px-2.5 py-0.5 text-xs font-semibold text-primary">
                  Detected
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
      <div className="mt-6 glass rounded-xl border-l-4 border-l-warning p-6">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-warning/20">
            <AlertCircle className="h-5 w-5 text-warning" />
          </div>
          <div>
            <p className="font-medium text-foreground">Potential Data Quality Issues</p>
            <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
              {warnings.map((w, idx) => (
                <li key={idx}>- {w}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
      )}
      </>
      )}
    </main>
  )
}
