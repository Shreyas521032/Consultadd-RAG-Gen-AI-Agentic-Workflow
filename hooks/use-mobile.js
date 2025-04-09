"use client"

import * as React from "react"

const MOBILE_BREAKPOINT = 768

export function useIsMobile() {
  const [isMobile, setIsMobile] = React.useState(undefined)

  React.useEffect(() => {
    const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`)
    const onChange = () => {
      setIsMobile(window.innerWidth < MOBILE_BREAKPOINT)
    }
    mql.addEventListener("change", onChange)
    setIsMobile(window.innerWidth < MOBILE_BREAKPOINT)
    return () => mql.removeEventListener("change", onChange);
  }, [])

  return !!isMobile
}










// generate fro v0 for kanban -- if above not works then use below one

// "use client"

// import { useState, useEffect } from "react"

// export function useIsMobile() {
//   const [isMobile, setIsMobile] = useState(false)

//   useEffect(() => {
//     // Check if window is defined (browser environment)
//     if (typeof window !== "undefined") {
//       const checkIsMobile = () => {
//         setIsMobile(window.innerWidth < 768)
//       }

//       // Initial check
//       checkIsMobile()

//       // Add event listener for window resize
//       window.addEventListener("resize", checkIsMobile)

//       // Clean up event listener
//       return () => {
//         window.removeEventListener("resize", checkIsMobile)
//       }
//     }
//   }, [])

//   return isMobile
// }

