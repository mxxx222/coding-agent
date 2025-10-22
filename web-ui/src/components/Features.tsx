import { 
  CodeBracketIcon, 
  CpuChipIcon, 
  SparklesIcon, 
  ShieldCheckIcon,
  BoltIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

const features = [
  {
    name: 'AI-Powered Refactoring',
    description: 'Get intelligent suggestions to improve code quality, performance, and maintainability with advanced AI analysis.',
    icon: CodeBracketIcon,
  },
  {
    name: 'Automated Test Generation',
    description: 'Generate comprehensive test suites automatically, covering unit tests, integration tests, and edge cases.',
    icon: CpuChipIcon,
  },
  {
    name: 'Smart Code Optimization',
    description: 'Optimize your code for performance, readability, and best practices with AI-driven recommendations.',
    icon: SparklesIcon,
  },
  {
    name: 'Security Analysis',
    description: 'Identify potential security vulnerabilities and get suggestions for secure coding practices.',
    icon: ShieldCheckIcon,
  },
  {
    name: 'Real-time Suggestions',
    description: 'Get instant feedback and suggestions as you code, integrated directly into your development environment.',
    icon: BoltIcon,
  },
  {
    name: 'Analytics & Insights',
    description: 'Track code quality metrics, performance improvements, and development productivity over time.',
    icon: ChartBarIcon,
  },
]

export function Features() {
  return (
    <div id="features" className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-primary-600">Everything you need</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Powerful AI features for modern development
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Our AI-powered platform provides everything you need to write better code, faster. 
            From intelligent refactoring to automated testing, we've got you covered.
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
            {features.map((feature) => (
              <div key={feature.name} className="flex flex-col">
                <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                  <feature.icon className="h-5 w-5 flex-none text-primary-600" aria-hidden="true" />
                  {feature.name}
                </dt>
                <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">{feature.description}</p>
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </div>
  )
}
