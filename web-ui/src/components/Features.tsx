import {
  CodeBracketIcon,
  CpuChipIcon,
  SparklesIcon,
  ShieldCheckIcon,
  BoltIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'

const features = [
  {
    name: 'Industry-Leading AI Refactoring',
    description:
      'Experience the most advanced code refactoring AI available. Our proprietary algorithms deliver enterprise-grade code improvements with unmatched accuracy and depth.',
    icon: CodeBracketIcon,
  },
  {
    name: 'Comprehensive Test Generation',
    description:
      'Generate production-ready test suites that exceed industry standards. Coverage includes unit, integration, edge cases, and performance benchmarks.',
    icon: CpuChipIcon,
  },
  {
    name: 'Elite Code Optimization',
    description:
      'Achieve peak performance with our state-of-the-art optimization engine. Reduce complexity, eliminate bottlenecks, and maximize efficiency.',
    icon: SparklesIcon,
  },
  {
    name: 'Advanced Security Analysis',
    description:
      'Military-grade security scanning identifies vulnerabilities before deployment. Stay ahead of threats with proactive security recommendations.',
    icon: ShieldCheckIcon,
  },
  {
    name: 'Real-time Premium Intelligence',
    description:
      'Get instant, context-aware suggestions from the most sophisticated AI coding assistant. Every recommendation is backed by deep analysis.',
    icon: BoltIcon,
  },
  {
    name: 'Enterprise Analytics & Insights',
    description:
      'Monitor code quality metrics, track performance improvements, and measure productivity gains with comprehensive analytics dashboard.',
    icon: ChartBarIcon,
  },
]

export function Features() {
  return (
    <div id="features" className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-sm font-semibold leading-6 text-primary-600">The Gold Standard</h2>
          <p className="mt-2 text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
            Premium AI Features Setting the Industry Standard
          </p>
          <p className="mt-6 text-base leading-7 text-gray-600 max-w-3xl mx-auto">
            The most exclusive AI coding intelligence ever developed. Our proprietary algorithms
            surpass all competitors, delivering perfection that only the world's most elite
            engineering organizations can achieve.
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
            {features.map(feature => (
              <div key={feature.name} className="flex flex-col">
                <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
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
