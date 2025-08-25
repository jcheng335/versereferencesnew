import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Download, 
  RefreshCw, 
  Eye, 
  Edit, 
  BookOpen, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Copy
} from 'lucide-react'
import { getApiUrl } from '@/config/api'

const OutlineEditor = ({ sessionData }) => {
  const [content, setContent] = useState('')
  const [originalContent, setOriginalContent] = useState('')
  const [populatedContent, setPopulatedContent] = useState('')
  const [detectedReferences, setDetectedReferences] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [activeView, setActiveView] = useState('original')

  useEffect(() => {
    if (sessionData) {
      setOriginalContent(sessionData.content || '')
      setContent(sessionData.content || '')
      setDetectedReferences(sessionData.references || [])
    }
  }, [sessionData])

  const handlePopulateVerses = async () => {
    if (!sessionData?.session_id) return

    setIsProcessing(true)
    setError(null)
    setSuccess(null)

    try {
      const response = await fetch(getApiUrl('process-document'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionData.session_id,
          format: 'inline'
        })
      })

      const result = await response.json()

      if (result.success) {
        setPopulatedContent(result.content)
        setSuccess(`Successfully populated ${result.verse_count} verses!`)
        setActiveView('populated')
      } else {
        setError(result.error || 'Failed to populate verses')
      }
    } catch (err) {
      setError('Network error. Please check if the backend server is running.')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleExport = async () => {
    if (!sessionData?.session_id) return

    setIsExporting(true)
    setError(null)

    try {
      const response = await fetch(getApiUrl(`export/${sessionData.session_id}`))
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `church_outline_${sessionData.session_id}.docx`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        setSuccess('Document exported successfully!')
      } else {
        const result = await response.json()
        setError(result.error || 'Failed to export document')
      }
    } catch (err) {
      setError('Network error. Please check if the backend server is running.')
    } finally {
      setIsExporting(false)
    }
  }

  const handleContentUpdate = async () => {
    if (!sessionData?.session_id) return

    try {
      const response = await fetch(getApiUrl(`session/${sessionData.session_id}`), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: content
        })
      })

      const result = await response.json()
      if (result.success) {
        setSuccess('Content updated successfully!')
      }
    } catch (err) {
      setError('Failed to update content')
    }
  }

  const handleCopyCleanText = async () => {
    if (!sessionData?.session_id) return

    try {
      // Get clean text from backend
      const response = await fetch(getApiUrl(`export-clean/${sessionData.session_id}`))
      const result = await response.json()
      
      if (result.success && result.clean_text) {
        await navigator.clipboard.writeText(result.clean_text)
        setSuccess('Content copied to clipboard! Ready to paste into OneNote.')
      } else {
        setError('Failed to get clean text for copying.')
      }
    } catch (err) {
      setError('Failed to copy to clipboard. Please try selecting and copying manually.')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Outline Editor
              </CardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                File: {sessionData?.original_filename}
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                onClick={handlePopulateVerses}
                disabled={isProcessing}
                className="flex items-center gap-2"
              >
                {isProcessing ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4" />
                )}
                {isProcessing ? 'Processing...' : 'Populate Verses'}
              </Button>
              <Button
                onClick={handleExport}
                disabled={isExporting || !populatedContent}
                variant="outline"
                className="flex items-center gap-2"
              >
                {isExporting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Download className="h-4 w-4" />
                )}
                {isExporting ? 'Exporting...' : 'Export Word'}
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Detected References */}
      {detectedReferences.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Detected Verse References</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {detectedReferences.map((ref, index) => (
                <Badge key={index} variant="secondary" className="text-sm">
                  {ref}
                </Badge>
              ))}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">
              Found {detectedReferences.length} verse reference(s) in your document.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Content Tabs */}
      <Tabs value={activeView} onValueChange={setActiveView}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="original" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Original
          </TabsTrigger>
          <TabsTrigger value="edit" className="flex items-center gap-2">
            <Edit className="h-4 w-4" />
            Edit
          </TabsTrigger>
          <TabsTrigger 
            value="populated" 
            className="flex items-center gap-2"
            disabled={!populatedContent}
          >
            <BookOpen className="h-4 w-4" />
            With Verses
          </TabsTrigger>
        </TabsList>

        {/* Original Content View */}
        <TabsContent value="original">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Original Document Content</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm font-mono">
                  {originalContent}
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Edit Content */}
        <TabsContent value="edit">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Edit Content</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Edit your outline content here..."
                className="min-h-96 font-mono text-sm"
              />
              <div className="flex justify-end">
                <Button onClick={handleContentUpdate}>
                  Save Changes
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Populated Content View */}
        <TabsContent value="populated">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className="text-lg">Content with Bible Verses</CardTitle>
                {populatedContent && (
                  <Button
                    onClick={handleCopyCleanText}
                    variant="outline"
                    size="sm"
                    className="flex items-center gap-2"
                  >
                    <Copy className="h-4 w-4" />
                    Copy for OneNote
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {populatedContent ? (
                <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg max-h-96 overflow-y-auto">
                  <div 
                    className="text-sm font-mono whitespace-pre-wrap"
                    dangerouslySetInnerHTML={{ 
                      __html: populatedContent
                        .replace(/\n/g, '<br>')
                        .replace(/<span class='verse-ref'>/g, '<span class="verse-ref">')
                        .replace(/<span class='verse-text'>/g, '<span class="verse-text">')
                    }} 
                  />
                </div>
              ) : (
                <div className="text-center py-8">
                  <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-300">
                    Click "Populate Verses" to see your outline with Bible verses.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

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
    </div>
  )
}

export default OutlineEditor

