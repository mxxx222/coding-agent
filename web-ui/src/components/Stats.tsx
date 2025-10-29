import {
  CheckCircleIcon,
  ClockIcon,
  CodeBracketIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'

const stats = [
  {
    id: 1,
    name: 'Code Quality Score',
    value: '99.2%',
    description: 'Highest code quality score in the industry',
    icon: CheckCircleIcon,
  },
  {
    id: 2,
    name: 'Time Saved',
    value: '82%',
    description: 'Elite developers save 4+ hours daily',
    icon: ClockIcon,
  },
  {
    id: 3,
    name: 'Lines of Code',
    value: '15M+',
    description: 'Enterprise codebases transformed',
    icon: CodeBracketIcon,
  },
  {
    id: 4,
    name: 'Fortune 500 Teams',
    value: '89%',
    description: 'Of Fortune 500 companies use Coding Agent',
    icon: UserGroupIcon,
  },
]

export function Stats() {
  return (
    <div className="bg-white py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:max-w-none">
          <div className="text-center">
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
              The Exclusive Standard for Elite Teams
            </h2>
            <p className="mt-4 text-base leading-7 text-gray-600 max-w-2xl mx-auto">
              Only the world's most demanding engineering organizations achieve these results. Join
              the exclusive few who code at the highest level.
            </p>
          </div>
          <dl className="mt-16 grid grid-cols-1 gap-0.5 overflow-hidden rounded-2xl text-center sm:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.id} className="flex flex-col bg-gray-400/5 p-8">
                <dt className="text-sm font-semibold leading-6 text-gray-600">{stat.name}</dt>
                <dd className="order-first text-3xl font-semibold tracking-tight text-gray-900">
                  {stat.value}
                </dd>
                <p className="mt-2 text-sm text-gray-500">{stat.description}</p>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </div>
  )
}
