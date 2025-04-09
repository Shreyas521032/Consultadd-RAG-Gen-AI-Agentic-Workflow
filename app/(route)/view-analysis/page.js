"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { BarChart3, Check, Download, Filter, Search, SlidersHorizontal, X } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import JobSelector from "@/components/job-selector"
import { toast } from "@/components/ui/use-toast"

// Mock data
const jobs = [
  { id: "job1", title: "City Infrastructure Project RFP" },
  { id: "job2", title: "Healthcare System Modernization" },
  { id: "job3", title: "Educational Technology Initiative" },
]

const mockClients = {
  job1: [
    {
      id: 1,
      name: "Acme Corporation",
      status: "Approved",
      matchCount: "12/13",
      progress: 92,
      timestamp: "2023-04-05T14:32:12",
      criteria: [
        { id: 1, name: "Minimum 5 years experience", matched: true },
        { id: 2, name: "ISO 9001 Certification", matched: true },
        { id: 3, name: "Local business presence", matched: true },
        { id: 4, name: "Previous government contracts", matched: false },
        { id: 5, name: "Sustainability commitment", matched: true },
      ],
    },
    {
      id: 2,
      name: "Globex Industries",
      status: "Approved",
      matchCount: "17/20",
      progress: 85,
      timestamp: "2023-04-04T10:15:45",
      criteria: [
        { id: 1, name: "Minimum 5 years experience", matched: true },
        { id: 2, name: "ISO 9001 Certification", matched: true },
        { id: 3, name: "Local business presence", matched: false },
        { id: 4, name: "Previous government contracts", matched: true },
        { id: 5, name: "Sustainability commitment", matched: true },
      ],
    },
    {
      id: 3,
      name: "Stark Enterprises",
      status: "Partially Approved",
      matchCount: "7/9",
      progress: 78,
      timestamp: "2023-04-03T16:48:22",
      criteria: [
        { id: 1, name: "Minimum 5 years experience", matched: true },
        { id: 2, name: "ISO 9001 Certification", matched: true },
        { id: 3, name: "Local business presence", matched: false },
        { id: 4, name: "Previous government contracts", matched: true },
        { id: 5, name: "Sustainability commitment", matched: false },
      ],
    },
    {
      id: 4,
      name: "Wayne Foundations",
      status: "Partially Approved",
      matchCount: "8/12",
      progress: 67,
      timestamp: "2023-04-02T09:30:18",
      criteria: [
        { id: 1, name: "Minimum 5 years experience", matched: true },
        { id: 2, name: "ISO 9001 Certification", matched: false },
        { id: 3, name: "Local business presence", matched: true },
        { id: 4, name: "Previous government contracts", matched: false },
        { id: 5, name: "Sustainability commitment", matched: true },
      ],
    },
    {
      id: 5,
      name: "Umbrella Corp",
      status: "In Progress",
      matchCount: "7/12",
      progress: 58,
      timestamp: "2023-04-01T11:22:36",
      criteria: [
        { id: 1, name: "Minimum 5 years experience", matched: true },
        { id: 2, name: "ISO 9001 Certification", matched: false },
        { id: 3, name: "Local business presence", matched: true },
        { id: 4, name: "Previous government contracts", matched: false },
        { id: 5, name: "Sustainability commitment", matched: false },
      ],
    },
    {
      id: 6,
      name: "Oscorp Industries",
      status: "Rejected",
      matchCount: "3/10",
      progress: 30,
      timestamp: "2023-03-31T15:10:05",
      criteria: [
        { id: 1, name: "Minimum 5 years experience", matched: false },
        { id: 2, name: "ISO 9001 Certification", matched: false },
        { id: 3, name: "Local business presence", matched: true },
        { id: 4, name: "Previous government contracts", matched: false },
        { id: 5, name: "Sustainability commitment", matched: false },
      ],
    },
  ],
  job2: [
    {
      id: 7,
      name: "Cyberdyne Systems",
      status: "Approved",
      matchCount: "15/15",
      progress: 100,
      timestamp: "2023-04-05T08:45:30",
      criteria: [
        { id: 11, name: "Healthcare industry experience", matched: true },
        { id: 12, name: "HIPAA compliance", matched: true },
        { id: 13, name: "Electronic health record integration", matched: true },
        { id: 14, name: "24/7 technical support", matched: true },
        { id: 15, name: "Cloud-based solution", matched: true },
      ],
    },
    {
      id: 8,
      name: "Massive Dynamic",
      status: "Partially Approved",
      matchCount: "12/15",
      progress: 80,
      timestamp: "2023-04-04T13:20:15",
      criteria: [
        { id: 11, name: "Healthcare industry experience", matched: true },
        { id: 12, name: "HIPAA compliance", matched: true },
        { id: 13, name: "Electronic health record integration", matched: false },
        { id: 14, name: "24/7 technical support", matched: true },
        { id: 15, name: "Cloud-based solution", matched: true },
      ],
    },
    {
      id: 9,
      name: "Soylent Corp",
      status: "In Progress",
      matchCount: "6/15",
      progress: 40,
      timestamp: "2023-04-03T09:15:45",
      criteria: [
        { id: 11, name: "Healthcare industry experience", matched: false },
        { id: 12, name: "HIPAA compliance", matched: true },
        { id: 13, name: "Electronic health record integration", matched: false },
        { id: 14, name: "24/7 technical support", matched: false },
        { id: 15, name: "Cloud-based solution", matched: true },
      ],
    },
  ],
  job3: [
    {
      id: 10,
      name: "Initech",
      status: "Approved",
      matchCount: "10/10",
      progress: 100,
      timestamp: "2023-04-05T16:30:00",
      criteria: [
        { id: 16, name: "Educational content development", matched: true },
        { id: 17, name: "Learning management system", matched: true },
        { id: 18, name: "Mobile compatibility", matched: true },
        { id: 19, name: "Accessibility compliance", matched: true },
        { id: 20, name: "Student data privacy", matched: true },
      ],
    },
    {
      id: 11,
      name: "Rekall",
      status: "Rejected",
      matchCount: "2/10",
      progress: 20,
      timestamp: "2023-04-04T11:45:22",
      criteria: [
        { id: 16, name: "Educational content development", matched: false },
        { id: 17, name: "Learning management system", matched: false },
        { id: 18, name: "Mobile compatibility", matched: true },
        { id: 19, name: "Accessibility compliance", matched: false },
        { id: 20, name: "Student data privacy", matched: true },
      ],
    },
  ],
}

export default function ViewAnalysis() {
  const [selectedJob, setSelectedJob] = useState(jobs[0])
  const [clients, setClients] = useState([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [sortBy, setSortBy] = useState("match")
  const [isLoading, setIsLoading] = useState(true)
  const [selectedClient, setSelectedClient] = useState(null)
  const [viewMode, setViewMode] = useState("list")

  useEffect(() => {
    // Simulate loading data
    setIsLoading(true)
    setTimeout(() => {
      setClients(mockClients[selectedJob.id] || [])
      setSelectedClient(null)
      setIsLoading(false)
    }, 800)
  }, [selectedJob])

  const filteredClients = clients
    .filter(
      (client) =>
        client.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        (statusFilter === "all" || client.status === statusFilter),
    )
    .sort((a, b) => {
      if (sortBy === "match") {
        return b.progress - a.progress
      } else if (sortBy === "name") {
        return a.name.localeCompare(b.name)
      } else if (sortBy === "date") {
        return new Date(b.timestamp) - new Date(a.timestamp)
      }
      return 0
    })

  const getStatusColor = (status) => {
    switch (status) {
      case "Approved":
        return "bg-green-500/20 text-green-400 border-green-500/50"
      case "Partially Approved":
        return "bg-amber-500/20 text-amber-400 border-amber-500/50"
      case "In Progress":
        return "bg-blue-500/20 text-blue-400 border-blue-500/50"
      case "Rejected":
        return "bg-red-500/20 text-red-400 border-red-500/50"
      default:
        return "bg-slate-500/20 text-slate-400 border-slate-500/50"
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    })
  }

  const handleDownloadReport = (clientId) => {
    toast({
      title: "Report Downloaded",
      description: "The client report has been downloaded successfully.",
      duration: 3000,
    })
  }

  const handleViewClient = (client) => {
    setSelectedClient(client)
    setViewMode("detail")
  }

  const handleBackToList = () => {
    setSelectedClient(null)
    setViewMode("list")
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">View Analysis</h1>
          <p className="text-slate-400">Review and analyze client document matches</p>
        </div>
        <JobSelector jobs={jobs} selectedJob={selectedJob} onSelectJob={setSelectedJob} />
      </div>

      <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
        <CardHeader className="border-b border-slate-700/50 pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-slate-100 flex items-center">
              <BarChart3 className="mr-2 h-5 w-5 text-cyan-500" />
              Analysis Results
            </CardTitle>
            <Tabs value={viewMode} onValueChange={setViewMode} className="w-[200px]">
              <TabsList className="bg-slate-800/50 p-1">
                <TabsTrigger
                  value="list"
                  className="data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-400"
                  disabled={isLoading}
                >
                  List View
                </TabsTrigger>
                <TabsTrigger
                  value="detail"
                  className="data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-400"
                  disabled={isLoading || !selectedClient}
                >
                  Detail View
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          {viewMode === "list" ? (
            <>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                  <Input
                    placeholder="Search clients..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-slate-800/50 border-slate-700 text-slate-200 placeholder:text-slate-500"
                  />
                </div>
                <div className="flex flex-col md:flex-row gap-3">
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-[180px] bg-slate-800/50 border-slate-700 text-slate-200">
                      <Filter className="h-4 w-4 mr-2 text-slate-400" />
                      <SelectValue placeholder="Filter by status" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700 text-slate-200">
                      <SelectItem value="all" className="text-slate-200 focus:bg-slate-700 focus:text-slate-200">
                        All Statuses
                      </SelectItem>
                      <SelectItem value="Approved" className="text-slate-200 focus:bg-slate-700 focus:text-slate-200">
                        Approved
                      </SelectItem>
                      <SelectItem
                        value="Partially Approved"
                        className="text-slate-200 focus:bg-slate-700 focus:text-slate-200"
                      >
                        Partially Approved
                      </SelectItem>
                      <SelectItem
                        value="In Progress"
                        className="text-slate-200 focus:bg-slate-700 focus:text-slate-200"
                      >
                        In Progress
                      </SelectItem>
                      <SelectItem value="Rejected" className="text-slate-200 focus:bg-slate-700 focus:text-slate-200">
                        Rejected
                      </SelectItem>
                    </SelectContent>
                  </Select>

                  <Select value={sortBy} onValueChange={setSortBy}>
                    <SelectTrigger className="w-[180px] bg-slate-800/50 border-slate-700 text-slate-200">
                      <SlidersHorizontal className="h-4 w-4 mr-2 text-slate-400" />
                      <SelectValue placeholder="Sort by" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700 text-slate-200">
                      <SelectItem value="match" className="text-slate-200 focus:bg-slate-700 focus:text-slate-200">
                        Match Percentage
                      </SelectItem>
                      <SelectItem value="name" className="text-slate-200 focus:bg-slate-700 focus:text-slate-200">
                        Client Name
                      </SelectItem>
                      <SelectItem value="date" className="text-slate-200 focus:bg-slate-700 focus:text-slate-200">
                        Upload Date
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {isLoading ? (
                <div className="flex justify-center items-center h-64">
                  <div className="relative w-16 h-16">
                    <div className="absolute inset-0 border-4 border-cyan-500/30 rounded-full animate-ping"></div>
                    <div className="absolute inset-2 border-4 border-t-cyan-500 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
                  </div>
                </div>
              ) : filteredClients.length === 0 ? (
                <div className="text-center py-12 text-slate-400">No clients found matching your criteria.</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredClients.map((client, index) => (
                    <motion.div
                      key={client.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.05 }}
                    >
                      <Card
                        className="bg-slate-800/50 border-slate-700/50 hover:border-cyan-500/30 transition-colors cursor-pointer"
                        onClick={() => handleViewClient(client)}
                      >
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start mb-3">
                            <h3 className="font-medium text-slate-200">{client.name}</h3>
                            <Badge variant="outline" className={getStatusColor(client.status)}>
                              {client.status}
                            </Badge>
                          </div>

                          <div className="space-y-3">
                            <div>
                              <div className="flex items-center justify-between mb-1">
                                <div className="text-xs text-slate-400">Match Rate</div>
                                <div className="text-xs text-cyan-400 font-mono">{client.matchCount}</div>
                              </div>
                              <Progress value={client.progress} className="h-1.5 bg-slate-700">
                                <div
                                  className={`h-full rounded-full ${
                                    client.progress > 80
                                      ? "bg-green-500"
                                      : client.progress > 60
                                        ? "bg-cyan-500"
                                        : client.progress > 40
                                          ? "bg-amber-500"
                                          : "bg-red-500"
                                  }`}
                                  style={{ width: `${client.progress}%` }}
                                />
                              </Progress>
                            </div>

                            <div className="flex items-center justify-between text-xs">
                              <span className="text-slate-400">Uploaded: {formatDate(client.timestamp)}</span>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-7 px-2 text-cyan-400 hover:text-cyan-300 hover:bg-slate-700/50"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleDownloadReport(client.id)
                                }}
                              >
                                <Download className="h-3.5 w-3.5 mr-1" />
                                Report
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              )}
            </>
          ) : (
            selectedClient && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <Button
                      variant="outline"
                      size="sm"
                      className="border-slate-700 text-slate-400"
                      onClick={handleBackToList}
                    >
                      <X className="h-4 w-4 mr-2" />
                      Back to List
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="border-cyan-500/30 text-cyan-400"
                      onClick={() => handleDownloadReport(selectedClient.id)}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download Report
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card className="bg-slate-800/50 border-slate-700/50 col-span-2">
                      <CardContent className="p-6">
                        <div className="flex items-center space-x-4">
                          <div className="h-16 w-16 rounded-full bg-cyan-500/20 flex items-center justify-center">
                            <BarChart3 className="h-8 w-8 text-cyan-400" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-slate-200">{selectedClient.name}</h3>
                            <p className="text-sm text-slate-400">
                              {selectedClient.matchCount} criteria matched ({selectedClient.progress}%)
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="bg-slate-800/50 border-slate-700/50">
                      <CardContent className="p-6 flex flex-col items-center justify-center">
                        <div className="text-3xl font-bold text-cyan-400">{selectedClient.progress}%</div>
                        <div className="text-sm text-slate-400 mt-2">Match Rate</div>
                        <Badge className={getStatusColor(selectedClient.status)} variant="outline">
                          {selectedClient.status}
                        </Badge>
                      </CardContent>
                    </Card>
                  </div>

                  <div className="bg-slate-800/30 rounded-lg border border-slate-700/50 overflow-hidden">
                    <div className="p-4 border-b border-slate-700/50 bg-slate-800/50">
                      <h3 className="text-sm font-medium text-slate-200">Criteria Checklist</h3>
                    </div>

                    <div className="divide-y divide-slate-700/30">
                      {selectedClient.criteria.map((criterion, index) => (
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
              </motion.div>
            )
          )}
        </CardContent>
      </Card>
    </div>
  )
}

