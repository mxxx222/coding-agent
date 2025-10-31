export function Pricing() {
  return (
    <section className="py-20 bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center animate-fade-in">
          <h2 className="text-4xl font-bold text-white sm:text-5xl animate-slide-up">
            Simple Pricing
          </h2>
          <p className="mt-6 text-xl text-gray-400 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            Choose the plan that works for you
          </p>
        </div>
        
        <div className="mt-20 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div className="bg-gray-900/50 backdrop-blur-sm border border-white/10 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 hover:border-white/20 animate-fade-in">
            <div className="text-center">
              <h3 className="text-xl font-semibold text-white">Free</h3>
              <p className="mt-6 text-5xl font-bold text-blue-400">$0</p>
              <p className="mt-4 text-base text-gray-400">
                Basic features and local analysis
              </p>
            </div>
            <ul className="mt-8 space-y-4">
              <li className="flex items-center">
                <div className="flex-shrink-0 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
                <span className="ml-3 text-base text-gray-300">CLI Tool</span>
              </li>
              <li className="flex items-center">
                <div className="flex-shrink-0 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
                <span className="ml-3 text-base text-gray-300">Local Analysis</span>
              </li>
              <li className="flex items-center">
                <div className="flex-shrink-0 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
                <span className="ml-3 text-base text-gray-300">Basic Refactoring</span>
              </li>
            </ul>
          </div>
          
          <div className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 border-2 border-blue-500/50 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 animate-fade-in relative overflow-hidden" style={{ animationDelay: '0.1s' }}>
            <div className="absolute top-0 right-0 bg-blue-500 text-white px-3 py-1 text-xs font-semibold rounded-bl-lg">
              Most Popular
            </div>
            <div className="text-center">
              <h3 className="text-xl font-semibold text-white">Pro</h3>
              <p className="mt-6 text-5xl font-bold text-blue-400">$29<span className="text-lg text-gray-400">/mo</span></p>
              <p className="mt-4 text-base text-gray-300">
                Full AI features with your API key
              </p>
            </div>
            <ul className="mt-8 space-y-4">
              <li className="flex items-center">
                <div className="flex-shrink-0 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
                <span className="ml-3 text-base text-gray-300">Everything in Free</span>
              </li>
              <li className="flex items-center">
                <div className="flex-shrink-0 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
                <span className="ml-3 text-base text-gray-300">AI-Powered Analysis</span>
              </li>
              <li className="flex items-center">
                <div className="flex-shrink-0 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
                <span className="ml-3 text-base text-gray-300">Test Generation</span>
              </li>
              <li className="flex items-center">
                <div className="flex-shrink-0 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
                <span className="ml-3 text-base text-gray-300">VSCode Extension</span>
              </li>
            </ul>
          </div>
          
          <div className="bg-gray-900/50 backdrop-blur-sm border border-white/10 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 hover:border-white/20 animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <div className="text-center">
              <h3 className="text-xl font-semibold text-white">Enterprise</h3>
              <p className="mt-6 text-5xl font-bold text-blue-400">Custom</p>
              <p className="mt-4 text-base text-gray-400">
                Tailored for large teams
              </p>
            </div>
            <ul className="mt-8 space-y-4">
              <li className="flex items-center">
                <div className="flex-shrink-0 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
                <span className="ml-3 text-base text-gray-300">Everything in Pro</span>
              </li>
              <li className="flex items-center">
                <div className="flex-shrink-0 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
                <span className="ml-3 text-base text-gray-300">Team Management</span>
              </li>
              <li className="flex items-center">
                <div className="flex-shrink-0 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
                <span className="ml-3 text-base text-gray-300">Custom Integrations</span>
              </li>
              <li className="flex items-center">
                <div className="flex-shrink-0 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
                <span className="ml-3 text-base text-gray-300">Priority Support</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
