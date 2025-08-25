import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { Label } from '@/components/ui/label.jsx'
import { 
  Upload, 
  Brain, 
  Sparkles, 
  AlertCircle, 
  CheckCircle, 
  ThumbsUp, 
  ThumbsDown,
  BarChart3,
  Settings
} from 'lucide-react'
import { getApiUrl } from '@/config/api'

const EnhancedUpload = ({ onProcessed }) => {
  const [file, setFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [useLLM, setUseLLM] = useState(true)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [feedback, setFeedback] = useState([])
  const [showSettings, setShowSettings] = useState(false)
  const [apiKey, setApiKey] = useState('')

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setIsUploading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('use_llm', useLLM)

    try {
      const response = await fetch(getApiUrl('enhanced/upload'), {
        method: 'POST',
        body: formData
      })

      const result = await response.json()

      if (result.success) {
        setSessionId(result.session_id)
        setResults(result)
        onProcessed(result)
      } else {
        setError(result.error || 'Processing failed')
      }
    } catch (err) {
      setError('Network error. Please check your connection.')
    } finally {
      setIsUploading(false)
    }
  }

  const handlePopulate = async () => {
    if (!sessionId) return

    try {
      const response = await fetch(getApiUrl(`enhanced/populate/${sessionId}`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format: 'inline' })
      })

      const result = await response.json()
      if (result.success) {
        onProcessed({ ...results, populated_content: result.populated_content })
      }
    } catch (err) {
      setError('Failed to populate verses')
    }
  }

  const handleFeedback = async (isPositive) => {
    if (!sessionId) return

    const corrections = prompt('Please describe any corrections needed:')
    if (!corrections) return

    try {
      const response = await fetch(getApiUrl(`enhanced/feedback/${sessionId}`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          corrections: [{ type: isPositive ? 'positive' : 'negative', description: corrections }]
        })
      })

      const result = await response.json()
      if (result.success) {
        setFeedback([...feedback, { isPositive, corrections }])
      }
    } catch (err) {
      console.error('Feedback error:', err)
    }
  }

  const handleSaveApiKey = async () => {
    try {
      const response = await fetch(getApiUrl('enhanced/settings'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ openai_key: apiKey })
      })

      const result = await response.json()
      if (result.success) {
        setShowSettings(false)
        alert('API key saved successfully')
      }
    } catch (err) {
      setError('Failed to save API key')
    }
  }

  const getTrainingReport = async () => {
    try {
      const response = await fetch(getApiUrl('enhanced/training-report'))
      const report = await response.json()
      alert(JSON.stringify(report, null, 2))
    } catch (err) {
      console.error('Report error:', err)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Enhanced AI-Powered Verse Detection
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Settings */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Switch
                id="use-llm"
                checked={useLLM}
                onCheckedChange={setUseLLM}
              />
              <Label htmlFor="use-llm" className="flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                Use OpenAI for enhanced accuracy
              </Label>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Settings className="h-4 w-4" />
            </Button>
          </div>

          {/* API Key Settings */}
          {showSettings && (
            <Card className="p-4 bg-gray-50">
              <div className="space-y-2">
                <Label>OpenAI API Key</Label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    className="flex-1 px-3 py-2 border rounded"
                    placeholder="sk-..."
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                  />
                  <Button onClick={handleSaveApiKey} size="sm">
                    Save
                  </Button>
                </div>
                <p className="text-xs text-gray-600">
                  Get your key from{' '}
                  <a
                    href="https://platform.openai.com/api-keys"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 underline"
                  >
                    OpenAI Platform
                  </a>
                </p>
              </div>
            </Card>
          )}

          {/* File Upload */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <Upload className="h-12 w-12 mx-auto text-gray-400" />
              <p className="mt-2">
                {file ? file.name : 'Click to select or drag and drop'}
              </p>
            </label>
          </div>

          {/* Upload Button */}
          <Button
            onClick={handleUpload}
            disabled={!file || isUploading}
            className="w-full"
          >
            {isUploading ? 'Processing with AI...' : 'Upload and Analyze'}
          </Button>

          {/* Progress */}
          {isUploading && (
            <div className="space-y-2">
              <Progress value={50} />
              <p className="text-sm text-center text-gray-600">
                {useLLM ? 'Using AI to validate references...' : 'Processing document...'}
              </p>
            </div>
          )}

          {/* Results */}
          {results && (
            <Card className="p-4 bg-green-50">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="font-semibold">Processing Complete</span>
                </div>
                <div className="text-sm space-y-1">
                  <p>References found: {results.references_found}</p>
                  <p>Total verses: {results.total_verses}</p>
                  <p>Confidence: {(results.average_confidence * 100).toFixed(1)}%</p>
                </div>
                <div className="flex gap-2 mt-3">
                  <Button onClick={handlePopulate} size="sm">
                    Populate Verses
                  </Button>
                  <Button
                    onClick={() => handleFeedback(true)}
                    size="sm"
                    variant="outline"
                  >
                    <ThumbsUp className="h-4 w-4" />
                  </Button>
                  <Button
                    onClick={() => handleFeedback(false)}
                    size="sm"
                    variant="outline"
                  >
                    <ThumbsDown className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* Training Report */}
          <div className="flex justify-end">
            <Button
              onClick={getTrainingReport}
              variant="outline"
              size="sm"
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              Training Report
            </Button>
          </div>

          {/* Error */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default EnhancedUpload