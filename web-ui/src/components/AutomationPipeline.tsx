'use client'

import { useState } from 'react'
import { CheckIcon, XMarkIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

interface PipelineStep {
  id: string
  name: string
  status: 'pending' | 'running' | 'success' | 'error'
  message?: string
}

export function AutomationPipeline({ notionPageId }: { notionPageId: string }) {
  const [steps, setSteps] = useState<PipelineStep[]>([
    { id: '1', name: 'Fetch Notion Idea', status: 'pending' },
    { id: '2', name: 'Generate Plan', status: 'pending' },
    { id: '3', name: 'Generate Code', status: 'pending' },
    { id: '4', name: 'Run Tests', status: 'pending' },
    { id: '5', name: 'Create PR', status: 'pending' },
    { id: '6', name: 'Deploy to Vercel', status: 'pending' }
  ])
  const [isRunning, setIsRunning] = useState(false)
  const [result, setResult] = useState<{ url?: string; error?: string } | null>(null)

  async function startPipeline() {
    setIsRunning(true)
    setResult(null)

    try {
      // Start automation job
      const response = await fetch('/api/automation/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          notion_page_id: notionPageId
        })
      })

      const data = await response.json()
      const jobId = data.job_id

      // Poll for job status
      const pollInterval = setInterval(async () => {
        const statusResponse = await fetch(`/api/automation/job/${jobId}`)
        const status = await statusResponse.json()

        // Update steps based on job progress
        if (status.steps && status.steps.length > 0) {
          const updatedSteps = steps.map((step, index) => {
            if (index < status.steps.length) {
              const jobStep = status.steps[index]
              return {
                ...step,
                status: jobStep.success ? 'success' : 'error',
                message: jobStep.error
              }
            }
            return step
          })
          setSteps(updatedSteps)
        }

        // Check if job is complete
        if (status.status === 'success' || status.status === 'failed') {
          clearInterval(pollInterval)
          setIsRunning(false)
          
          if (status.status === 'success' && status.result?.deployment_url) {
            setResult({ url: status.result.deployment_url })
          } else {
            setResult({ error: status.error || 'Pipeline failed' })
          }
        }
      }, 2000)

    } catch (error) {
      setIsRunning(false)
      setResult({ error: 'Failed to start pipeline' })
    }
  }

  function getStatusIcon(status: string) {
    switch (status) {
      case 'success':
        return <CheckIcon className="w-6 h-6 text-green-600" />
      case 'error':
        return <XMarkIcon className="w-6 h-6 text-red-600" />
      case 'running':
        return <ArrowPathIcon className="w-6 h-6 text-blue-600 animate-spin" />
      default:
        return <div className="w-6 h-6 border-2 border-gray-300 rounded-full" />
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Automation Pipeline
        </h2>
        <button
          onClick={startPipeline}
          disabled={isRunning}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <ArrowPathIcon className="w-5 h-5" />
          {isRunning ? 'Running...' : 'Start Pipeline'}
        </button>
      </div>

      {/* Pipeline Steps */}
      <div className="space-y-4">
        {steps.map((step, index) => (
          <div
            key={step.id}
            className="flex items-center gap-4 p-4 border border-gray-200 rounded-lg"
          >
            <div className="flex-shrink-0">
              {getStatusIcon(step.status)}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">
                  {step.name}
                </h3>
                <span className={`px-3 py-1 text-sm font-medium rounded ${
                  step.status === 'success' ? 'bg-green-100 text-green-800' :
                  step.status === 'error' ? 'bg-red-100 text-red-800' :
                  step.status === 'running' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {step.status.charAt(0).toUpperCase() + step.status.slice(1)}
                </span>
              </div>
              {step.message && (
                <p className="mt-1 text-sm text-red-600">{step.message}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Result */}
      {result && (
        <div className={`mt-6 p-4 rounded-lg ${
          result.url ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
        }`}>
          {result.url ? (
            <div>
              <h3 className="font-semibold text-green-900 mb-2">
                ✅ Deployment Successful!
              </h3>
              <p className="text-green-800 mb-3">
                Your app has been deployed to Vercel.
              </p>
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Open App →
              </a>
            </div>
          ) : (
            <div>
              <h3 className="font-semibold text-red-900 mb-2">
                ❌ Deployment Failed
              </h3>
              <p className="text-red-800">
                {result.error}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

