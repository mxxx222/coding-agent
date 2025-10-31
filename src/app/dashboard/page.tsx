'use client'

import { Metadata } from 'next'
import { useState } from 'react'

export default function DashboardPage() {
  const [activeProject, setActiveProject] = useState('Current Project')
  const [activeFile, setActiveFile] = useState('app.py')
  const [chatMessages, setChatMessages] = useState([
    { role: 'assistant', content: "Hello! I'm your AI code assistant. I can help you with:", suggestions: [
      'Code generation and optimization',
      'Debugging and refactoring',
      'Project architecture suggestions'
    ]}
  ])

  const projects = ['Current Project', 'Side Project', 'Learning Project']
  const files = [
    { name: 'src', type: 'folder', expanded: true },
    { name: 'app.py', type: 'file', indent: true },
    { name: 'config.py', type: 'file', indent: true },
    { name: 'static', type: 'folder', expanded: false },
    { name: 'templates', type: 'folder', expanded: false },
  ]

  return (
    <div className="h-screen w-screen bg-gray-900 text-white overflow-hidden">
      {/* Top Navigation Bar */}
      <nav className="h-14 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
              <span className="text-white font-bold text-xs">CA</span>
            </div>
            <span className="font-semibold text-sm">AI Code Agent</span>
          </div>
        </div>
        
        <div className="flex-1 max-w-xl mx-8">
          <div className="relative">
            <input
              type="text"
              placeholder="Quick search... (Cmd+K)"
              className="w-full bg-gray-700/50 border border-gray-600 rounded px-4 py-2 pl-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <svg className="w-4 h-4 absolute left-3 top-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-gray-700 rounded transition-colors" title="Activity Log">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
          <button className="p-2 hover:bg-gray-700 rounded transition-colors" title="Settings">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
          </div>
        </div>
      </nav>

      <div className="flex h-[calc(100vh-3.5rem)]">
        {/* Left Sidebar */}
        <aside className="w-64 bg-gray-800 border-r border-gray-700 overflow-y-auto">
          {/* PROJECTS Section */}
          <div className="p-4 border-b border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-bold text-gray-400 uppercase">PROJECTS</h3>
              <button className="text-gray-400 hover:text-white transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
            </div>
            <div className="space-y-1">
              {projects.map((project, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveProject(project)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded transition-colors ${
                    activeProject === project
                      ? 'bg-blue-600 text-white'
                      : 'hover:bg-gray-700 text-gray-300'
                  }`}
                >
                  {activeProject === project ? (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
                    </svg>
                  )}
                  <span className="text-sm">{project}</span>
                </button>
              ))}
            </div>
          </div>

          {/* FILES Section */}
          <div className="p-4 border-b border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-bold text-gray-400 uppercase">FILES</h3>
              <button className="text-gray-400 hover:text-white transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
            </div>
            <div className="space-y-1">
              {files.map((file, idx) => (
                <button
                  key={idx}
                  onClick={() => file.type === 'file' && setActiveFile(file.name)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded transition-colors ${
                    activeFile === file.name
                      ? 'bg-blue-600 text-white'
                      : 'hover:bg-gray-700 text-gray-300'
                  } ${file.indent ? 'ml-4' : ''}`}
                >
                  {file.type === 'folder' && (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  )}
                  {file.type === 'file' && (
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                    </svg>
                  )}
                  <span className="text-sm">{file.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* AI AGENTS Section */}
          <div className="p-4">
            <h3 className="text-xs font-bold text-gray-400 uppercase mb-3">AI AGENTS</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-3 p-3 bg-blue-600/20 border border-blue-500/30 rounded">
                <div className="text-2xl">🤖</div>
                <div>
                  <div className="text-sm font-semibold">Code Assistant</div>
                  <div className="text-xs text-green-400">Ready</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 hover:bg-gray-700 rounded transition-colors cursor-pointer">
                <div className="text-2xl">🔍</div>
                <div>
                  <div className="text-sm font-semibold">Analytics Agent</div>
                  <div className="text-xs text-yellow-400">Active</div>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* File Tabs */}
          <div className="h-10 bg-gray-800 border-b border-gray-700 flex items-center gap-1 px-2">
            <button
              onClick={() => setActiveFile('app.py')}
              className={`px-4 py-1.5 rounded-t text-sm transition-colors ${
                activeFile === 'app.py'
                  ? 'bg-gray-700 text-white'
                  : 'hover:bg-gray-700/50 text-gray-400'
              }`}
            >
              app.py
            </button>
            <button
              onClick={() => setActiveFile('config.py')}
              className={`px-4 py-1.5 rounded-t text-sm transition-colors ${
                activeFile === 'config.py'
                  ? 'bg-gray-700 text-white'
                  : 'hover:bg-gray-700/50 text-gray-400'
              }`}
            >
              config.py
            </button>
            <button className="p-1.5 hover:bg-gray-700 rounded transition-colors ml-auto">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>

          {/* Editor and AI Chat */}
          <div className="flex-1 flex overflow-hidden">
            {/* Code Editor */}
            <div className="flex-1 flex flex-col">
              <div className="flex-1 bg-gray-900 p-4 overflow-auto">
                <div className="max-w-4xl mx-auto">
                  <div className="text-sm font-mono">
                    <div className="mb-2"># AI Code Agent - Project Management</div>
                    <div className="mb-2">from flask import Flask, render_template</div>
                    <div className="mb-2">app = Flask(__name__)</div>
                    <div className="mb-4"></div>
                    <div className="mb-2">@app.route('/')</div>
                    <div className="mb-2">def index():</div>
                    <div className="mb-2 pl-4">return render_template('dashboard.html')</div>
                    <div className="mb-4"></div>
                    <div className="mb-2">if __name__ == '__main__':</div>
                    <div className="mb-2 pl-4">app.run(debug=True)</div>
                  </div>
                </div>
              </div>
              
              {/* AI Chat Panel */}
              <div className="h-64 bg-gray-800 border-t border-gray-700 flex flex-col">
                <div className="flex items-center justify-between p-3 border-b border-gray-700">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">AI Assistant</h3>
                    <span className="text-xs text-green-400">Online</span>
                  </div>
                  <div className="flex gap-2">
                    <button className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors">
                      AI Chat
                    </button>
                    <button className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors">
                      Run
                    </button>
                  </div>
                </div>
                
                <div className="flex-1 p-4 overflow-y-auto">
                  {chatMessages.map((msg, idx) => (
                    <div key={idx} className="mb-4">
                      <div className="flex items-start gap-3">
                        <div className="text-2xl">🤖</div>
                        <div className="flex-1">
                          <p className="text-sm mb-2">{msg.content}</p>
                          <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
                            {msg.suggestions?.map((s, i) => (
                              <li key={i}>{s}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="p-3 border-t border-gray-700">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Ask anything about your code..."
                      className="flex-1 bg-gray-700 border border-gray-600 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Panel */}
          <div className="h-48 bg-gray-800 border-t border-gray-700 flex flex-col">
            <div className="flex gap-4 px-4 py-2 border-b border-gray-700">
              <button className="text-sm font-medium text-gray-400 hover:text-white transition-colors">Terminal</button>
              <button className="text-sm font-medium text-gray-400 hover:text-white transition-colors">Logs</button>
              <button className="text-sm font-medium text-gray-400 hover:text-white transition-colors">Problems</button>
            </div>
            <div className="flex-1 p-4 font-mono text-sm overflow-auto">
              <div className="space-y-1">
                <div className="text-green-400">$ Starting AI Code Agent...</div>
                <div className="text-green-400">✓ Flask app running on http://localhost:8080</div>
                <div className="text-green-400">✓ AI Assistant connected</div>
                <div className="text-green-400">✓ All systems operational</div>
                <div className="text-gray-400">Ready for commands. Type 'help' for available options.</div>
              </div>
            </div>
          </div>
        </main>

        {/* Right Sidebar */}
        <aside className="w-80 bg-gray-800 border-l border-gray-700 overflow-y-auto">
          {/* INSIGHTS Section */}
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-xs font-bold text-gray-400 uppercase mb-3">INSIGHTS</h3>
            <div className="space-y-3">
              <div className="bg-gray-700/30 rounded p-3">
                <div className="text-sm text-gray-400 mb-1">Code Quality</div>
                <div className="text-2xl font-bold mb-1">93%</div>
                <div className="text-xs text-green-400">+5% from yesterday</div>
              </div>
              <div className="bg-gray-700/30 rounded p-3">
                <div className="text-sm text-gray-400 mb-1">Issues</div>
                <div className="text-2xl font-bold mb-1">4%</div>
                <div className="text-xs text-red-400">-2 from yesterday</div>
              </div>
              <div className="bg-gray-700/30 rounded p-3">
                <div className="text-sm text-gray-400 mb-1">Test Coverage</div>
                <div className="text-2xl font-bold mb-1">86%</div>
              </div>
            </div>
          </div>

          {/* ACTIVITIES Section */}
          <div className="p-4 border-b border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-bold text-gray-400 uppercase">ACTIVITIES</h3>
              <button className="text-xs text-gray-400 hover:text-white transition-colors">Clear</button>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="flex-1">Code committed</span>
                <span className="text-xs text-gray-400">2 min ago</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="flex-1">Tests passed</span>
                <span className="text-xs text-gray-400">5 min ago</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span className="flex-1">Project synced</span>
                <span className="text-xs text-gray-400">10 min ago</span>
              </div>
            </div>
          </div>

          {/* QUICK ACTIONS Section */}
          <div className="p-4">
            <h3 className="text-xs font-bold text-gray-400 uppercase mb-3">QUICK ACTIONS</h3>
            <div className="grid grid-cols-2 gap-2">
              <button className="px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded transition-colors text-sm">
                Deploy
              </button>
              <button className="px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded transition-colors text-sm">
                Database
              </button>
              <button className="px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded transition-colors text-sm">
                Cloud Sync
              </button>
              <button className="px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded transition-colors text-sm">
                Security
              </button>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}

