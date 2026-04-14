"use client"

import { Sidebar } from "./sidebar"
import { TopNavbar } from "./top-navbar"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div className="ml-64 flex min-h-screen flex-col">
        <TopNavbar />
        {children}
      </div>
    </div>
  )
}
