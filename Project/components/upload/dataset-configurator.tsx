"use client"

import { useState, useRef } from "react"
import { Upload, FileText, CheckCircle, Database } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"

export function DatasetConfigurator() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [columns, setColumns] = useState<string[]>([])
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  
  const [targetCol, setTargetCol] = useState("")
  const [sensitiveCol, setSensitiveCol] = useState("")
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      if (!selectedFile.name.endsWith('.csv')) {
        alert("Please upload a CSV file.")
        return
      }
      setFile(selectedFile)
      
      // Upload right away to get columns
      setLoading(true)
      const formData = new FormData()
      formData.append("file", selectedFile)
      
      try {
        const res = await fetch("http://localhost:8001/api/upload", {
          method: "POST",
          body: formData
        })
        
        if (!res.ok) throw new Error("Upload failed")
        const data = await res.json()
        setColumns(data.columns)
        setStep(2)
      } catch (err) {
        alert("Failed to upload dataset.")
        setFile(null)
      } finally {
        setLoading(false)
      }
    }
  }

  const handleConfigure = async () => {
    if (!targetCol || !sensitiveCol) {
      alert("Please select both a Target and Protected Attribute.")
      return
    }
    
    setLoading(true)
    const formData = new FormData()
    formData.append("target_col", targetCol)
    formData.append("sensitive_col", sensitiveCol)
    
    try {
      const res = await fetch("http://localhost:8001/api/configure", {
        method: "POST",
        body: formData
      })
      if (!res.ok) throw new Error("Configuration failed")
      
      // Redirect to dashboard explicitly to trigger re-renders everywhere
      router.push('/')
      router.refresh()
    } catch (err) {
      alert("Failed to configure AI pipeline.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto glass p-8 rounded-xl border border-primary/20 shadow-2xl">
      <div className="flex flex-col items-center text-center space-y-4 mb-8">
        <div className="p-4 rounded-full bg-primary/10 mb-2">
          <Database className="w-12 h-12 text-primary" />
        </div>
        <h2 className="text-3xl font-bold tracking-tight text-white">Seed the Fairness Engine</h2>
        <p className="text-muted-foreground w-[80%]">
          Upload any historical dataset (CSV) to analyze demographic bias, optimize thresholds, and explain predictions via our scalable architecture.
        </p>
      </div>

      {step === 1 && (
        <div 
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-primary/30 rounded-lg p-12 flex flex-col items-center justify-center cursor-pointer hover:border-primary/60 hover:bg-white/5 transition-all duration-300"
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            className="hidden" 
            accept=".csv"
            onChange={handleFileChange}
          />
          {loading ? (
            <div className="animate-pulse flex flex-col items-center">
              <Upload className="w-10 h-10 text-primary mb-4 animate-bounce" />
              <p className="text-lg font-medium text-white">Ingesting CSV Headers...</p>
            </div>
          ) : (
            <>
              <FileText className="w-12 h-12 text-primary mb-4" />
              <p className="text-xl font-semibold mb-2 text-white">Upload your Dataset</p>
              <p className="text-sm text-muted-foreground">Drop a .csv file here, or click to select</p>
            </>
          )}
        </div>
      )}

      {step === 2 && (
        <div className="space-y-6 animate-in slide-in-from-bottom-4 fade-in duration-500">
          <div className="flex items-center gap-3 p-4 bg-primary/10 rounded-lg border border-primary/20">
            <CheckCircle className="w-6 h-6 text-primary" />
            <div>
              <p className="font-semibold text-white">File Uploaded Successfully</p>
              <p className="text-sm text-muted-foreground">{file?.name}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">
                Target Variable (What is the AI predicting?)
              </label>
              <select 
                className="w-full p-3 rounded-md bg-black/40 border border-white/10 text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none"
                value={targetCol}
                onChange={(e) => setTargetCol(e.target.value)}
              >
                <option value="">Select Target Column...</option>
                {columns.map(col => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">
                Protected Attribute (Audit for Demographic Bias against...)
              </label>
              <select 
                className="w-full p-3 rounded-md bg-black/40 border border-white/10 text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none"
                value={sensitiveCol}
                onChange={(e) => setSensitiveCol(e.target.value)}
              >
                <option value="">Select Protected Column...</option>
                {columns.map(col => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
            </div>
          </div>

          <Button 
            onClick={handleConfigure} 
            disabled={loading || !targetCol || !sensitiveCol}
            className="w-full h-12 text-lg font-semibold glow-cyan"
          >
            {loading ? "Spinning up Engines..." : "Initialize Intelligence Pipeline"}
          </Button>
        </div>
      )}
    </div>
  )
}
