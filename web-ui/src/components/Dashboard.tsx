'use client'

import { useState, useEffect } from 'react'

interface Project {
  id: string
  name: string
  language: string
  framework: string
  status: string
  lastAnalyzed: string
}

interface Metric {
  label: string
  value: string | number
  change?: number
}

export function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([])
  const [metrics, setMetrics] = useState<Metric[]>([])

  useEffect(() => {
    // Fetch projects and metrics
    setMetrics([
      { label: 'Active Projects', value: 12, change: 5 },
      { label: 'Code Analyses', value: 1247, change: 23 },
      { label: 'Tests Generated', value: 892, change: 15 },
      { label: 'Refactoring Suggestions', value: 156, change: -3 },
    ])
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metrics.map((metric) => (
            <div
              key={metric.label}
              className="bg-white rounded-lg shadow p-6"
            >
              <div className="text-sm font-medium text-gray-500">
                {metric.label}
              </div>
              <div className="mt-2 flex items-baseline">
                <div className="text-3xl font-bold text-gray-900">
                  {metric.value}
                </div>
                {metric.change && (
                  <div
                    className={`ml-2 text-sm font-semibold ${
                      metric.change >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {metric.change >= 0 ? '+' : ''}
                    {metric.change}%
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Projects Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              Recent Projects
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Project
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Language
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Framework
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Analyzed
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {projects.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                      No projects yet. Create your first project to get started!
                    </td>
                  </tr>
                ) : (
                  projects.map((project) => (
                    <tr key={project.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {project.name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                          {project.language}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {project.framework}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          {project.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {project.lastAnalyzed}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

