"use client"

import { useState, useEffect } from "react"
import { Circle, AlertTriangle, CheckCircle2, Clock, RefreshCw, Pause, Play } from "lucide-react"
import { Button } from "@/components/ui/button"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts"
import { useConfig } from "@/hooks/use-config"

// Removed generic javascript data generator
// Fetches from Python Instead

const recentAlerts = [
  {
    id: 1,
    severity: "critical",
    message: "Disparity spike detected at 02:15 AM - threshold exceeded",
    time: "2 hours ago",
    resolved: false,
  },
  {
    id: 2,
    severity: "warning",
    message: "Model latency increased to 450ms (threshold: 300ms)",
    time: "4 hours ago",
    resolved: true,
  },
  {
    id: 3,
    severity: "info",
    message: "Weekly bias report generated and sent to compliance team",
    time: "6 hours ago",
    resolved: true,
  },
  {
    id: 4,
    severity: "warning",
    message: "Demographic drift detected in live data distribution",
    time: "12 hours ago",
    resolved: true,
  },
]

export function MonitorContent() {
  const [isLive, setIsLive] = useState(true)
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([])
  const [apiData, setApiData] = useState<any>(null)
  const [lastUpdated, setLastUpdated] = useState(new Date())
  const { config } = useConfig()

  const modelEndpoints = [
    { name: `${config.target_col.toLowerCase()}-classifier-v8.3`, status: "healthy", requests: "12.4k/hr", latency: "124ms" },
    { name: `${config.sensitive_col.toLowerCase()}-bias-auditor-v2.1`, status: "healthy", requests: "8.2k/hr", latency: "89ms" },
    { name: "feature-weights-v3.1", status: "degraded", requests: "5.1k/hr", latency: "342ms" },
  ]

  const fetchData = async () => {
    try {
      const resp = await fetch("http://127.0.0.1:8001/api/monitor")
      if (resp.ok) {
        const json = await resp.json()
        setApiData(json)
        setTimeSeriesData(json.timeseries)
        setLastUpdated(new Date())
      }
    } catch(err) {
      console.error("API offline")
    }
  }

  useEffect(() => {
    fetchData() // Initial fetch
    if (!isLive) return

    const interval = setInterval(() => {
      fetchData()
    }, 5000)

    return () => clearInterval(interval)
  }, [isLive])

  return (
    <main className="flex-1 overflow-auto p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Live Production Monitor</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Real-time fairness metrics and model health monitoring
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            Last updated: {lastUpdated.toLocaleTimeString()}
          </div>
          <Button
            variant={isLive ? "default" : "outline"}
            onClick={() => setIsLive(!isLive)}
            className={isLive ? "bg-success text-success-foreground hover:bg-success/90" : ""}
          >
            {isLive ? (
              <>
                <Pause className="mr-2 h-4 w-4" />
                Pause
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Resume
              </>
            )}
          </Button>
          <Button variant="outline" className="border-border">
            <RefreshCw className="mr-2 h-4 w-4" />
            Force Refresh
          </Button>
        </div>
      </div>

      {/* Status Banner */}
      <div className="mb-6 glass rounded-xl p-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Circle className="h-4 w-4 fill-success text-success animate-pulse" />
            </div>
            <span className="text-sm font-medium text-foreground">System Operational</span>
          </div>
          <div className="flex flex-wrap gap-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-foreground">99.97%</p>
              <p className="text-xs text-muted-foreground">Uptime (30d)</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-foreground">48.2k</p>
              <p className="text-xs text-muted-foreground">Predictions/hr</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-warning">{apiData?.current_skew || "0.05"}</p>
              <p className="text-xs text-muted-foreground">Attribution Drift</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-foreground">{apiData ? (apiData.current_accuracy * 100).toFixed(1) : "87.2"}%</p>
              <p className="text-xs text-muted-foreground">Accuracy</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="mb-6 grid gap-6 lg:grid-cols-2">
        {/* Disparity Over Time */}
        <div className="glass rounded-xl p-6">
          <h3 className="mb-2 text-lg font-semibold text-foreground">Vertex AI Feature Attribution Drift</h3>
          <p className="mb-4 text-sm text-muted-foreground">
            L-infinity distance threshold monitoring
          </p>
          <div className="h-[240px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.30 0.03 260)" />
                <XAxis
                  dataKey="time"
                  tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 10 }}
                  interval={3}
                />
                <YAxis
                  domain={[0, 0.25]}
                  tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 10 }}
                  tickFormatter={(value) => value.toFixed(2)}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "oklch(0.18 0.02 260)",
                    border: "1px solid oklch(0.30 0.03 260)",
                    borderRadius: "8px",
                  }}
                  itemStyle={{ color: "oklch(0.95 0.01 260)" }}
                  labelStyle={{ color: "oklch(0.95 0.01 260)" }}
                  formatter={(value: number) => [value.toFixed(3), "Disparity"]}
                />
                <ReferenceLine
                  y={0.1}
                  stroke="oklch(0.75 0.18 65)"
                  strokeDasharray="5 5"
                  label={{
                    value: "Threshold",
                    fill: "oklch(0.75 0.18 65)",
                    fontSize: 10,
                    position: "right",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="vertex_skew"
                  stroke="oklch(0.75 0.15 195)"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: "oklch(0.75 0.15 195)" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Model Accuracy Over Time */}
        <div className="glass rounded-xl p-6">
          <h3 className="mb-2 text-lg font-semibold text-foreground">Model Accuracy (24h)</h3>
          <p className="mb-4 text-sm text-muted-foreground">
            Prediction accuracy over time
          </p>
          <div className="h-[240px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.30 0.03 260)" />
                <XAxis
                  dataKey="time"
                  tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 10 }}
                  interval={3}
                />
                <YAxis
                  domain={[0.8, 1]}
                  tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 10 }}
                  tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "oklch(0.18 0.02 260)",
                    border: "1px solid oklch(0.30 0.03 260)",
                    borderRadius: "8px",
                  }}
                  itemStyle={{ color: "oklch(0.95 0.01 260)" }}
                  labelStyle={{ color: "oklch(0.95 0.01 260)" }}
                  formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, "Accuracy"]}
                />
                <Line
                  type="monotone"
                  dataKey="accuracy"
                  stroke="oklch(0.70 0.18 160)"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: "oklch(0.70 0.18 160)" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Model Endpoints */}
      <div className="mb-6 glass rounded-xl p-6">
        <h3 className="mb-4 text-lg font-semibold text-foreground">Model Endpoints</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="pb-3 text-left font-medium text-muted-foreground">Endpoint</th>
                <th className="pb-3 text-center font-medium text-muted-foreground">Status</th>
                <th className="pb-3 text-center font-medium text-muted-foreground">Requests</th>
                <th className="pb-3 text-center font-medium text-muted-foreground">Latency</th>
              </tr>
            </thead>
            <tbody>
              {modelEndpoints.map((endpoint) => (
                <tr key={endpoint.name} className="border-b border-border/50">
                  <td className="py-3 font-mono text-foreground">{endpoint.name}</td>
                  <td className="py-3 text-center">
                    <span
                      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                        endpoint.status === "healthy"
                          ? "bg-success/20 text-success"
                          : "bg-warning/20 text-warning"
                      }`}
                    >
                      <Circle
                        className={`h-2 w-2 ${
                          endpoint.status === "healthy" ? "fill-success" : "fill-warning"
                        }`}
                      />
                      {endpoint.status}
                    </span>
                  </td>
                  <td className="py-3 text-center text-muted-foreground">{endpoint.requests}</td>
                  <td className="py-3 text-center text-muted-foreground">{endpoint.latency}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="glass rounded-xl p-6">
        <h3 className="mb-4 text-lg font-semibold text-foreground">Recent Alerts</h3>
        <div className="space-y-3">
          {recentAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`flex items-start gap-4 rounded-lg p-4 ${
                alert.resolved ? "bg-secondary/30" : "bg-destructive/10 border border-destructive/30"
              }`}
            >
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                  alert.severity === "critical"
                    ? "bg-destructive/20"
                    : alert.severity === "warning"
                      ? "bg-warning/20"
                      : "bg-primary/20"
                }`}
              >
                {alert.severity === "critical" ? (
                  <AlertTriangle className="h-4 w-4 text-destructive" />
                ) : alert.severity === "warning" ? (
                  <AlertTriangle className="h-4 w-4 text-warning" />
                ) : (
                  <CheckCircle2 className="h-4 w-4 text-primary" />
                )}
              </div>
              <div className="flex-1">
                <p className={`text-sm ${alert.resolved ? "text-muted-foreground" : "text-foreground"}`}>
                  {alert.message}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">{alert.time}</p>
              </div>
              {alert.resolved && (
                <span className="inline-flex items-center rounded-full bg-success/20 px-2 py-0.5 text-xs font-semibold text-success">
                  Resolved
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
