'use client'

import { useState } from 'react'
import { Button } from './ui/Button'

interface CodeEditorProps {
  onAnalyze?: (code: string, language: string) => void
  onRefactor?: (code: string, language: string) => void
  onGenerateTests?: (code: string, language: string) => void
}

const exampleCode = `def calculate_total(items):
    total = 0
    for item in items:
        if item.price > 0:
            total += item.price * item.quantity
    return total`

export function CodeEditor({ onAnalyze, onRefactor, onGenerateTests }: CodeEditorProps) {
  const [code, setCode] = useState(exampleCode)
  const [language, setLanguage] = useState('python')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleAction = async (action: 'analyze' | 'refactor' | 'tests') => {
    setLoading(true)
    setResult(null)

    try {
      const endpoint = action === 'analyze' 
        ? '/api/analyze/code'
        : action === 'refactor'
        ? '/api/analyze/refactor'
        : '/api/generate/test'

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          language,
          ...(action === 'refactor' && { file_path: 'example.py' }),
        }),
      })

      const data = await response.json()
      setResult(data)
    } catch (error) {
      setResult({ error: 'Failed to connect to API. Make sure the server is running.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="py-12 bg-gray-50">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Try Coding Agent Now</h2>
            <p className="mt-2 text-lg text-gray-600">
              Paste your code below and see how AI can help improve it
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Language selector */}
            <div className="px-4 py-3 bg-gray-100 border-b border-gray-200">
              <label className="text-sm font-medium text-gray-700 mr-3">Language:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-md text-sm"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="java">Java</option>
                <option value="go">Go</option>
              </select>
            </div>

            {/* Code editor */}
            <div className="p-4">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full h-64 font-mono text-sm border border-gray-300 rounded-md p-4 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Paste your code here..."
                spellCheck={false}
              />
            </div>

            {/* Action buttons */}
            <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex flex-wrap gap-2">
              <Button
                onClick={() => handleAction('analyze')}
                disabled={loading || !code.trim()}
                size="sm"
              >
                {loading ? 'Analyzing...' : '📊 Analyze Code'}
              </Button>
              <Button
                onClick={() => handleAction('refactor')}
                disabled={loading || !code.trim()}
                size="sm"
                variant="outline"
              >
                {loading ? 'Refactoring...' : '🔧 Suggest Refactor'}
              </Button>
              <Button
                onClick={() => handleAction('tests')}
                disabled={loading || !code.trim()}
                size="sm"
                variant="outline"
              >
                {loading ? 'Generating...' : '🧪 Generate Tests'}
              </Button>
            </div>

            {/* Results */}
            {result && (
              <div className="px-4 py-4 bg-gray-50 border-t border-gray-200">
                {result.error ? (
                  <div className="bg-red-50 border border-red-200 rounded-md p-4">
                    <p className="text-sm text-red-800">{result.error}</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <h3 className="text-sm font-semibold text-gray-900">Results:</h3>
                    <div className="bg-white border border-gray-200 rounded-md p-4">
                      <pre className="text-xs text-gray-700 whitespace-pre-wrap overflow-x-auto">
                        {JSON.stringify(result, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="mt-6 text-center text-sm text-gray-500">
            <p>💡 Make sure the API server is running at <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:8000</code></p>
          </div>
        </div>
      </div>
    </div>
  )
}

