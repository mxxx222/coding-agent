import { Metadata } from 'next'
import { Testimonials } from '@/components/Testimonials'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'

export const metadata: Metadata = {
  title: 'About - Coding Agent',
  description: 'Learn more about our AI-powered coding assistant and hear from our users.',
}

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <Testimonials />
      </main>
      <Footer />
    </div>
  )
}