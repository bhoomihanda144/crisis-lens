import { useRef, useState } from 'react'
import { FlaskConical } from 'lucide-react'
import PageHeader from '../components/ui/PageHeader'
import Badge from '../components/ui/Badge'
import EmptyState from '../components/ui/EmptyState'
import ScenarioForm from '../components/simulation/ScenarioForm'
import ScenarioResult from '../components/simulation/ScenarioResult'
import ScenarioComparison from '../components/simulation/ScenarioComparison'
import { runSimulation } from '../services/simulationService'

const MAX_SCENARIOS = 4

export default function SimulationPage() {
  const [scenarios, setScenarios] = useState([])
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const nextKey = useRef(1)

  async function run(payload) {
    setRunning(true)
    setError('')
    try {
      const response = await runSimulation(payload)
      const key = `s${nextKey.current}`
      nextKey.current += 1
      setScenarios((prev) => [...prev, { ...response, key }])
    } catch (err) {
      setError(err.message)
    } finally {
      setRunning(false)
    }
  }

  const latest = scenarios[scenarios.length - 1]

  return (
    <>
      <PageHeader
        title="What-if Simulation Centre"
        description="Test a hypothetical disaster and your available resources. Results are estimates. They never change real incidents, and humans decide what to do with them."
        actions={<Badge tone="verify">Hypothetical only</Badge>}
      />

      <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
        <ScenarioForm
          onRun={run}
          running={running}
          error={error}
          blockedReason={scenarios.length >= MAX_SCENARIOS ? `You have ${MAX_SCENARIOS} scenarios. Remove one from the comparison to add another.` : ''}
        />
        <div className="min-w-0">
          {latest ? (
            <ScenarioResult scenario={latest} />
          ) : (
            <EmptyState
              icon={FlaskConical}
              title="No scenarios yet"
              description="Choose an example or set your own numbers, then press Run simulation."
            />
          )}
        </div>
      </div>

      {scenarios.length > 0 && (
        <div className="mt-6">
          <ScenarioComparison
            scenarios={scenarios}
            onRemove={(key) => setScenarios((prev) => prev.filter((s) => s.key !== key))}
            onClear={() => setScenarios([])}
          />
        </div>
      )}
    </>
  )
}