import { Metadata } from 'next'
import { Pricing } from '@/components/Pricing'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'

export const metadata: Metadata = {
  title: 'Pricing - Coding Agent',
  description: 'Choose the right plan for your development needs with our AI-powered coding assistant.',
}

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <Pricing />
      </main>
      <Footer />
    </div>
  )
}