import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Coding Agent - AI-Powered Development Assistant',
  description: 'Intelligent coding assistant for development workflows',
  keywords: ['AI', 'coding', 'development', 'assistant', 'refactoring', 'testing'],
  authors: [{ name: 'Coding Agent Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
  openGraph: {
    title: 'Coding Agent - AI-Powered Development Assistant',
    description: 'Intelligent coding assistant for development workflows',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Coding Agent - AI-Powered Development Assistant',
    description: 'Intelligent coding assistant for development workflows',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-gray-50`}>
        <Providers>
          <header className="bg-white border-b">
            <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
              <a href="/" className="font-semibold">Coding Agent</a>
              <nav className="flex items-center gap-4 text-sm">
                <a className="hover:underline" href="/auto-deploy">Auto‑Deploy</a>
                <a className="hover:underline" href="/secrets">Secrets</a>
                <a className="hover:underline" href="/secrets/providers">Providers</a>
                <a className="hover:underline" href="/secrets/tools">Tools</a>
              </nav>
            </div>
          </header>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </Providers>
      </body>
    </html>
  )
}
