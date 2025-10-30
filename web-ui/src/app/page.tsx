import { Metadata } from 'next'
import { Hero } from '@/components/Hero'
import { Features } from '@/components/Features'
import { HowItWorks } from '@/components/HowItWorks'
import { Testimonials } from '@/components/Testimonials'
import { Pricing } from '@/components/Pricing'

export const metadata: Metadata = {
  title: 'Coding Agent - AI-Powered Development Assistant',
  description:
    'Intelligent coding assistant for development workflows. Get AI-powered refactoring, test generation, and code optimization.',
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      <main>
        <Hero />
        <section className="py-12 md:py-16">
          <div className="max-w-6xl mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <a href="/auto-deploy" className="card p-4 hover:shadow transition">
                <h3 className="font-semibold mb-1">Auto‑Deploy</h3>
                <p className="text-sm text-gray-600">Notion → Deploy pipeline with status tracking.</p>
              </a>
              <a href="/secrets" className="card p-4 hover:shadow transition">
                <h3 className="font-semibold mb-1">Secrets</h3>
                <p className="text-sm text-gray-600">Manage API keys, rotation, and testing.</p>
              </a>
              <a href="/secrets/tools" className="card p-4 hover:shadow transition">
                <h3 className="font-semibold mb-1">Export / Import</h3>
                <p className="text-sm text-gray-600">Encrypted bundles with passphrase.</p>
              </a>
            </div>
          </div>
        </section>
        <HowItWorks />
        <Features />
        <Testimonials />
        <Pricing />
        <section className="py-12 md:py-16">
          <div className="max-w-6xl mx-auto px-4 text-center">
            <h3 className="text-xl font-semibold mb-3">Get started</h3>
            <p className="text-gray-600 mb-6">Open the Secrets page, add your provider tokens, and run Auto‑Deploy.</p>
            <div className="flex items-center justify-center gap-3">
              <a href="/secrets" className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">Open Secrets</a>
              <a href="/auto-deploy" className="px-4 py-2 rounded bg-gray-100 hover:bg-gray-200">Open Auto‑Deploy</a>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
