"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Check, Download, FileText, X } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { toast } from "@/components/ui/use-toast"

// Mock data
const mockReports = {
  job1: {
    clients: [
      { id: 1, name: "Acme Corporation" },
      { id: 2, name: "Globex Industries" },
      { id: 3, name: "Stark Enterprises" },
      { id: 4, name: "Wayne Foundations" },
      { id: 5, name: "Umbrella Corp" },
      { id: 6, name: "Oscorp Industries" },
    ],
    criteria: [
      { id: 1, name: "Minimum 5 years experience", matched: true },
      { id: 2, name: "ISO 9001 Certification", matched: true },
      { id: 3, name: "Local business presence", matched: true },
      { id: 4, name: "Previous government contracts", matched: false },
      { id: 5, name: "Sustainability commitment", matched: true },
      { id: 6, name: "Liability insurance ($2M+)", matched: true },
      { id: 7, name: "Workforce diversity program", matched: true },
      { id: 8, name: "24/7 Support capability", matched: true },
      { id: 9, name: "Disaster recovery plan", matched: false },
      { id: 10, name: "Financial stability (5yr+)", matched: true },
    ],
  },
  job2: {
    clients: [
      { id: 7, name: "Cyberdyne Systems" },
      { id: 8, name: "Massive Dynamic" },
      { id: 9, name: "Soylent Corp" },
    ],
    criteria: [
      { id: 11, name: "Healthcare industry experience", matched: true },
      { id: 12, name: "HIPAA compliance", matched: true },
      { id: 13, name: "Electronic health record integration", matched: false },
      { id: 14, name: "24/7 technical support", matched: true },
      { id: 15, name: "Cloud-based solution", matched: true },
    ],
  },
  job3: {
    clients: [
      { id: 10, name: "Initech" },
      { id: 11, name: "Rekall" },
    ],
    criteria: [
      { id: 16, name: "Educational content development", matched: true },
      { id: 17, name: "Learning management system", matched: true },
      { id: 18, name: "Mobile compatibility", matched: true },
      { id: 19, name: "Accessibility compliance", matched: false },
      { id: 20, name: "Student data privacy", matched: true },
    ],
  },
}

export default function ReportView({ jobId }) {
  const [selectedClientId, setSelectedClientId] = useState("")
  const [report, setReport] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate loading data
    setIsLoading(true)
    setTimeout(() => {
      const jobReport = mockReports[jobId]
      setReport(jobReport)
      if (jobReport && jobReport.clients.length > 0) {
        setSelectedClientId(jobReport.clients[0].id.toString())
      } else {
        setSelectedClientId("")
      }
      setIsLoading(false)
    }, 800)
  }, [jobId])

  const handleDownload = () => {
    toast({
      title: "Report Downloaded",
      description: "The report has been downloaded successfully.",
      duration: 3000,
    })
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 border-4 border-cyan-500/30 rounded-full animate-ping"></div>
          <div className="absolute inset-2 border-4 border-t-cyan-500 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    )
  }

  if (!report || report.clients.length === 0) {
    return <div className="text-center py-12 text-slate-400">No reports available for this job.</div>
  }

  const matchedCount = report.criteria.filter((c) => c.matched).length
  const totalCount = report.criteria.length
  const matchPercentage = Math.round((matchedCount / totalCount) * 100)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <Select value={selectedClientId} onValueChange={setSelectedClientId}>
          <SelectTrigger className="w-[280px] bg-slate-800/50 border-slate-700 text-slate-200">
            <SelectValue placeholder="Select client" />
          </SelectTrigger>
          <SelectContent className="bg-slate-800 border-slate-700 text-slate-200">
            {report.clients.map((client) => (
              <SelectItem
                key={client.id}
                value={client.id.toString()}
                className="text-slate-200 focus:bg-slate-700 focus:text-slate-200"
              >
                {client.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Button variant="outline" className="border-cyan-500/30 text-cyan-400" onClick={handleDownload}>
          <Download className="mr-2 h-4 w-4" />
          Download Report
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Card className="bg-slate-800/50 border-slate-700/50 col-span-2">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="h-16 w-16 rounded-full bg-cyan-500/20 flex items-center justify-center">
                <FileText className="h-8 w-8 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-slate-200">Match Summary</h3>
                <p className="text-sm text-slate-400">
                  {matchedCount} of {totalCount} criteria matched ({matchPercentage}%)
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700/50">
          <CardContent className="p-6 flex flex-col items-center justify-center">
            <div className="text-3xl font-bold text-cyan-400">{matchPercentage}%</div>
            <div className="text-sm text-slate-400 mt-2">Match Rate</div>
            <Badge
              className={
                matchPercentage >= 80
                  ? "bg-green-500/20 text-green-400 border-green-500/50 mt-4"
                  : matchPercentage >= 60
                    ? "bg-amber-500/20 text-amber-400 border-amber-500/50 mt-4"
                    : "bg-red-500/20 text-red-400 border-red-500/50 mt-4"
              }
            >
              {matchPercentage >= 80 ? "Approved" : matchPercentage >= 60 ? "Partially Approved" : "Rejected"}
            </Badge>
          </CardContent>
        </Card>
      </div>

      <div className="bg-slate-800/30 rounded-lg border border-slate-700/50 overflow-hidden">
        <div className="p-4 border-b border-slate-700/50 bg-slate-800/50">
          <h3 className="text-sm font-medium text-slate-200">Criteria Checklist</h3>
        </div>

        <div className="divide-y divide-slate-700/30">
          {report.criteria.map((criterion, index) => (
            <motion.div
              key={criterion.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className="flex items-center justify-between p-4 hover:bg-slate-800/50"
            >
              <div className="flex items-center">
                <div
                  className={`h-6 w-6 rounded-full flex items-center justify-center mr-3 ${
                    criterion.matched ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"
                  }`}
                >
                  {criterion.matched ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
                </div>
                <span className="text-slate-300">{criterion.name}</span>
              </div>
              <Badge
                variant="outline"
                className={
                  criterion.matched
                    ? "bg-green-500/10 text-green-400 border-green-500/30"
                    : "bg-red-500/10 text-red-400 border-red-500/30"
                }
              >
                {criterion.matched ? "Matched" : "Unmatched"}
              </Badge>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

