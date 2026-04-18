"use client"

import { useState, useEffect } from "react"
import { Info, ChevronDown, ChevronUp, Lightbulb, Loader2, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts"
import { useConfig } from "@/hooks/use-config"

export function ShapContent() {
  const [expandedSection, setExpandedSection] = useState<string | null>("global")
  const [apiData, setApiData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const { config } = useConfig()

  const fetchData = async () => {
    setLoading(true)
    try {
      const response = await fetch("http://127.0.0.1:8001/api/shap")
      if (response.ok) {
        const json = await response.json()
        setApiData(json)
      }
    } catch (err: any) {
      console.error("SHAP API Offline")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  return (
    <main className="flex-1 overflow-auto p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">LIT Visualization Engine</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Google Learning Interpretability Tool (LIT) interface for '{config.target_col}' predictions
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="border-border" onClick={fetchData}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh Analysis
          </Button>
          <Button variant="outline" className="border-border">
            <Info className="mr-2 h-4 w-4" />
            What is LIT?
          </Button>
        </div>
      </div>

      {/* Info Banner */}
      <div className="mb-6 glass rounded-xl border-l-4 border-l-primary p-6">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/20">
            <Lightbulb className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="font-medium text-foreground">Learning Interpretability Tool (LIT) Mechanics</p>
            <p className="mt-1 text-sm text-muted-foreground">
              LIT evaluates model behavior using exact feature attributions. Positive arrows push toward one class, negative arrows push toward the opposite class. Interactive "What-If" counterfactuals are simulated on demand.
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex h-[400px] items-center justify-center rounded-xl glass">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-muted-foreground">Booting Google LIT Dependencies...</p>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Global SHAP */}
          <div className="mb-6 glass rounded-xl overflow-hidden">
            <button
              onClick={() => toggleSection("global")}
              className="flex w-full items-center justify-between p-6 text-left"
            >
              <div>
                <h3 className="text-lg font-semibold text-foreground">Global Feature Importance</h3>
                <p className="text-sm text-muted-foreground">
                  Average impact of each historical feature across all Income predictions
                </p>
              </div>
              {expandedSection === "global" ? (
                <ChevronUp className="h-5 w-5 text-muted-foreground" />
              ) : (
                <ChevronDown className="h-5 w-5 text-muted-foreground" />
              )}
            </button>
            {expandedSection === "global" && (
              <div className="border-t border-border p-6">
                <div className="h-[320px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={apiData?.global || []} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.30 0.03 260)" horizontal={false} />
                      <XAxis
                        type="number"
                        domain={[-0.25, 0.4]}
                        tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 11 }}
                        tickFormatter={(value) => value.toFixed(2)}
                      />
                      <YAxis
                        dataKey="feature"
                        type="category"
                        tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 11 }}
                        width={120}
                      />
                      <Tooltip
                        cursor={{ fill: "oklch(0.269 0 0)" }}
                        contentStyle={{
                          backgroundColor: "oklch(0.18 0.02 260)",
                          border: "1px solid oklch(0.30 0.03 260)",
                          borderRadius: "8px",
                        }}
                        itemStyle={{ color: "oklch(0.95 0.01 260)" }}
                        labelStyle={{ color: "oklch(0.95 0.01 260)" }}
                        formatter={(value: number) => [value.toFixed(3), "SHAP Impact"]}
                      />
                      <ReferenceLine x={0} stroke="oklch(0.50 0.02 260)" strokeWidth={2} />
                      <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                        {(apiData?.global || []).map((entry: any, index: number) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={
                              entry.direction === "positive"
                                ? "oklch(0.70 0.18 160)" // Green tint
                                : "oklch(0.55 0.22 30)"  // Red tint
                            }
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  )
}
