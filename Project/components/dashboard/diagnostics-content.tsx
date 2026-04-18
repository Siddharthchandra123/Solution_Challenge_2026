"use client"

import { useState, useEffect } from "react"
import { Upload, FileText, Database, AlertCircle, CheckCircle2, Info, Loader2, Shield, TrendingUp, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts"
import { useConfig } from "@/hooks/use-config"

export function DiagnosticsContent() {
  const [dataQualityStats, setDataQualityStats] = useState<any[]>([])
  const [featureDistribution, setFeatureDistribution] = useState<any[]>([])
  const [protectedAttributes, setProtectedAttributes] = useState<any[]>([])
  const [warnings, setWarnings] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [datasetInfo, setDatasetInfo] = useState({ records: 0, feature_count: 0 })
  const [auditResults, setAuditResults] = useState<any>(null)
  const [auditLoading, setAuditLoading] = useState(false)
  const [modelCard, setModelCard] = useState<any>(null)
  const [cardLoading, setCardLoading] = useState(false)
  const { config } = useConfig()

  useEffect(() => {
    async function fetchData() {
      try {
        const resp = await fetch("http://127.0.0.1:8001/api/diagnostics")
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

  const generateModelCard = async () => {
    setCardLoading(true)
    try {
      const resp = await fetch("http://127.0.0.1:8001/api/model-card")
      if (resp.ok) {
        const json = await resp.json()
        setModelCard(json)
      }
    } catch (err) {
      console.error("Model Card API Error")
    } finally {
      setCardLoading(false)
    }
  }

  const runAudit = async () => {
    setAuditLoading(true)
    try {
      const resp = await fetch("http://127.0.0.1:8001/api/audit")
      if (resp.ok) {
        const json = await resp.json()
        setAuditResults(json)
      }
    } catch (err) {
      console.error("Audit API Error")
    } finally {
      setAuditLoading(false)
    }
  }
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
            <h2 className="text-lg font-semibold text-foreground">Project Dataset File</h2>
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

      {/* Model Cards Section */}
      <div className="mt-8 glass rounded-xl p-6 border border-primary/20">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold text-foreground">Google Model Card Generator</h2>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Automatically synthesize unstructured metadata into a standard JSON transparency report
            </p>
          </div>
          <Button
            onClick={generateModelCard}
            disabled={cardLoading}
            variant="outline"
            className="border-primary/50 text-foreground hover:bg-primary/10"
          >
            {cardLoading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <FileText className="mr-2 h-4 w-4" />
            )}
            Generate Card
          </Button>
        </div>
        
        {modelCard && (
          <div className="relative mt-4">
            <pre className="overflow-auto rounded-lg bg-background/50 p-4 font-mono text-xs text-primary border border-border">
              <code>{JSON.stringify(modelCard, null, 2)}</code>
            </pre>
            <div className="absolute right-4 top-4">
              <Button size="sm" className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold">
                Download .json
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Audit Engine Section */}
      <div className="mt-8 glass rounded-xl p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-foreground">AI Audit Engine</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Comprehensive fairness analysis with TFDV and Vertex AI integration
            </p>
          </div>
          <Button
            onClick={runAudit}
            disabled={auditLoading}
            className="bg-primary text-primary-foreground hover:bg-primary/90 glow-cyan"
          >
            {auditLoading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Shield className="mr-2 h-4 w-4" />
            )}
            Run Audit
          </Button>
        </div>

        {auditResults && (
          <div className="space-y-6">
            {/* Fairness Metrics */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="glass rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Disparate Impact</p>
                    <p className="text-2xl font-bold text-primary">
                      {auditResults.fairness_metrics.disparate_impact}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Target range: 0.8 - 1.25
                    </p>
                  </div>
                </div>
              </div>
              <div className="glass rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Recall Difference</p>
                    <p className="text-2xl font-bold text-primary">
                      {auditResults.fairness_metrics.recall_difference}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Equal Opportunity metric
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Group Statistics */}
            <div className="glass rounded-lg p-4">
              <h3 className="mb-4 text-sm font-semibold text-foreground">Group Statistics</h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-sm text-muted-foreground">Privileged Group ({config.sensitive_col})</p>
                  <div className="mt-2 space-y-1">
                    <p className="text-xs">Count: {auditResults.group_statistics.privileged_count}</p>
                    <p className="text-xs">Positive Rate: {(auditResults.group_statistics.privileged_positive_rate * 100).toFixed(1)}%</p>
                    <p className="text-xs">Recall: {(auditResults.group_statistics.privileged_recall * 100).toFixed(1)}%</p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Unprivileged Group ({config.sensitive_col})</p>
                  <div className="mt-2 space-y-1">
                    <p className="text-xs">Count: {auditResults.group_statistics.unprivileged_count}</p>
                    <p className="text-xs">Positive Rate: {(auditResults.group_statistics.unprivileged_positive_rate * 100).toFixed(1)}%</p>
                    <p className="text-xs">Recall: {(auditResults.group_statistics.unprivileged_recall * 100).toFixed(1)}%</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Data Validation */}
            <div className="glass rounded-lg p-4">
              <h3 className="mb-4 text-sm font-semibold text-foreground">Data Validation (TFDV)</h3>
              <div className="flex items-center gap-3">
                {auditResults.data_validation.has_anomalies ? (
                  <AlertTriangle className="h-5 w-5 text-warning" />
                ) : (
                  <CheckCircle2 className="h-5 w-5 text-success" />
                )}
                <div>
                  <p className="text-sm font-medium text-foreground">
                    {auditResults.data_validation.anomaly_count} anomalies detected
                  </p>
                  <p className="text-xs text-muted-foreground">
                    TensorFlow Data Validation analysis
                  </p>
                </div>
              </div>
            </div>

            {/* Skew Detection */}
            <div className="glass rounded-lg p-4">
              <h3 className="mb-4 text-sm font-semibold text-foreground">Skew Detection (Vertex AI)</h3>
              <div className="flex items-center gap-3">
                <Shield className="h-5 w-5 text-primary" />
                <div>
                  <p className="text-sm font-medium text-foreground">
                    {auditResults.skew_detection.status || 'Not configured'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Production data monitoring setup
                  </p>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="glass rounded-lg p-4">
              <h3 className="mb-4 text-sm font-semibold text-foreground">Audit Recommendations</h3>
              <div className="space-y-3">
                {auditResults.recommendations.map((rec: any, idx: number) => (
                  <div key={idx} className={`flex items-start gap-3 rounded-lg p-3 ${
                    rec.type === 'critical' ? 'bg-destructive/10 border border-destructive/20' :
                    rec.type === 'warning' ? 'bg-warning/10 border border-warning/20' :
                    rec.type === 'success' ? 'bg-success/10 border border-success/20' :
                    'bg-secondary/50'
                  }`}>
                    <div className={`mt-0.5 h-2 w-2 rounded-full ${
                      rec.type === 'critical' ? 'bg-destructive' :
                      rec.type === 'warning' ? 'bg-warning' :
                      rec.type === 'success' ? 'bg-success' :
                      'bg-primary'
                    }`} />
                    <div>
                      <p className="text-sm font-medium text-foreground">{rec.title}</p>
                      <p className="text-xs text-muted-foreground mt-1">{rec.description}</p>
                      <p className="text-xs text-primary mt-1 font-medium">{rec.action}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
      </>
      )}
    </main>
  )
}
