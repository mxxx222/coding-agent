'use client'

import { useState } from 'react'
import { CheckIcon } from '@heroicons/react/24/outline'

interface Step {
  id: string
  title: string
  description: string
  completed: boolean
}

interface Recipe {
  id: string
  name: string
  description: string
  steps: Step[]
}

export function GuidedPath() {
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null)

  const recipes: Recipe[] = [
    {
      id: 'nextjs-supabase-stripe',
      name: 'Next.js + Supabase + Stripe',
      description: 'Build a full-stack SaaS application with authentication and payments',
      steps: [
        { id: '1', title: 'Initialize Next.js Project', description: 'Set up Next.js with TypeScript and Tailwind CSS', completed: false },
        { id: '2', title: 'Configure Supabase', description: 'Set up authentication and database', completed: false },
        { id: '3', title: 'Add Stripe Integration', description: 'Configure payment processing and webhooks', completed: false },
        { id: '4', title: 'Implement Auth Flow', description: 'Add sign up, sign in, and protected routes', completed: false },
        { id: '5', title: 'Create Dashboard', description: 'Build user dashboard and subscription management', completed: false },
        { id: '6', title: 'Deploy to Production', description: 'Deploy to Vercel and configure environment variables', completed: false },
      ],
    },
    {
      id: 'fastapi-prefect-ml',
      name: 'FastAPI + Prefect + ML Pipeline',
      description: 'Build a machine learning API with workflow orchestration',
      steps: [
        { id: '1', title: 'Setup FastAPI Server', description: 'Create FastAPI project with database models', completed: false },
        { id: '2', title: 'Configure Prefect', description: 'Set up Prefect for workflow orchestration', completed: false },
        { id: '3', title: 'Implement ML Pipeline', description: 'Create data processing and model training flows', completed: false },
        { id: '4', title: 'Add Vector Store', description: 'Set up pgvector for embeddings storage', completed: false },
        { id: '5', title: 'Create API Endpoints', description: 'Implement prediction and inference endpoints', completed: false },
        { id: '6', title: 'Deploy with Docker', description: 'Containerize and deploy to production', completed: false },
      ],
    },
  ]

  if (!selectedRecipe) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Build With Me
            </h1>
            <p className="text-xl text-gray-600">
              Choose a guided path to build your project step-by-step
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {recipes.map((recipe) => (
              <div
                key={recipe.id}
                className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer"
                onClick={() => setSelectedRecipe(recipe)}
              >
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {recipe.name}
                </h3>
                <p className="text-gray-600 mb-4">{recipe.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">
                    {recipe.steps.length} steps
                  </span>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    Start Building →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <button
            onClick={() => setSelectedRecipe(null)}
            className="text-blue-600 hover:text-blue-700 mb-4"
          >
            ← Back to Recipes
          </button>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {selectedRecipe.name}
          </h1>
          <p className="text-gray-600">{selectedRecipe.description}</p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="space-y-6">
            {selectedRecipe.steps.map((step, index) => (
              <div
                key={step.id}
                className={`flex gap-4 p-4 rounded-lg ${
                  step.completed ? 'bg-green-50' : 'bg-gray-50'
                }`}
              >
                <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                  step.completed
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}>
                  {step.completed ? (
                    <CheckIcon className="w-6 h-6" />
                  ) : (
                    <span className="font-bold">{index + 1}</span>
                  )}
                </div>
                <div className="flex-1">
                  <h3 className={`font-semibold ${
                    step.completed ? 'text-green-900' : 'text-gray-900'
                  }`}>
                    {step.title}
                  </h3>
                  <p className={`text-sm mt-1 ${
                    step.completed ? 'text-green-700' : 'text-gray-600'
                  }`}>
                    {step.description}
                  </p>
                </div>
                {!step.completed && (
                  <button
                    onClick={() => {
                      const updatedRecipe = {
                        ...selectedRecipe,
                        steps: selectedRecipe.steps.map((s) =>
                          s.id === step.id ? { ...s, completed: true } : s
                        ),
                      }
                      setSelectedRecipe(updatedRecipe)
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    Complete
                  </button>
                )}
              </div>
            ))}
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">
                Progress: {selectedRecipe.steps.filter(s => s.completed).length} / {selectedRecipe.steps.length} steps completed
              </span>
              <div className="w-48 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{
                    width: `${(selectedRecipe.steps.filter(s => s.completed).length / selectedRecipe.steps.length) * 100}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

