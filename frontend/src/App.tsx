/**
 * App.tsx — Placeholder landing page (Setup Phase)
 *
 * This page exists only to verify:
 *   1. Vite builds correctly
 *   2. Tailwind CSS is configured correctly
 *   3. The dev server starts without errors
 *
 * All business UI (configuration forms, pricing, dashboards)
 * will be implemented in later milestones (M7+).
 */

function App() {
  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center">

      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="text-center space-y-4 px-6">

        {/* Logo placeholder */}
        <div className="flex justify-center mb-8">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-2xl">
            <span className="text-4xl">🏢</span>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-4xl font-bold tracking-tight text-white">
          Elevator Configuration Engine
        </h1>

        <p className="text-xl text-slate-400 max-w-lg">
          Rule-Based CPQ System — Setup Phase Complete
        </p>

        {/* Status badges */}
        <div className="flex justify-center gap-3 pt-4 flex-wrap">
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-900/50 text-emerald-400 text-sm font-medium border border-emerald-700">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            Backend Running
          </span>
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-900/50 text-blue-400 text-sm font-medium border border-blue-700">
            <span className="w-2 h-2 rounded-full bg-blue-400"></span>
            Frontend Running
          </span>
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-900/50 text-purple-400 text-sm font-medium border border-purple-700">
            <span className="w-2 h-2 rounded-full bg-purple-400"></span>
            80 Tests Passing
          </span>
        </div>

        {/* Quick links */}
        <div className="flex justify-center gap-4 pt-8">
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition-colors duration-200 shadow-lg"
          >
            Open Swagger UI →
          </a>
          <a
            href="http://127.0.0.1:8000/api/v1/health"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 rounded-xl bg-slate-700 hover:bg-slate-600 text-white font-medium transition-colors duration-200"
          >
            Health Check →
          </a>
        </div>

        {/* Milestone status */}
        <div className="mt-12 grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-2xl text-sm">
          {[
            { label: 'Setup',   status: 'done',    emoji: '✅' },
            { label: 'M1 Components', status: 'next', emoji: '⏳' },
            { label: 'M2 Rules',      status: 'todo', emoji: '⬜' },
            { label: 'M3 Deps',       status: 'todo', emoji: '⬜' },
          ].map(({ label, status, emoji }) => (
            <div
              key={label}
              className={`rounded-xl p-3 border text-center ${
                status === 'done'
                  ? 'bg-emerald-900/30 border-emerald-700 text-emerald-300'
                  : status === 'next'
                  ? 'bg-blue-900/30 border-blue-700 text-blue-300'
                  : 'bg-slate-800 border-slate-700 text-slate-500'
              }`}
            >
              <div className="text-lg mb-1">{emoji}</div>
              <div className="font-medium">{label}</div>
            </div>
          ))}
        </div>

        <p className="text-slate-600 text-xs mt-8">
          UI implementation begins in Milestone 7
        </p>
      </div>
    </div>
  )
}

export default App
