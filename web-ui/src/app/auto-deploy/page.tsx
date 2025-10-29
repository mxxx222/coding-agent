'use client'

import { useState } from 'react'
import { NotionSelector } from '@/components/NotionSelector'
import { AutomationPipeline } from '@/components/AutomationPipeline'
import { Header } from '@/components/Header'

export default function AutoDeployPage() {
  const [selectedPageId, setSelectedPageId] = useState<string | null>(null)

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Automated Deployment
          </h1>
          <p className="text-xl text-gray-600">
            Select a Notion idea and let AI generate, test, and deploy it automatically.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Notion Selector */}
          <div>
            <NotionSelector onSelect={(pageId) => setSelectedPageId(pageId)} />
          </div>

          {/* Pipeline */}
          <div>
            {selectedPageId ? (
              <AutomationPipeline notionPageId={selectedPageId} />
            ) : (
              <div className="bg-white rounded-lg shadow-lg p-6 text-center">
                <p className="text-gray-600">
                  Select a Notion idea to start the automation pipeline.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

