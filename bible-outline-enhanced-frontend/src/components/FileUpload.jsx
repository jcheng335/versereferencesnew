import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { getApiUrl } from '@/config/api'

const FileUpload = ({ onFileProcessed }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleFileSelect = (e) => {
    const files = e.target.files
    if (files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleFileUpload = async (file) => {
    // Validate file type
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ]
    
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a PDF or Word document (.pdf, .doc, .docx)')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }

    setIsUploading(true)
    setError(null)
    setSuccess(null)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + 10
        })
      }, 200)

      const response = await fetch(getApiUrl('upload'), {
        method: 'POST',
        body: formData
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      const result = await response.json()

      if (result.success) {
        setSuccess(`Document processed successfully! Found ${result.references_found || 0} verse references.`)
        onFileProcessed(result)
      } else {
        setError(result.error || 'Failed to process document')
      }
    } catch (err) {
      setError('Network error. Please check if the backend server is running.')
    } finally {
      setIsUploading(false)
      setTimeout(() => {
        setUploadProgress(0)
      }, 2000)
    }
  }

  return (
    <div className="space-y-4">
      {/* Drag and Drop Area */}
      <Card
        className={`border-2 border-dashed transition-colors cursor-pointer ${
          isDragging
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <CardContent className="flex flex-col items-center justify-center py-12">
          {isUploading ? (
            <Loader2 className="h-12 w-12 text-blue-500 animate-spin mb-4" />
          ) : (
            <Upload className="h-12 w-12 text-gray-400 mb-4" />
          )}
          
          <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
            {isUploading ? 'Processing Document...' : 'Upload Your Outline'}
          </h3>
          
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center mb-4">
            {isUploading
              ? 'Please wait while we extract text and identify verse references'
              : 'Drag and drop your PDF or Word document here, or click to browse'}
          </p>

          {!isUploading && (
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <FileText className="h-4 w-4" />
              <span>Supports: PDF, DOC, DOCX (max 10MB)</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.doc,.docx"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Progress Bar */}
      {isUploading && (
        <div className="space-y-2">
          <Progress value={uploadProgress} className="w-full" />
          <p className="text-sm text-gray-500 text-center">
            {uploadProgress < 90 ? 'Uploading...' : 'Processing document...'}
          </p>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <Alert className="border-green-200 bg-green-50 dark:bg-green-950">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-700 dark:text-green-300">
            {success}
          </AlertDescription>
        </Alert>
      )}

      {/* Error Message */}
      {error && (
        <Alert className="border-red-200 bg-red-50 dark:bg-red-950">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-700 dark:text-red-300">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Manual Upload Button */}
      {!isUploading && (
        <div className="text-center">
          <Button
            onClick={() => fileInputRef.current?.click()}
            variant="outline"
            className="w-full sm:w-auto"
          >
            <Upload className="h-4 w-4 mr-2" />
            Choose File
          </Button>
        </div>
      )}
    </div>
  )
}

export default FileUpload

