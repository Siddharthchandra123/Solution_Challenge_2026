"use client"

import { useState, useEffect } from "react"
import { Filter, RefreshCw, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
} from "recharts"

export function ExplorerContent() {
  const [scatterData, setScatterData] = useState<any[]>([])
  const [correlations, setCorrelations] = useState<any[]>([])
  const [insights, setInsights] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      const resp = await fetch("http://127.0.0.1:8000/api/explorer")
      if (resp.ok) {
        const json = await resp.json()
        setScatterData(json.scatter_data)
        setCorrelations(json.correlations)
        setInsights(json.insights)
      }
    } catch(err) {
      console.error("API offline")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <main className="flex-1 overflow-auto p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Bivariate Explorer</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Explore predictive relationships and detect hidden Proxy Variables
          </p>
        </div>
        <Button variant="outline" className="border-border" onClick={fetchData}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh Analysis
        </Button>
      </div>

      {/* Controls (Locked for MVP) */}
      <div className="mb-6 glass rounded-xl p-6">
        <div className="flex items-center gap-2 mb-2">
          <Filter className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium text-foreground">Active Configuration</span>
        </div>
        <p className="text-sm text-muted-foreground">
           Currently mapping: <b>Experience</b> (X-Axis) vs <b>Income Score Model</b> (Y-Axis), segregated by <b>Sex</b> (Grouping).
        </p>
      </div>

      {loading ? (
        <div className="flex h-[400px] items-center justify-center rounded-xl glass w-full mb-6">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-muted-foreground">Calculating Cramer's V Contingency Arrays...</p>
          </div>
        </div>
      ) : (
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Scatter Plot */}
        <div className="glass rounded-xl p-6">
          <h3 className="mb-2 text-lg font-semibold text-foreground">
            Experience vs Target By Demographic
          </h3>
          <p className="mb-4 text-sm text-muted-foreground">
            Visual representation of outcome disparities across protected groups
          </p>
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.30 0.03 260)" />
                <XAxis
                  type="number"
                  dataKey="x"
                  name="Experience (Years)"
                  tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 11 }}
                  label={{
                    value: "Experience (Years)",
                    position: "bottom",
                    fill: "oklch(0.65 0.02 260)",
                    fontSize: 12,
                  }}
                />
                <YAxis
                  type="number"
                  dataKey="y"
                  name="Income Score"
                  domain={[-10, 25]}
                  tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 11 }}
                  label={{
                    value: "Income Score",
                    angle: -90,
                    position: "insideLeft",
                    fill: "oklch(0.65 0.02 260)",
                    fontSize: 12,
                  }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "oklch(0.18 0.02 260)",
                    border: "1px solid oklch(0.30 0.03 260)",
                    borderRadius: "8px",
                  }}
                  itemStyle={{ color: "oklch(0.95 0.01 260)" }}
                  labelStyle={{ color: "oklch(0.95 0.01 260)" }}
                  formatter={(value: number, name: string) => [
                    value,
                    name,
                  ]}
                />
                <Legend
                  wrapperStyle={{ paddingTop: "16px" }}
                  formatter={(value) => <span style={{ color: "oklch(0.65 0.02 260)" }}>{value}</span>}
                />
                <Scatter name="Male" data={scatterData.filter((d) => d.group === "Male")}>
                  {scatterData
                    .filter((d) => d.group === "Male")
                    .map((entry, index) => (
                      <Cell key={`cell-m-${index}`} fill="oklch(0.75 0.15 195)" fillOpacity={0.7} />
                    ))}
                </Scatter>
                <Scatter name="Female" data={scatterData.filter((d) => d.group === "Female")}>
                  {scatterData
                    .filter((d) => d.group === "Female")
                    .map((entry, index) => (
                      <Cell key={`cell-f-${index}`} fill="oklch(0.65 0.22 30)" fillOpacity={0.7} />
                    ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Correlation Matrix */}
        <div className="glass rounded-xl p-6">
          <h3 className="mb-2 text-lg font-semibold text-foreground">Feature Correlations</h3>
          <p className="mb-4 text-sm text-muted-foreground">
            Pearson & Cramer's V Coefficients between variables
          </p>
          <div className="space-y-3">
            {correlations.map((item, index) => (
              <div key={index} className="flex items-center gap-4">
                <div className="w-40 text-sm text-muted-foreground truncate">
                  {item.feature1} &rarr; {item.feature2}
                </div>
                <div className="flex-1">
                  <div className="h-3 overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full transition-all duration-500"
                      style={{
                        width: `${item.correlation * 100}%`,
                        backgroundColor:
                          item.correlation > 0.5
                            ? "oklch(0.75 0.18 65)"
                            : "oklch(0.75 0.15 195)",
                      }}
                    />
                  </div>
                </div>
                <span
                  className={`w-12 text-right text-sm font-semibold ${
                    item.correlation > 0.5 ? "text-warning" : "text-foreground"
                  }`}
                >
                  {item.correlation.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
          
          {insights.map((insight, idx) => (
            <div key={`insight-${idx}`} className={`mt-6 rounded-lg border p-4 ${insight.type === 'warning' ? 'bg-warning/10 border-warning/30' : 'bg-destructive/10 border-destructive/30'}`}>
              <p className={`text-sm font-medium ${insight.type === 'warning' ? 'text-warning' : 'text-destructive'}`}>Automatic Proxy Scanner</p>
              <p className="mt-1 text-xs text-muted-foreground">
                {insight.message}
              </p>
            </div>
          ))}
        </div>
      </div>
      )}

      {/* Summary Stats */}
      <div className="mt-6 grid gap-4 sm:grid-cols-4">
        {[
          { label: "Disparity Ratio", value: "1.48x", status: "warning" },
          { label: "Statistical Parity", value: "0.24", status: "warning" },
          { label: "Equal Opportunity", value: "0.18", status: "warning" },
          { label: "Calibration Error", value: "0.06", status: "success" },
        ].map((stat) => (
          <div key={stat.label} className="glass rounded-xl p-4">
            <p className="text-xs text-muted-foreground">{stat.label}</p>
            <p
              className={`mt-1 text-2xl font-bold ${
                stat.status === "warning" ? "text-warning" : "text-success"
              }`}
            >
              {stat.value}
            </p>
          </div>
        ))}
      </div>
    </main>
  )
}
