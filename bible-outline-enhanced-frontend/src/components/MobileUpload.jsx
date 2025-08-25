import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  Camera, 
  Upload, 
  Image as ImageIcon, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  FileText,
  Eye
} from 'lucide-react'

const MobileUpload = ({ onFileProcessed }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [previewImage, setPreviewImage] = useState(null)
  const [extractedText, setExtractedText] = useState('')
  const [showPreview, setShowPreview] = useState(false)
  const fileInputRef = useRef(null)
  const cameraInputRef = useRef(null)

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
      handleImageUpload(files[0])
    }
  }

  const handleFileSelect = (e) => {
    const files = e.target.files
    if (files.length > 0) {
      handleImageUpload(files[0])
    }
  }

  const handleImageUpload = async (file) => {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg']
    
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a JPG or PNG image')
      return
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Image size must be less than 5MB')
      return
    }

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setPreviewImage(e.target.result)
      setShowPreview(true)
    }
    reader.readAsDataURL(file)

    setIsProcessing(true)
    setError(null)
    setSuccess(null)
    setUploadProgress(0)
    setExtractedText('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Simulate progress for OCR processing
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 80) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + 10
        })
      }, 300)

      const response = await fetch('/api/upload-image', {
        method: 'POST',
        body: formData
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      const result = await response.json()

      if (result.success) {
        const ocrText = result.ocr_result?.text || ''
        const docResult = result.document_result

        setExtractedText(ocrText)
        setSuccess(`OCR completed! Extracted text and found ${docResult?.reference_count || 0} verse references.`)
        
        if (docResult?.success) {
          onFileProcessed(docResult)
        }
      } else {
        setError(result.error || 'Failed to process image')
      }
    } catch (err) {
      setError('Network error. Please check if the backend server is running.')
    } finally {
      setIsProcessing(false)
      setTimeout(() => {
        setUploadProgress(0)
      }, 2000)
    }
  }

  const resetUpload = () => {
    setPreviewImage(null)
    setExtractedText('')
    setShowPreview(false)
    setError(null)
    setSuccess(null)
    setUploadProgress(0)
  }

  return (
    <div className="space-y-4">
      {/* Image Preview */}
      {showPreview && previewImage && (
        <Card>
          <CardContent className="p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Image Preview</h3>
              <Button variant="outline" size="sm" onClick={resetUpload}>
                Upload New Image
              </Button>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-medium mb-2">Uploaded Image</h4>
                <img
                  src={previewImage}
                  alt="Uploaded outline"
                  className="w-full h-64 object-contain border rounded-lg bg-gray-50 dark:bg-gray-900"
                />
              </div>
              {extractedText && (
                <div>
                  <h4 className="text-sm font-medium mb-2">Extracted Text</h4>
                  <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-lg h-64 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-xs font-mono">
                      {extractedText}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Upload Area */}
      {!showPreview && (
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
            {isProcessing ? (
              <Loader2 className="h-12 w-12 text-blue-500 animate-spin mb-4" />
            ) : (
              <ImageIcon className="h-12 w-12 text-gray-400 mb-4" />
            )}
            
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
              {isProcessing ? 'Processing Image...' : 'Upload Outline Photo'}
            </h3>
            
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center mb-4">
              {isProcessing
                ? 'Using OCR to extract text from your image'
                : 'Take a photo of your outline or upload an existing image'}
            </p>

            {!isProcessing && (
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <ImageIcon className="h-4 w-4" />
                <span>Supports: JPG, PNG (max 5MB)</span>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Hidden File Inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Progress Bar */}
      {isProcessing && (
        <div className="space-y-2">
          <Progress value={uploadProgress} className="w-full" />
          <p className="text-sm text-gray-500 text-center">
            {uploadProgress < 50 ? 'Uploading image...' : 
             uploadProgress < 80 ? 'Processing with OCR...' : 
             'Analyzing text...'}
          </p>
        </div>
      )}

      {/* Action Buttons */}
      {!isProcessing && !showPreview && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Button
            onClick={() => cameraInputRef.current?.click()}
            className="flex items-center gap-2"
          >
            <Camera className="h-4 w-4" />
            Take Photo
          </Button>
          <Button
            onClick={() => fileInputRef.current?.click()}
            variant="outline"
            className="flex items-center gap-2"
          >
            <Upload className="h-4 w-4" />
            Upload Image
          </Button>
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

      {/* OCR Tips */}
      {!showPreview && (
        <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
          <CardContent className="p-4">
            <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-200 mb-2">
              Tips for Better OCR Results
            </h4>
            <ul className="text-xs text-blue-700 dark:text-blue-300 space-y-1">
              <li>• Ensure good lighting and avoid shadows</li>
              <li>• Keep the camera steady and text in focus</li>
              <li>• Make sure text is clearly visible and not blurry</li>
              <li>• Avoid reflections and glare on the paper</li>
              <li>• Capture the entire outline in the frame</li>
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default MobileUpload

