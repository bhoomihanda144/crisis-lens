import { DATA_ORIGIN, mockReports, mockIncidents, mockGraphs, getMockPriority, mockSimulate } from './data/mockData'

function App() {
  const sim = mockSimulate({ affected_population: 12000, disaster_severity: 4, rescue_teams: 6, blocked_roads: 3, available_ambulances: 5 })
  return (
    <div className="min-h-screen bg-navy-950 p-8">
      <h1 className="text-3xl font-bold text-accent">CrisisLens</h1>
      <p className="mt-2 inline-block rounded bg-verify/20 px-2 py-1 text-verify">Data: {DATA_ORIGIN}</p>
      <ul className="mt-6 space-y-1 text-text-muted">
        <li>Reports: {mockReports.length}</li>
        <li>Incidents: {mockIncidents.length}</li>
        <li>Graph nodes for inc_001: {mockGraphs.inc_001.nodes.length}</li>
        <li>Top urgency incident: {getMockPriority('urgency').items[0].title}</li>
        <li>Top verify-first incident: {getMockPriority('verification').items[0].title}</li>
        <li>Simulated shortages: {sim.results.shortages.length}</li>
      </ul>
    </div>
  )
}

export default App