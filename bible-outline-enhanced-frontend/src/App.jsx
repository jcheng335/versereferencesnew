import React, { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Upload, FileText, Smartphone, Download, BookOpen, Search, Star, CreditCard } from 'lucide-react'
import FileUpload from './components/FileUpload'
import OutlineEditor from './components/OutlineEditor'
import MobileUpload from './components/MobileUpload'
import VerseSearch from './components/VerseSearch'
import PremiumDashboard from './components/premium/PremiumDashboard'
import SubscriptionManager from './components/premium/SubscriptionManager'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('upload')
  const [sessionData, setSessionData] = useState(null)

  const handleFileProcessed = (data) => {
    setSessionData(data)
    setActiveTab('editor')
  }

  const handleMobileProcessed = (data) => {
    setSessionData(data)
    setActiveTab('editor')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <BookOpen className="h-12 w-12 text-blue-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Bible Outline Verse Populator
            </h1>
          </div>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Upload your church outlines and automatically populate them with Bible verses from the Recovery Version. 
            Perfect for sermon preparation and Bible study materials.
          </p>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-6 mb-8">
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              Upload Document
            </TabsTrigger>
            <TabsTrigger value="mobile" className="flex items-center gap-2">
              <Smartphone className="h-4 w-4" />
              Mobile Upload
            </TabsTrigger>
            <TabsTrigger value="editor" className="flex items-center gap-2" disabled={!sessionData}>
              <FileText className="h-4 w-4" />
              Edit Outline
            </TabsTrigger>
            <TabsTrigger value="search" className="flex items-center gap-2">
              <Search className="h-4 w-4" />
              Verse Search
            </TabsTrigger>
            <TabsTrigger value="premium" className="flex items-center gap-2">
              <Star className="h-4 w-4" />
              🌟 Premium Features
            </TabsTrigger>
            <TabsTrigger value="subscription" className="flex items-center gap-2">
              <CreditCard className="h-4 w-4" />
              💎 Subscription
            </TabsTrigger>
          </TabsList>

          {/* File Upload Tab */}
          <TabsContent value="upload" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Upload PDF or Word Document
                </CardTitle>
                <CardDescription>
                  Upload your church outline in PDF or Word format. We'll extract the text and identify Bible verse references automatically.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileUpload onFileProcessed={handleFileProcessed} />
              </CardContent>
            </Card>

            {/* Features Overview */}
            <div className="grid md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Smart Detection</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Automatically detects verse references in various formats like "John 3:16", "Eph. 1:5, 9", and "1 John 4:8, 16".
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Recovery Version</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Uses the Recovery Version Bible text to populate your outlines with accurate and consistent verse content.
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Export Ready</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Export your populated outline as a Word document, ready for printing or sharing with your congregation.
                  </p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Mobile Upload Tab */}
          <TabsContent value="mobile" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Smartphone className="h-5 w-5" />
                  Mobile Photo Upload
                </CardTitle>
                <CardDescription>
                  Take a photo of your outline or upload an existing image. We'll use OCR to extract the text and process it.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <MobileUpload onFileProcessed={handleMobileProcessed} />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Outline Editor Tab */}
          <TabsContent value="editor" className="space-y-6">
            {sessionData ? (
              <OutlineEditor sessionData={sessionData} />
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 dark:text-gray-300 mb-2">
                    No Document Uploaded
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400 mb-4">
                    Please upload a document first to start editing your outline.
                  </p>
                  <Button onClick={() => setActiveTab('upload')}>
                    Upload Document
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Verse Search Tab */}
          <TabsContent value="search" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="h-5 w-5" />
                  Bible Verse Search
                </CardTitle>
                <CardDescription>
                  Search for specific Bible verses or browse the Recovery Version Bible database.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <VerseSearch />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Premium Features Tab */}
          <TabsContent value="premium" className="space-y-6">
            <PremiumDashboard />
          </TabsContent>

          {/* Subscription Tab */}
          <TabsContent value="subscription" className="space-y-6">
            <SubscriptionManager />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

