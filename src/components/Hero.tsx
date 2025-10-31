import Link from 'next/link'
import { Button } from './ui/Button'
import { ArrowRightIcon, SparklesIcon, CodeBracketIcon } from '@heroicons/react/24/outline'

export function Hero() {
  return (
    <div className="relative min-h-screen bg-black text-white flex items-center justify-center overflow-hidden">
      {/* Subtle gradient background */}
      <div className="absolute inset-0 bg-gradient-to-b from-gray-950 via-black to-black" />
      
      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
      
      {/* Floating accent circles */}
      <div className="absolute top-20 left-20 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      
      <div className="relative z-10 max-w-7xl mx-auto px-6 py-32">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left side - Text content */}
          <div className="text-center lg:text-left">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 mb-8 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm">
              <SparklesIcon className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-gray-300">AI-Powered Development</span>
            </div>

            {/* Main heading */}
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-gray-400">
              Build with AI
              <br />
              Code Smarter
            </h1>

            {/* Description */}
            <p className="text-xl text-gray-400 mb-12 max-w-2xl">
              Intelligent coding assistant that helps you refactor, test, and optimize your code with AI-powered suggestions.
            </p>

            {/* CTA buttons */}
            <div className="flex items-center justify-center lg:justify-start gap-4">
              <Button size="lg" className="bg-white text-black hover:bg-gray-100">
                Get Started
                <ArrowRightIcon className="ml-2 h-5 w-5" />
              </Button>
              <Button size="lg" variant="outline" className="border-white/20 bg-white/5 hover:bg-white/10">
                <Link href="http://localhost:8000/api/docs" target="_blank" rel="noopener noreferrer">
                  View API Docs
                </Link>
              </Button>
            </div>
          </div>

          {/* Right side - Code preview */}
          <div className="relative">
            <div className="bg-gray-900/90 backdrop-blur-sm border border-white/10 rounded-lg p-6 shadow-2xl">
              {/* Code editor header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <CodeBracketIcon className="w-4 h-4" />
                  <span>AI Assistant</span>
                </div>
              </div>

              {/* Code content */}
              <div className="space-y-3 font-mono text-sm">
                <div className="text-blue-400">// Before: Basic function</div>
                <div className="text-gray-300">function calculateTotal(items) {'{'}</div>
                <div className="text-gray-300 pl-4">let total = 0;</div>
                <div className="text-gray-300 pl-4">for (let item of items) {'{'}</div>
                <div className="text-gray-300 pl-8">total += item.price;</div>
                <div className="text-gray-300 pl-4">{'}'}</div>
                <div className="text-gray-300 pl-4">return total;</div>
                <div className="text-gray-300">{'}'}</div>

                <div className="text-green-400 pt-2">// After: AI-optimized</div>
                <div className="text-gray-300">function calculateTotal(items) {'{'}</div>
                <div className="text-gray-300 pl-4">{'return items.reduce((total, item) => total + item.price, 0);'}</div>
                <div className="text-gray-300">{'}'}</div>

                <div className="text-purple-400 pt-2">// AI Suggestion: 83% more efficient</div>
              </div>

              {/* AI typing indicator */}
              <div className="mt-4 flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span className="text-xs text-gray-400">AI analyzing code...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
