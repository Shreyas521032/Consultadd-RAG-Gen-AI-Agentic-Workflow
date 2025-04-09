"use client"

import { useState } from "react"
import { CheckCircle, Clock, Download, FileText, RefreshCw, Users, XCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import JobSelector from "@/components/job-selector"
import ClientOverview from "@/components/dashboard/client-overview"
import ReportView from "@/components/dashboard/report-view"
import StatusCard from "@/components/dashboard/status-card"
import RingProgress from "@/components/dashboard/ring-progress"

// Mock data
const jobs = [
  { id: "job1", title: "City Infrastructure Project RFP" },
  { id: "job2", title: "Healthcare System Modernization" },
  { id: "job3", title: "Educational Technology Initiative" },
]

export default function Dashboard() {
  const [selectedJob, setSelectedJob] = useState(jobs[0])
  const [isLoading, setIsLoading] = useState(false)

  const refreshData = () => {
    setIsLoading(true)
    setTimeout(() => {
      setIsLoading(false)
    }, 1500)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Dashboard</h1>
          <p className="text-slate-400">Monitor and analyze RFP document processing</p>
        </div>
        <JobSelector jobs={jobs} selectedJob={selectedJob} onSelectJob={setSelectedJob} />
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatusCard
          title="Total Documents"
          value="42"
          icon={FileText}
          color="blue"
          trend={{ value: "+12%", direction: "up" }}
        />
        <StatusCard
          title="Approved"
          value="28"
          icon={CheckCircle}
          color="green"
          trend={{ value: "+8%", direction: "up" }}
        />
        <StatusCard title="Pending" value="10" icon={Clock} color="amber" trend={{ value: "-5%", direction: "down" }} />
        <StatusCard title="Rejected" value="4" icon={XCircle} color="red" trend={{ value: "+2%", direction: "up" }} />
      </div>

      {/* Main Content */}
      <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm overflow-hidden">
        <CardHeader className="border-b border-slate-700/50 pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-slate-100 flex items-center">
              <Users className="mr-2 h-5 w-5 text-cyan-500" />
              {selectedJob.title}
            </CardTitle>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="bg-slate-800/50 text-cyan-400 border-cyan-500/50 text-xs">
                <div className="h-1.5 w-1.5 rounded-full bg-cyan-500 mr-1 animate-pulse"></div>
                LIVE
              </Badge>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-slate-400"
                onClick={refreshData}
                disabled={isLoading}
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="bg-slate-800/50 p-1 mb-6">
              <TabsTrigger
                value="overview"
                className="data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-400"
              >
                Client Overview
              </TabsTrigger>
              <TabsTrigger
                value="report"
                className="data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-400"
              >
                View / Download Report
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-0">
              <ClientOverview jobId={selectedJob.id} />
            </TabsContent>

            <TabsContent value="report" className="mt-0">
              <ReportView jobId={selectedJob.id} />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Performance Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-slate-100 text-base">Top Performing Clients</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: "Acme Corporation", progress: 92, criteria: "12/13" },
                { name: "Globex Industries", progress: 85, criteria: "17/20" },
                { name: "Stark Enterprises", progress: 78, criteria: "7/9" },
                { name: "Wayne Foundations", progress: 67, criteria: "8/12" },
                { name: "Umbrella Corp", progress: 58, criteria: "7/12" },
              ].map((client, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="text-slate-300">{index + 1}.</div>
                    <div>
                      <div className="text-sm font-medium text-slate-200">{client.name}</div>
                      <div className="text-xs text-slate-400">Criteria Met: {client.criteria}</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-24">
                      <Progress value={client.progress} className="h-2 bg-slate-700">
                        <div
                          className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
                          style={{ width: `${client.progress}%` }}
                        />
                      </Progress>
                    </div>
                    <div className="text-sm font-mono text-cyan-400">{client.progress}%</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-slate-100 text-base">Overall Match Rate</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center p-6">
            <RingProgress value={76} size={180} strokeWidth={12} />
            <div className="mt-4 text-center">
              <div className="text-sm text-slate-400">Total Criteria Matched</div>
              <div className="text-2xl font-bold text-slate-100 mt-1">152 / 200</div>
              <Button variant="outline" size="sm" className="mt-4 border-cyan-500/30 text-cyan-400">
                <Download className="mr-2 h-4 w-4" />
                Export Report
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

