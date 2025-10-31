export function HowItWorks() {
  return (
    <section className="py-16 bg-gray-900/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white sm:text-4xl">
            How It Works
          </h2>
          <p className="mt-4 text-lg text-gray-400">
            Get started with Coding Agent in three simple steps
          </p>
        </div>

        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div className="text-center bg-gray-800/50 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-gray-700/50 transition-all duration-300">
            <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white mx-auto">
              <span className="text-xl font-bold">1</span>
            </div>
            <h3 className="mt-4 text-lg font-medium text-white">Install</h3>
            <p className="mt-2 text-base text-gray-300">
              Install the CLI tool or VSCode extension
            </p>
          </div>

          <div className="text-center bg-gray-800/50 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-gray-700/50 transition-all duration-300">
            <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white mx-auto">
              <span className="text-xl font-bold">2</span>
            </div>
            <h3 className="mt-4 text-lg font-medium text-white">Configure</h3>
            <p className="mt-2 text-base text-gray-300">
              Set up your OpenAI API key and preferences
            </p>
          </div>

          <div className="text-center bg-gray-800/50 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-gray-700/50 transition-all duration-300">
            <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white mx-auto">
              <span className="text-xl font-bold">3</span>
            </div>
            <h3 className="mt-4 text-lg font-medium text-white">Code</h3>
            <p className="mt-2 text-base text-gray-300">
              Start coding with AI-powered assistance
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
