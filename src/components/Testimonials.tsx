export function Testimonials() {
  return (
    <section className="py-16 bg-gray-900/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white sm:text-4xl">
            What Developers Say
          </h2>
          <p className="mt-4 text-lg text-gray-400">
            Join thousands of developers using Coding Agent
          </p>
        </div>

        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div className="bg-gray-800/50 backdrop-blur-sm border border-white/10 rounded-lg p-6 shadow-sm hover:bg-gray-700/50 transition-all duration-300">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center">
                  <span className="text-white font-bold">JS</span>
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-white">John Smith</h4>
                <p className="text-base text-gray-400">Senior Developer</p>
              </div>
            </div>
            <p className="mt-4 text-base text-gray-300">
              "Coding Agent has revolutionized my development workflow. The AI-powered refactoring suggestions are incredibly accurate."
            </p>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm border border-white/10 rounded-lg p-6 shadow-sm hover:bg-gray-700/50 transition-all duration-300">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-green-500 flex items-center justify-center">
                  <span className="text-white font-bold">AS</span>
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-white">Alice Johnson</h4>
                <p className="text-base text-gray-400">Full Stack Developer</p>
              </div>
            </div>
            <p className="mt-4 text-base text-gray-300">
              "The test generation feature is a game-changer. It saves me hours of work every week."
            </p>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm border border-white/10 rounded-lg p-6 shadow-sm hover:bg-gray-700/50 transition-all duration-300">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-purple-500 flex items-center justify-center">
                  <span className="text-white font-bold">MD</span>
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-white">Mike Davis</h4>
                <p className="text-base text-gray-400">Tech Lead</p>
              </div>
            </div>
            <p className="mt-4 text-base text-gray-300">
              "Our team's code quality has improved significantly since we started using Coding Agent."
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
