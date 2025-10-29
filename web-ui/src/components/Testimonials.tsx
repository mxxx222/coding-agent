export function Testimonials() {
  return (
    <section className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">
            Elite Developers Choose Premium Quality
          </h2>
          <p className="mt-4 text-base text-gray-600 max-w-2xl mx-auto">
            Hear from top-tier developers who demand the world's highest quality AI coding tool
          </p>
        </div>

        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">JS</span>
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900">John Smith</h4>
                <p className="text-base text-gray-500">Staff Engineer at Google DeepMind</p>
              </div>
            </div>
            <p className="mt-4 text-base text-gray-600">
              "After evaluating every AI coding assistant on the market, Coding Agent is the only
              one that consistently produces code at Google DeepMind's standards. Its refactoring
              intelligence is so advanced it feels like it understands the codebase better than most
              senior engineers."
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">AS</span>
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900">Alice Johnson</h4>
                <p className="text-base text-gray-500">Principal Engineer at OpenAI</p>
              </div>
            </div>
            <p className="mt-4 text-base text-gray-600">
              "At OpenAI, we build the most advanced AI systems in the world. Coding Agent is the
              only external tool we've approved for our codebase. Its security analysis and test
              generation capabilities are so sophisticated they rival our internal tools."
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">MD</span>
                </div>
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-medium text-gray-900">Mike Davis</h4>
                <p className="text-base text-gray-500">VP Engineering at SpaceX</p>
              </div>
            </div>
            <p className="mt-4 text-base text-gray-600">
              "SpaceX's mission-critical systems demand perfection. Coding Agent Pro reduced our
              critical bugs by 65% and increased our deployment velocity by 3x. This tool doesn't
              just assist coding - it elevates entire engineering organizations to elite status."
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
