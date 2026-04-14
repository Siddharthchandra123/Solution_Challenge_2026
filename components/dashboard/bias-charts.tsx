"use client"

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"

interface ChartCardProps {
  title: string
  subtitle: string
  data: any[]
  showDisparity?: boolean
}

function ChartCard({ title, subtitle, data, showDisparity }: ChartCardProps) {
  return (
    <div className="glass rounded-xl p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-foreground">{title}</h3>
        <p className="text-sm text-muted-foreground">{subtitle}</p>
      </div>
      <div className="h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barGap={4} barCategoryGap="20%">
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="oklch(0.30 0.03 260)" 
              vertical={false}
            />
            <XAxis 
              dataKey="category" 
              tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 12 }}
              axisLine={{ stroke: "oklch(0.30 0.03 260)" }}
              tickLine={false}
            />
            <YAxis 
              domain={[0, 1]}
              tick={{ fill: "oklch(0.65 0.02 260)", fontSize: 12 }}
              axisLine={{ stroke: "oklch(0.30 0.03 260)" }}
              tickLine={false}
              tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "oklch(0.18 0.02 260)",
                border: "1px solid oklch(0.30 0.03 260)",
                borderRadius: "8px",
                color: "oklch(0.95 0.01 260)",
              }}
              labelStyle={{ color: "oklch(0.95 0.01 260)" }}
              formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, ""]}
            />
            <Legend 
              wrapperStyle={{ paddingTop: "16px" }}
              formatter={(value) => (
                <span style={{ color: "oklch(0.65 0.02 260)" }}>{value}</span>
              )}
            />
            <Bar 
              dataKey="privileged" 
              name="Male (Privileged)"
              fill="oklch(0.75 0.15 195)"
              radius={[4, 4, 0, 0]}
            />
            <Bar 
              dataKey="unprivileged" 
              name="Female (Unprivileged)"
              fill={showDisparity ? "oklch(0.65 0.22 30)" : "oklch(0.70 0.14 185)"}
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

interface BiasChartsProps {
  chartsBefore: any[]
  chartsAfter: any[]
}

export function BiasCharts({ chartsBefore, chartsAfter }: BiasChartsProps) {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <ChartCard
        title="Before Mitigation"
        subtitle="Unmitigated positive prediction rates by sex"
        data={chartsBefore}
        showDisparity={true}
      />
      <ChartCard
        title="After Threshold Optimizer"
        subtitle="Achieving mathematical equality enforcing Demographic Parity"
        data={chartsAfter}
        showDisparity={false}
      />
    </div>
  )
}
