export function Pricing() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
            Premium Pricing for Elite Developers
          </h2>
          <p className="mt-4 text-base text-gray-600 max-w-2xl mx-auto">
            Unlock the world's highest quality AI coding tool with our premium Pro plan
          </p>
        </div>

        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div className="bg-white border border-gray-200 rounded-lg p-8">
            <h3 className="text-lg font-medium text-gray-900">Free</h3>
            <p className="mt-4 text-3xl font-bold text-gray-900">$0</p>
            <p className="mt-4 text-base text-gray-500">
              Try basic features - upgrade to Pro for premium quality
            </p>
            <ul className="mt-6 space-y-4">
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">CLI Tool</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Local Analysis</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Basic Refactoring</span>
              </li>
            </ul>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-lg p-8 relative">
            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
              <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                ELITE ACCESS
              </span>
            </div>
            <h3 className="text-lg font-medium text-gray-900">Pro (Exclusive)</h3>
            <p className="mt-4 text-3xl font-bold text-gray-900">$29/mo</p>
            <p className="mt-4 text-base text-gray-500">
              Invitation-only access to the world's most exclusive AI coding tool. Reserved for
              engineering excellence.
            </p>
            <ul className="mt-6 space-y-4">
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Everything in Free</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Industry-Leading AI Analysis</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Enterprise Test Generation</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Premium VSCode Extension</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Advanced Security Analysis</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Real-time Premium Intelligence</span>
              </li>
            </ul>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-8">
            <h3 className="text-lg font-medium text-gray-900">Enterprise</h3>
            <p className="mt-4 text-3xl font-bold text-gray-900">Custom</p>
            <p className="mt-4 text-base text-gray-500">
              Maximum premium features for enterprise teams
            </p>
            <ul className="mt-6 space-y-4">
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Everything in Pro</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Advanced Team Management</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Custom Enterprise Integrations</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">24/7 Premium Support</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Dedicated Account Manager</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  )
}
