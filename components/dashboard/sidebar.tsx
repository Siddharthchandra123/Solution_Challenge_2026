"use client"

import { 
  BarChart3, 
  GitBranch, 
  Wrench, 
  BrainCircuit, 
  Activity,
  Sparkles
} from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

interface NavItem {
  icon: React.ElementType
  label: string
  href: string
}

const navItems: NavItem[] = [
  { icon: BarChart3, label: "Data Diagnostics", href: "/diagnostics" },
  { icon: GitBranch, label: "Bivariate Explorer", href: "/explorer" },
  { icon: Wrench, label: "Bias Mitigation (The Fixer)", href: "/" },
  { icon: BrainCircuit, label: "SHAP Explainability", href: "/shap" },
  { icon: Activity, label: "Live Production Monitor", href: "/monitor" },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 glass border-r border-border">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-6 border-b border-border">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/20 glow-cyan">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-foreground">Truth & Fairness</h1>
            <p className="text-xs text-muted-foreground">AI Engine</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.label}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-primary/15 text-primary glow-cyan border border-primary/30"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                )}
              >
                <item.icon className={cn(
                  "h-5 w-5",
                  isActive ? "text-primary" : "text-muted-foreground"
                )} />
                <span className="truncate">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-border p-4">
          <div className="glass rounded-lg p-3">
            <p className="text-xs text-muted-foreground">Engine Version</p>
            <p className="text-sm font-semibold text-foreground">v2.4.1</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
