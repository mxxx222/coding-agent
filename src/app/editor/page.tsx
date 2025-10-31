import { Metadata } from 'next'
import { CodeEditor } from '@/components/CodeEditor'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'

export const metadata: Metadata = {
  title: 'Code Editor - Coding Agent',
  description: 'Interactive code editor powered by AI for development workflows.',
}

export default function EditorPage() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        <div id="code-editor">
          <CodeEditor />
        </div>
      </main>
      <Footer />
    </div>
  )
}