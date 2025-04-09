"use client"

import { useEffect, useState } from "react"
import { X } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

let toastCount = 0

function Toast({ toast, onDismiss }) {
  const { id, title, description, variant = "default", duration = 5000 } = toast

  useEffect(() => {
    if (duration) {
      const timer = setTimeout(() => {
        onDismiss(id)
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [id, duration, onDismiss])

  const variantStyles = {
    default: "bg-slate-800 border-slate-700",
    destructive: "bg-red-900/90 border-red-800",
    success: "bg-green-900/90 border-green-800",
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={`rounded-lg border ${variantStyles[variant]} p-4 shadow-lg pointer-events-auto flex items-start w-full max-w-md`}
    >
      <div className="flex-1">
        {title && <div className="text-sm font-medium text-slate-100">{title}</div>}
        {description && <div className="mt-1 text-xs text-slate-400">{description}</div>}
      </div>
      <button
        onClick={() => onDismiss(id)}
        className="ml-4 inline-flex h-6 w-6 items-center justify-center rounded-md text-slate-400 hover:text-slate-100"
      >
        <X className="h-4 w-4" />
      </button>
    </motion.div>
  )
}

export function Toaster() {
  const [toasts, setToasts] = useState([])

  useEffect(() => {
    const handleToast = (event) => {
      const { toast } = event.detail
      setToasts((toasts) => [...toasts, { id: ++toastCount, ...toast }])
    }

    window.addEventListener("toast", handleToast)
    return () => window.removeEventListener("toast", handleToast)
  }, [])

  const dismissToast = (id) => {
    setToasts((toasts) => toasts.filter((toast) => toast.id !== id))
  }

  return (
    <div className="fixed bottom-0 right-0 z-50 flex flex-col p-4 gap-2 max-h-screen w-full sm:max-w-md overflow-hidden pointer-events-none">
      <AnimatePresence>
        {toasts.map((toast) => (
          <Toast key={toast.id} toast={toast} onDismiss={dismissToast} />
        ))}
      </AnimatePresence>
    </div>
  )
}

export function toast(props) {
  const event = new CustomEvent("toast", { detail: { toast: props } })
  window.dispatchEvent(event)
}

