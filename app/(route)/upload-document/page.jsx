"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { FileText, Upload } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { toast } from "@/components/ui/use-toast"

// Mock data
const jobs = [
  { id: "job1", title: "City Infrastructure Project RFP" },
  { id: "job2", title: "Healthcare System Modernization" },
  { id: "job3", title: "Educational Technology Initiative" },
]

export default function UploadDocument() {
  const [file, setFile] = useState(null)
  const [selectedJob, setSelectedJob] = useState("")
  const [clientName, setClientName] = useState("")
  const [isUploading, setIsUploading] = useState(false)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!file) {
      toast({
        title: "No file selected",
        description: "Please select a PDF file to upload.",
        variant: "destructive",
      })
      return
    }

    if (!selectedJob) {
      toast({
        title: "No job selected",
        description: "Please select a project for this document.",
        variant: "destructive",
      })
      return
    }

    if (!clientName.trim()) {
      toast({
        title: "Client name required",
        description: "Please enter a client name.",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)

    // Simulate upload and processing
    setTimeout(() => {
      setIsUploading(false)
      setFile(null)
      setClientName("")

      toast({
        title: "Document uploaded successfully",
        description: "The document has been uploaded and is being processed.",
      })
    }, 2000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Upload Client RFP Document</h1>
        <p className="text-slate-400">Upload a single client document for analysis</p>
      </div>

      <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
        <CardHeader className="border-b border-slate-700/50 pb-3">
          <CardTitle className="text-slate-100 flex items-center">
            <FileText className="mr-2 h-5 w-5 text-cyan-500" />
            Upload Document
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div>
                <Label htmlFor="client-name" className="text-slate-300">
                  Client Name
                </Label>
                <Input
                  id="client-name"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  placeholder="Enter client name"
                  className="bg-slate-800/50 border-slate-700 text-slate-200 mt-1"
                  disabled={isUploading}
                />
              </div>

              <div>
                <Label htmlFor="job-select" className="text-slate-300">
                  Select Job
                </Label>
                <Select value={selectedJob} onValueChange={setSelectedJob} disabled={isUploading}>
                  <SelectTrigger id="job-select" className="bg-slate-800/50 border-slate-700 text-slate-200 mt-1">
                    <SelectValue placeholder="Select a project" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700 text-slate-200">
                    {jobs.map((job) => (
                      <SelectItem
                        key={job.id}
                        value={job.id}
                        className="text-slate-200 focus:bg-slate-700 focus:text-slate-200"
                      >
                        {job.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label className="text-slate-300">Upload PDF</Label>
                <div className="mt-1">
                  <div className="border-2 border-dashed border-slate-700 rounded-lg p-8 text-center cursor-pointer hover:border-cyan-500/50 transition-colors">
                    <input
                      type="file"
                      id="file-upload"
                      className="hidden"
                      accept=".pdf"
                      onChange={handleFileChange}
                      disabled={isUploading}
                    />
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <Upload className="h-8 w-8 text-slate-500 mx-auto mb-4" />
                      <p className="text-slate-400 mb-2">
                        {file ? file.name : "Drag and drop your PDF here, or click to browse"}
                      </p>
                      <p className="text-xs text-slate-500">Supports PDF files up to 10MB</p>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <Button type="submit" disabled={isUploading} className="bg-cyan-600 hover:bg-cyan-700">
                {isUploading ? (
                  <>
                    <div className="animate-spin mr-2 h-4 w-4 border-2 border-slate-200 border-t-transparent rounded-full" />
                    Uploading...
                  </>
                ) : (
                  "Upload & Analyze"
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
          <CardHeader className="border-b border-slate-700/50 pb-3">
            <CardTitle className="text-slate-100 flex items-center">
              <FileText className="mr-2 h-5 w-5 text-cyan-500" />
              How It Works
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
                <div className="h-10 w-10 rounded-full bg-cyan-500/20 flex items-center justify-center mb-4">
                  <span className="text-cyan-400 font-bold">1</span>
                </div>
                <h3 className="text-slate-200 font-medium mb-2">Upload Document</h3>
                <p className="text-sm text-slate-400">
                  Upload a client's PDF document and select the relevant project.
                </p>
              </div>

              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
                <div className="h-10 w-10 rounded-full bg-cyan-500/20 flex items-center justify-center mb-4">
                  <span className="text-cyan-400 font-bold">2</span>
                </div>
                <h3 className="text-slate-200 font-medium mb-2">AI Analysis</h3>
                <p className="text-sm text-slate-400">
                  Our AI system analyzes the document against the project criteria.
                </p>
              </div>

              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
                <div className="h-10 w-10 rounded-full bg-cyan-500/20 flex items-center justify-center mb-4">
                  <span className="text-cyan-400 font-bold">3</span>
                </div>
                <h3 className="text-slate-200 font-medium mb-2">View Results</h3>
                <p className="text-sm text-slate-400">Review the analysis results and download detailed reports.</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

