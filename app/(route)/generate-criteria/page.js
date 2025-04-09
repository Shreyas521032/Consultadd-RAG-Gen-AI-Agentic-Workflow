"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { AlertCircle, Check, FileText, Upload } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Badge } from "@/components/ui/badge"
import { toast } from "@/components/ui/use-toast"

export default function GenerateCriteria() {
  const [file, setFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [criteria, setCriteria] = useState(null)

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

    setIsUploading(true)

    // Simulate upload
    setTimeout(() => {
      setIsUploading(false)
      setIsProcessing(true)

      // Simulate processing
      setTimeout(() => {
        setIsProcessing(false)

        // Mock criteria extraction
        setCriteria([
          { id: 1, name: "Minimum 5 years experience in similar projects", category: "Experience" },
          { id: 2, name: "ISO 9001 Certification", category: "Certifications" },
          { id: 3, name: "Local business presence", category: "Location" },
          { id: 4, name: "Previous government contracts", category: "Experience" },
          { id: 5, name: "Sustainability commitment", category: "Policy" },
          { id: 6, name: "Liability insurance ($2M+)", category: "Insurance" },
          { id: 7, name: "Workforce diversity program", category: "Policy" },
          { id: 8, name: "24/7 Support capability", category: "Service" },
          { id: 9, name: "Disaster recovery plan", category: "Policy" },
          { id: 10, name: "Financial stability (5yr+)", category: "Financial" },
        ])

        toast({
          title: "Criteria extracted successfully",
          description: "10 criteria have been identified from the document.",
        })
      }, 3000)
    }, 1500)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Generate Criteria</h1>
        <p className="text-slate-400">Upload a Eligibility Criteria Document PDF to extract eligibility criteria</p>
      </div>

      <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
        <CardHeader className="border-b border-slate-700/50 pb-3">
          <CardTitle className="text-slate-100 flex items-center">
            <FileText className="mr-2 h-5 w-5 text-cyan-500" />
            Upload Eligibility Criteria Document 
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <div className="border-2 border-dashed border-slate-700 rounded-lg p-10 text-center cursor-pointer hover:border-cyan-500/50 transition-colors">
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  accept=".pdf"
                  onChange={handleFileChange}
                  disabled={isUploading || isProcessing}
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <Upload className="h-10 w-10 text-slate-500 mx-auto mb-4" />
                  <p className="text-slate-400 mb-2">
                    {file ? file.name : "Drag and drop your PDF here, or click to browse"}
                  </p>
                  <p className="text-xs text-slate-500">Supports PDF files up to 10MB</p>
                </label>
              </div>
            </div>

            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={!file || isUploading || isProcessing}
                className="bg-cyan-600 hover:bg-cyan-700"
              >
                {isUploading ? (
                  <>
                    <div className="animate-spin mr-2 h-4 w-4 border-2 border-slate-200 border-t-transparent rounded-full" />
                    Uploading...
                  </>
                ) : isProcessing ? (
                  <>
                    <div className="animate-spin mr-2 h-4 w-4 border-2 border-slate-200 border-t-transparent rounded-full" />
                    Processing...
                  </>
                ) : (
                  "Extract Criteria"
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {criteria && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
            <CardHeader className="border-b border-slate-700/50 pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-slate-100 flex items-center">
                  <Check className="mr-2 h-5 w-5 text-green-500" />
                  Extracted Criteria
                </CardTitle>
                <Badge className="bg-green-500/20 text-green-400 border-green-500/50">
                  {criteria.length} Criteria Found
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              <div className="mb-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                <div className="flex items-start">
                  <AlertCircle className="h-5 w-5 text-amber-500 mr-2 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-medium text-slate-200">AI-Generated Content</h4>
                    <p className="text-xs text-slate-400 mt-1">
                      The following criteria were automatically extracted from your document. Please review for accuracy
                      before proceeding.
                    </p>
                  </div>
                </div>
              </div>

              <Accordion type="single" collapsible className="w-full">
                {Object.entries(
                  criteria.reduce((acc, criterion) => {
                    if (!acc[criterion.category]) {
                      acc[criterion.category] = []
                    }
                    acc[criterion.category].push(criterion)
                    return acc
                  }, {}),
                ).map(([category, items], index) => (
                  <AccordionItem key={category} value={category} className="border-slate-700/50">
                    <AccordionTrigger className="text-slate-200 hover:text-slate-100 hover:no-underline">
                      <div className="flex items-center">
                        <span>{category}</span>
                        <Badge className="ml-2 bg-slate-700/50 text-slate-300 border-slate-600/50">
                          {items.length}
                        </Badge>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="space-y-2 py-2">
                        {items.map((criterion) => (
                          <div key={criterion.id} className="p-3 bg-slate-800/50 rounded-md border border-slate-700/50">
                            <div className="flex items-center justify-between">
                              <div className="text-slate-300">{criterion.name}</div>
                              <Badge variant="outline" className="bg-cyan-500/10 text-cyan-400 border-cyan-500/30">
                                ID: {criterion.id}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>

              <div className="mt-6 flex justify-end space-x-3">
                <Button variant="outline" className="border-slate-700 text-slate-400">
                  Edit Criteria
                </Button>
                <Button className="bg-cyan-600 hover:bg-cyan-700">Save Criteria</Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  )
}

