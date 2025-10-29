'use client'

import { useState, useEffect } from 'react'
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'

interface NotionPage {
  id: string
  data: {
    title: string
    description?: string
    status?: string
    priority?: string
    tech_stack?: string[]
  }
}

export function NotionSelector({ onSelect }: { onSelect: (pageId: string) => void }) {
  const [pages, setPages] = useState<NotionPage[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadPages()
  }, [])

  async function loadPages() {
    setLoading(true)
    try {
      const response = await fetch('/api/notion/query-database', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          database_id: process.env.NEXT_PUBLIC_NOTION_DATABASE_ID || '',
          filters: null
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setPages(data.pages || [])
      }
    } catch (error) {
      console.error('Error loading Notion pages:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredPages = pages.filter(page =>
    page.data.title?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        Select a Notion Idea
      </h2>
      
      {/* Search */}
      <div className="relative mb-6">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search ideas..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Pages List */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading ideas...</p>
        </div>
      ) : filteredPages.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-600">No ideas found.</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredPages.map((page) => (
            <div
              key={page.id}
              onClick={() => onSelect(page.id)}
              className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md cursor-pointer transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {page.data.title || 'Untitled'}
                  </h3>
                  {page.data.description && (
                    <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                      {page.data.description}
                    </p>
                  )}
                  <div className="mt-2 flex items-center gap-3">
                    {page.data.status && (
                      <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                        {page.data.status}
                      </span>
                    )}
                    {page.data.priority && (
                      <span className="px-2 py-1 text-xs font-medium bg-orange-100 text-orange-800 rounded">
                        {page.data.priority}
                      </span>
                    )}
                  </div>
                  {page.data.tech_stack && page.data.tech_stack.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {page.data.tech_stack.map((tech) => (
                        <span
                          key={tech}
                          className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

