"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { AlertCircle, Check, FileText, FolderUp, Loader2, X } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { toast } from "@/components/ui/use-toast"

// Mock data
const jobs = [
  { id: "job1", title: "City Infrastructure Project RFP" },
  { id: "job2", title: "Healthcare System Modernization" },
  { id: "job3", title: "Educational Technology Initiative" },
]

export default function BulkUpload() {
  const [files, setFiles] = useState([])
  const [selectedJob, setSelectedJob] = useState("")
  const [isUploading, setIsUploading] = useState(false)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files).map((file) => ({
        id: Math.random().toString(36).substring(2, 9),
        file,
        status: "pending", // pending, uploading, success, error
        progress: 0,
      }))
      setFiles([...files, ...newFiles])
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    if (files.length === 0) {
      toast({
        title: "No files selected",
        description: "Please select at least one PDF file to upload.",
        variant: "destructive",
      })
      return
    }

    if (!selectedJob) {
      toast({
        title: "No job selected",
        description: "Please select a job for these documents.",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)

    // Simulate upload and processing for each file
    const updatedFiles = files.map((file) => ({
      ...file,
      status: "uploading",
    }))
    setFiles(updatedFiles)

    // Process each file with a delay to simulate sequential uploads
    updatedFiles.forEach((file, index) => {
      setTimeout(() => {
        setFiles((prevFiles) => {
          const newFiles = [...prevFiles]
          const fileIndex = newFiles.findIndex((f) => f.id === file.id)

          if (fileIndex !== -1) {
            // Simulate random success/failure
            const success = Math.random() > 0.2
            newFiles[fileIndex] = {
              ...newFiles[fileIndex],
              status: success ? "success" : "error",
              progress: 100,
            }
          }

          // If this is the last file, set uploading to false
          if (index === updatedFiles.length - 1) {
            setTimeout(() => setIsUploading(false), 500)
          }

          return newFiles
        })
      }, index * 1000) // Stagger uploads by 1 second
    })

    toast({
      title: "Upload started",
      description: `Uploading ${files.length} files. Please wait...`,
    })
  }

  const removeFile = (id) => {
    setFiles(files.filter((file) => file.id !== id))
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case "pending":
        return <FileText className="h-4 w-4 text-slate-400" />
      case "uploading":
        return <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />
      case "success":
        return <Check className="h-4 w-4 text-green-400" />
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-400" />
      default:
        return <FileText className="h-4 w-4 text-slate-400" />
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case "pending":
        return <Badge className="bg-slate-500/20 text-slate-400 border-slate-500/50">Pending</Badge>
      case "uploading":
        return <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/50">Uploading</Badge>
      case "success":
        return <Badge className="bg-green-500/20 text-green-400 border-green-500/50">Uploaded</Badge>
      case "error":
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/50">Failed</Badge>
      default:
        return <Badge className="bg-slate-500/20 text-slate-400 border-slate-500/50">Pending</Badge>
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Bulk Upload Documents</h1>
        <p className="text-slate-400">Upload multiple client documents for analysis</p>
      </div>

      <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
        <CardHeader className="border-b border-slate-700/50 pb-3">
          <CardTitle className="text-slate-100 flex items-center">
            <FolderUp className="mr-2 h-5 w-5 text-cyan-500" />
            Bulk Upload
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="job-select" className="text-slate-300">
                Select Job
              </Label>
              <Select value={selectedJob} onValueChange={setSelectedJob} disabled={isUploading}>
                <SelectTrigger id="job-select" className="bg-slate-800/50 border-slate-700 text-slate-200 mt-1">
                  <SelectValue placeholder="Select a job" />
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
              <Label className="text-slate-300">Upload PDFs</Label>
              <div className="mt-1">
                <div className="border-2 border-dashed border-slate-700 rounded-lg p-8 text-center cursor-pointer hover:border-cyan-500/50 transition-colors">
                  <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    accept=".pdf"
                    multiple
                    onChange={handleFileChange}
                    disabled={isUploading}
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <FolderUp className="h-8 w-8 text-slate-500 mx-auto mb-4" />
                    <p className="text-slate-400 mb-2">Drag and drop multiple PDFs here, or click to browse</p>
                    <p className="text-xs text-slate-500">Supports multiple PDF files up to 10MB each</p>
                  </label>
                </div>
              </div>
            </div>

            {files.length > 0 && (
              <div className="bg-slate-800/30 rounded-lg border border-slate-700/50 overflow-hidden">
                <div className="grid grid-cols-12 text-xs text-slate-400 p-3 border-b border-slate-700/50 bg-slate-800/50">
                  <div className="col-span-6">File Name</div>
                  <div className="col-span-2">Size</div>
                  <div className="col-span-3">Status</div>
                  <div className="col-span-1"></div>
                </div>

                <div className="divide-y divide-slate-700/30">
                  {files.map((file, index) => (
                    <motion.div
                      key={file.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.05 }}
                      className="grid grid-cols-12 py-3 px-3 text-sm items-center"
                    >
                      <div className="col-span-6 flex items-center">
                        {getStatusIcon(file.status)}
                        <span className="ml-2 text-slate-300 truncate">{file.file.name}</span>
                      </div>
                      <div className="col-span-2 text-slate-400 text-xs">{(file.file.size / 1024).toFixed(0)} KB</div>
                      <div className="col-span-3">{getStatusBadge(file.status)}</div>
                      <div className="col-span-1 flex justify-end">
                        {file.status !== "uploading" && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-7 w-7 text-slate-400 hover:text-slate-100"
                            onClick={() => removeFile(file.id)}
                            disabled={isUploading}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-between items-center">
              <div className="text-sm text-slate-400">
                {files.length} {files.length === 1 ? "file" : "files"} selected
              </div>
              <div className="flex space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  className="border-slate-700 text-slate-400"
                  onClick={() => setFiles([])}
                  disabled={files.length === 0 || isUploading}
                >
                  Clear All
                </Button>
                <Button
                  type="submit"
                  disabled={files.length === 0 || isUploading || !selectedJob}
                  className="bg-cyan-600 hover:bg-cyan-700"
                >
                  {isUploading ? (
                    <>
                      <div className="animate-spin mr-2 h-4 w-4 border-2 border-slate-200 border-t-transparent rounded-full" />
                      Uploading...
                    </>
                  ) : (
                    "Upload & Analyze All"
                  )}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

