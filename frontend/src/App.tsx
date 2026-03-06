import ChatWindow from './components/ChatWindow'

function App() {
  return (
    <div className="h-screen w-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white flex flex-col">
      {/* Header */}
      <header className="flex items-center gap-3 px-6 py-4 border-b border-white/10 bg-gray-900/60 backdrop-blur-md">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
          <span className="text-lg">⚡</span>
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight">Jenkins AI Assistant</h1>
          <p className="text-xs text-gray-500">Powered by RAG · Local LLM</p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-gray-500">Online</span>
        </div>
      </header>

      {/* Chat */}
      <main className="flex-1 overflow-hidden">
        <div className="h-full max-w-4xl mx-auto">
          <ChatWindow />
        </div>
      </main>
    </div>
  )
}

export default App
