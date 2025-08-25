import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Search, 
  BookOpen, 
  Copy, 
  CheckCircle, 
  AlertCircle,
  Loader2
} from 'lucide-react'
import { getApiUrl } from '@/config/api'

const VerseSearch = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [referenceQuery, setReferenceQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [referenceResults, setReferenceResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)
  const [isLookingUp, setIsLookingUp] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [copiedVerse, setCopiedVerse] = useState(null)

  const handleTextSearch = async () => {
    if (!searchQuery.trim()) return

    setIsSearching(true)
    setError(null)
    setSearchResults([])

    try {
      const response = await fetch(getApiUrl(`verses/search?query=${encodeURIComponent(searchQuery)}&limit=20`))
      const result = await response.json()

      if (result.success) {
        setSearchResults(result.verses)
        if (result.verses.length === 0) {
          setError('No verses found matching your search query.')
        }
      } else {
        setError(result.error || 'Failed to search verses')
      }
    } catch (err) {
      setError('Network error. Please check if the backend server is running.')
    } finally {
      setIsSearching(false)
    }
  }

  const handleReferenceLookup = async () => {
    if (!referenceQuery.trim()) return

    setIsLookingUp(true)
    setError(null)
    setReferenceResults([])

    try {
      const response = await fetch(getApiUrl(`verses/lookup?reference=${encodeURIComponent(referenceQuery)}`))
      const result = await response.json()

      if (result.success) {
        setReferenceResults(result.verses)
        if (result.verses.length === 0) {
          setError('No verses found for the given reference. Please check the format (e.g., "John 3:16" or "Eph. 1:5, 9").')
        }
      } else {
        setError(result.error || 'Failed to lookup verse reference')
      }
    } catch (err) {
      setError('Network error. Please check if the backend server is running.')
    } finally {
      setIsLookingUp(false)
    }
  }

  const copyToClipboard = async (verse) => {
    const text = `${verse.reference}: ${verse.text}`
    try {
      await navigator.clipboard.writeText(text)
      setCopiedVerse(verse.id)
      setSuccess('Verse copied to clipboard!')
      setTimeout(() => {
        setCopiedVerse(null)
        setSuccess(null)
      }, 2000)
    } catch (err) {
      setError('Failed to copy to clipboard')
    }
  }

  const VerseCard = ({ verse, showCopyButton = true }) => (
    <Card key={verse.id} className="mb-4">
      <CardContent className="p-4">
        <div className="flex justify-between items-start gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline" className="text-sm">
                {verse.reference}
              </Badge>
              <span className="text-xs text-gray-500">
                {verse.book_name} {verse.chapter}:{verse.verse}
              </span>
            </div>
            <p className="text-sm leading-relaxed">
              {verse.text}
            </p>
          </div>
          {showCopyButton && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(verse)}
              className="flex items-center gap-1"
            >
              {copiedVerse === verse.id ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6">
      <Tabs defaultValue="reference" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="reference" className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Reference Lookup
          </TabsTrigger>
          <TabsTrigger value="text" className="flex items-center gap-2">
            <Search className="h-4 w-4" />
            Text Search
          </TabsTrigger>
        </TabsList>

        {/* Reference Lookup Tab */}
        <TabsContent value="reference" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Look Up Bible Verses</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Enter verse reference (e.g., John 3:16, Eph. 1:5, 9)"
                  value={referenceQuery}
                  onChange={(e) => setReferenceQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleReferenceLookup()}
                  className="flex-1"
                />
                <Button 
                  onClick={handleReferenceLookup}
                  disabled={isLookingUp || !referenceQuery.trim()}
                >
                  {isLookingUp ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4" />
                  )}
                </Button>
              </div>

              <div className="text-xs text-gray-500 space-y-1">
                <p><strong>Supported formats:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Single verse: "John 3:16"</li>
                  <li>Multiple verses: "John 3:16, 17"</li>
                  <li>Verse range: "John 3:16-18"</li>
                  <li>Multiple references: "Eph. 1:5, 9; 1 John 4:8"</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Reference Results */}
          {referenceResults.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4">
                Found {referenceResults.length} verse(s)
              </h3>
              {referenceResults.map(verse => (
                <VerseCard key={verse.id} verse={verse} />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Text Search Tab */}
        <TabsContent value="text" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Search Bible Text</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Search for words or phrases in Bible verses..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleTextSearch()}
                  className="flex-1"
                />
                <Button 
                  onClick={handleTextSearch}
                  disabled={isSearching || !searchQuery.trim()}
                >
                  {isSearching ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4" />
                  )}
                </Button>
              </div>

              <p className="text-xs text-gray-500">
                Search for specific words or phrases within the Bible text. Results are limited to 20 verses.
              </p>
            </CardContent>
          </Card>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4">
                Found {searchResults.length} verse(s) containing "{searchQuery}"
              </h3>
              {searchResults.map(verse => (
                <VerseCard key={verse.id} verse={verse} />
              ))}
            </div>
          )}
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

      {/* Sample Verses */}
      <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
        <CardHeader>
          <CardTitle className="text-lg text-blue-800 dark:text-blue-200">
            Sample Verses Available
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
            <Badge variant="outline" className="justify-center">Eph. 1:5</Badge>
            <Badge variant="outline" className="justify-center">Eph. 1:9</Badge>
            <Badge variant="outline" className="justify-center">Eph. 5:1</Badge>
            <Badge variant="outline" className="justify-center">Eph. 5:2</Badge>
            <Badge variant="outline" className="justify-center">1 John 4:8</Badge>
            <Badge variant="outline" className="justify-center">1 John 1:5</Badge>
            <Badge variant="outline" className="justify-center">John 1:12</Badge>
            <Badge variant="outline" className="justify-center">Matt. 5:48</Badge>
            <Badge variant="outline" className="justify-center">2 Pet. 1:4</Badge>
          </div>
          <p className="text-xs text-blue-700 dark:text-blue-300 mt-3">
            These are sample verses from the outline. The full Recovery Version database would contain all Bible verses.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default VerseSearch

