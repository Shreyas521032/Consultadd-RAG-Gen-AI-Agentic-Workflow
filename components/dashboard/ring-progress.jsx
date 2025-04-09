"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"

export default function RingProgress({ value, size = 120, strokeWidth = 10 }) {
  const [progress, setProgress] = useState(0)

  // Animation effect
  useEffect(() => {
    const timer = setTimeout(() => {
      setProgress(value)
    }, 500)
    return () => clearTimeout(timer)
  }, [value])

  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const strokeDashoffset = circumference - (progress / 100) * circumference

  return (
    <div className="relative" style={{ width: size, height: size }}>
      {/* Background circle */}
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="rgba(100, 116, 139, 0.2)"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="url(#gradient)"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: "easeInOut" }}
          strokeLinecap="round"
        />
        {/* Gradient definition */}
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#06b6d4" /> {/* cyan-500 */}
            <stop offset="100%" stopColor="#3b82f6" /> {/* blue-500 */}
          </linearGradient>
        </defs>
      </svg>

      {/* Percentage text in the middle */}
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="text-3xl font-bold text-cyan-400"
        >
          {progress}%
        </motion.div>
      </div>
    </div>
  )
}

