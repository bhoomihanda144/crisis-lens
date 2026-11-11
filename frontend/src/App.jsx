function App() {
  return (
    <div className="min-h-screen bg-navy-950 p-8">
      <h1 className="text-3xl font-bold text-accent">CrisisLens</h1>
      <p className="mt-2 text-text-muted">Trust-Aware Emergency Intelligence</p>
      <div className="mt-6 flex gap-3">
        <span className="rounded-md bg-critical/20 px-3 py-1 text-critical">Critical</span>
        <span className="rounded-md bg-verify/20 px-3 py-1 text-verify">Needs verification</span>
        <span className="rounded-md bg-verified/20 px-3 py-1 text-verified">Verified</span>
      </div>
    </div>
  )
}

export default App