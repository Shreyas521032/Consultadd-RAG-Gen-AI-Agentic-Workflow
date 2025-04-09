"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Search } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Input } from "@/components/ui/input"

// Mock data
const mockClients = {
  job1: [
    {
      id: 1,
      name: "Acme Corporation",
      status: "Approved",
      matchCount: "12/13",
      progress: 92,
      timestamp: "2023-04-05T14:32:12",
    },
    {
      id: 2,
      name: "Globex Industries",
      status: "Approved",
      matchCount: "17/20",
      progress: 85,
      timestamp: "2023-04-04T10:15:45",
    },
    {
      id: 3,
      name: "Stark Enterprises",
      status: "Partially Approved",
      matchCount: "7/9",
      progress: 78,
      timestamp: "2023-04-03T16:48:22",
    },
    {
      id: 4,
      name: "Wayne Foundations",
      status: "Partially Approved",
      matchCount: "8/12",
      progress: 67,
      timestamp: "2023-04-02T09:30:18",
    },
    {
      id: 5,
      name: "Umbrella Corp",
      status: "In Progress",
      matchCount: "7/12",
      progress: 58,
      timestamp: "2023-04-01T11:22:36",
    },
    {
      id: 6,
      name: "Oscorp Industries",
      status: "Rejected",
      matchCount: "3/10",
      progress: 30,
      timestamp: "2023-03-31T15:10:05",
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
    },
    {
      id: 8,
      name: "Massive Dynamic",
      status: "Partially Approved",
      matchCount: "12/15",
      progress: 80,
      timestamp: "2023-04-04T13:20:15",
    },
    {
      id: 9,
      name: "Soylent Corp",
      status: "In Progress",
      matchCount: "6/15",
      progress: 40,
      timestamp: "2023-04-03T09:15:45",
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
    },
    {
      id: 11,
      name: "Rekall",
      status: "Rejected",
      matchCount: "2/10",
      progress: 20,
      timestamp: "2023-04-04T11:45:22",
    },
  ],
}

export default function ClientOverview({ jobId }) {
  const [clients, setClients] = useState([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate loading data
    setIsLoading(true)
    setTimeout(() => {
      setClients(mockClients[jobId] || [])
      setIsLoading(false)
    }, 800)
  }, [jobId])

  const filteredClients = clients.filter((client) => client.name.toLowerCase().includes(searchTerm.toLowerCase()))

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

  const formatTime = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <div>
      <div className="flex items-center mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search clients..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-slate-800/50 border-slate-700 text-slate-200 placeholder:text-slate-500"
          />
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
        <div className="text-center py-12 text-slate-400">No clients found for this job.</div>
      ) : (
        <div className="bg-slate-800/30 rounded-lg border border-slate-700/50 overflow-hidden">
          <div className="grid grid-cols-12 text-xs text-slate-400 p-3 border-b border-slate-700/50 bg-slate-800/50">
            <div className="col-span-4">Client Name</div>
            <div className="col-span-2">Status</div>
            <div className="col-span-2">Match Count</div>
            <div className="col-span-2">Progress</div>
            <div className="col-span-2">Upload Date</div>
          </div>

          <div className="divide-y divide-slate-700/30">
            {filteredClients.map((client, index) => (
              <motion.div
                key={client.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="grid grid-cols-12 py-3 px-3 text-sm hover:bg-slate-800/50"
              >
                <div className="col-span-4 text-slate-300 font-medium">{client.name}</div>
                <div className="col-span-2">
                  <Badge variant="outline" className={getStatusColor(client.status)}>
                    {client.status}
                  </Badge>
                </div>
                <div className="col-span-2 text-cyan-400 font-mono">{client.matchCount}</div>
                <div className="col-span-2">
                  <div className="flex items-center space-x-2">
                    <Progress value={client.progress} className="h-2 w-16 bg-slate-700">
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
                    <span className="text-xs text-slate-400">{client.progress}%</span>
                  </div>
                </div>
                <div className="col-span-2 text-slate-400 text-xs">
                  <div>{formatDate(client.timestamp)}</div>
                  <div>{formatTime(client.timestamp)}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

