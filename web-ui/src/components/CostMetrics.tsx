'use client'

import { useState, useEffect } from 'react'

interface CostData {
  total: number
  today: number
  thisMonth: number
  tokenUsage: number
  requests: number
}

interface DailyCost {
  date: string
  cost: number
  tokens: number
}

export function CostMetrics() {
  const [costData, setCostData] = useState<CostData>({
    total: 0,
    today: 0,
    thisMonth: 0,
    tokenUsage: 0,
    requests: 0,
  })

  const [dailyCosts, setDailyCosts] = useState<DailyCost[]>([])

  useEffect(() => {
    // Mock data
    setCostData({
      total: 245.67,
      today: 12.34,
      thisMonth: 156.78,
      tokenUsage: 12450,
      requests: 892,
    })

    setDailyCosts([
      { date: '2025-10-16', cost: 8.45, tokens: 8523 },
      { date: '2025-10-17', cost: 10.23, tokens: 10321 },
      { date: '2025-10-18', cost: 9.87, tokens: 9954 },
      { date: '2025-10-19', cost: 11.56, tokens: 11678 },
      { date: '2025-10-20', cost: 13.21, tokens: 13345 },
      { date: '2025-10-21', cost: 12.34, tokens: 12450 },
    ])
  }, [])

  const avgDailyCost = dailyCosts.length > 0
    ? (dailyCosts.reduce((sum, d) => sum + d.cost, 0) / dailyCosts.length).toFixed(2)
    : '0.00'

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">Cost Analytics</h2>
        <p className="mt-1 text-sm text-gray-500">
          Track your AI usage and costs
        </p>
      </div>

      <div className="p-6">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              ${costData.today}
            </div>
            <div className="text-sm text-gray-500 mt-1">Spent Today</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              ${costData.thisMonth}
            </div>
            <div className="text-sm text-gray-500 mt-1">This Month</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900">
              ${costData.total}
            </div>
            <div className="text-sm text-gray-500 mt-1">Total</div>
          </div>
        </div>

        {/* Token Usage */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Token Usage</span>
            <span className="text-sm text-gray-500">
              {costData.tokenUsage.toLocaleString()} tokens
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: `${Math.min((costData.tokenUsage / 50000) * 100, 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0</span>
            <span>50K limit</span>
          </div>
        </div>

        {/* Requests */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">API Requests</span>
            <span className="text-sm text-gray-500">
              {costData.requests.toLocaleString()} requests
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full"
              style={{ width: `${Math.min((costData.requests / 1000) * 100, 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0</span>
            <span>1K limit</span>
          </div>
        </div>

        {/* Daily Costs */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">
            Daily Costs (Last 7 Days)
          </h3>
          <div className="space-y-2">
            {dailyCosts.map((day, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">
                  {new Date(day.date).toLocaleDateString('en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                  })}
                </span>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-500">
                    {day.tokens.toLocaleString()} tokens
                  </span>
                  <span className="text-sm font-semibold text-gray-900">
                    ${day.cost.toFixed(2)}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Average Daily</span>
              <span className="font-semibold text-gray-900">
                ${avgDailyCost}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

