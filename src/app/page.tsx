import { redirect } from 'next/navigation'

export const metadata = {
  title: 'Coding Agent - AI-Powered Development Assistant',
  description: 'Intelligent coding assistant for development workflows. Get AI-powered refactoring, test generation, and code optimization.',
}

export default function HomePage() {
  redirect('/dashboard')
}
