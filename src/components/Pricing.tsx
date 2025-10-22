export function Pricing() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
            Simple Pricing
          </h2>
          <p className="mt-4 text-lg text-gray-600">
            Choose the plan that works for you
          </p>
        </div>
        
        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div className="bg-white border border-gray-200 rounded-lg p-8">
            <h3 className="text-lg font-medium text-gray-900">Free</h3>
            <p className="mt-4 text-3xl font-bold text-gray-900">$0</p>
            <p className="mt-4 text-base text-gray-500">
              Basic features and local analysis
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
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-8">
            <h3 className="text-lg font-medium text-gray-900">Pro</h3>
            <p className="mt-4 text-3xl font-bold text-gray-900">$29/mo</p>
            <p className="mt-4 text-base text-gray-500">
              Full AI features with your API key
            </p>
            <ul className="mt-6 space-y-4">
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Everything in Free</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">AI-Powered Analysis</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Test Generation</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">VSCode Extension</span>
              </li>
            </ul>
          </div>
          
          <div className="bg-white border border-gray-200 rounded-lg p-8">
            <h3 className="text-lg font-medium text-gray-900">Enterprise</h3>
            <p className="mt-4 text-3xl font-bold text-gray-900">Custom</p>
            <p className="mt-4 text-base text-gray-500">
              Tailored for large teams
            </p>
            <ul className="mt-6 space-y-4">
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Everything in Pro</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Team Management</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Custom Integrations</span>
              </li>
              <li className="flex items-center">
                <span className="text-green-500">✓</span>
                <span className="ml-3 text-base text-gray-500">Priority Support</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
