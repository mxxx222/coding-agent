import { Metadata } from 'next'
import { Hero } from '@/components/Hero'
import { Features } from '@/components/Features'
import { HowItWorks } from '@/components/HowItWorks'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'

export const metadata: Metadata = {
  title: 'Coding Agent - AI-Powered Development Assistant',
  description:
    'Intelligent coding assistant for development workflows. Get AI-powered refactoring, test generation, and code optimization.',
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <Hero />
        <HowItWorks />
        <Features />
      </main>
      <Footer />
    </div>
  )
}
