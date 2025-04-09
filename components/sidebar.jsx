"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion } from "framer-motion"
import { BarChart3, FolderUp, Hexagon, LayoutDashboard, ListChecks, Settings, Upload } from "lucide-react"

export default function Sidebar() {
  const pathname = usePathname()
  const [isCollapsed, setIsCollapsed] = useState(false)

  const navItems = [
    {
      title: "Dashboard",
      icon: LayoutDashboard,
      href: "/",
    },
    {
      title: "Generate Criteria",
      icon: ListChecks,
      href: "/generate-criteria",
    },
    {
      title: "Upload Document",
      icon: Upload,
      href: "/upload-document",
    },
    {
      title: "Bulk Upload",
      icon: FolderUp,
      href: "/bulk-upload",
    },
    {
      title: "View Analysis",
      icon: BarChart3,
      href: "/view-analysis",
    },
    {
      title: "Settings",
      icon: Settings,
      href: "/settings",
    },
  ]

  return (
    <div
      className={`${
        isCollapsed ? "w-20" : "w-64"
      } h-screen bg-slate-900 border-r border-slate-700/50 transition-all duration-300 ease-in-out flex flex-col`}
    >
      {/* Logo */}
      <div className="p-4 border-b border-slate-700/50 flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Hexagon className="h-8 w-8 text-cyan-500" />
          {!isCollapsed && (
            <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Consultadd
            </span>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 pt-4 px-2">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <li key={item.href}>
                <Link href={item.href}>
                  <div
                    className={`flex items-center p-3 rounded-lg transition-colors relative ${
                      isActive
                        ? "bg-slate-800/70 text-cyan-400"
                        : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/50"
                    }`}
                  >
                    {isActive && (
                      <motion.div
                        layoutId="activeNav"
                        className="absolute left-0 top-0 bottom-0 w-1 bg-cyan-500 rounded-full"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.2 }}
                      />
                    )}
                    <item.icon className={`h-5 w-5 ${isActive ? "text-cyan-400" : ""}`} />
                    {!isCollapsed && <span className="ml-3">{item.title}</span>}
                  </div>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Collapse button */}
      <div className="p-4 border-t border-slate-700/50 flex justify-center">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800/50"
        >
          {isCollapsed ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
          )}
        </button>
      </div>
    </div>
  )
}

