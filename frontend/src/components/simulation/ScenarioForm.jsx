import { useState } from 'react'
import { FlaskConical } from 'lucide-react'
import Card, { CardHeader } from '../ui/Card'
import Button from '../ui/Button'

export const PRESETS = [
  {
    label: 'Moderate flood, roads open',
    values: { scenario_name: 'Moderate flood, roads open', affected_population: 5000, disaster_severity: 2, rescue_teams: 4, blocked_roads: 0, available_ambulances: 4 },
  },
  {
    label: 'Heavy rain, 3 roads blocked',
    values: { scenario_name: 'Heavy rain, 3 roads blocked', affected_population: 10000, disaster_severity: 3, rescue_teams: 2, blocked_roads: 3, available_ambulances: 3 },
  },
  {
    label: 'Major earthquake',
    values: { scenario_name: 'Major earthquake', affected_population: 50000, disaster_severity: 5, rescue_teams: 10, blocked_roads: 5, available_ambulances: 10 },
  },
]

const FIELDS = [
  { key: 'affected_population', label: 'Affected population', min: 0, max: 10000000 },
  { key: 'rescue_teams', label: 'Rescue teams available', min: 0, max: 1000 },
  { key: 'blocked_roads', label: 'Blocked roads', min: 0, max: 200 },
  { key: 'available_ambulances', label: 'Ambulances available', min: 0, max: 1000 },
]
const SEVERITY_TEXT = { 1: 'Minor', 2: 'Moderate', 3: 'Serious', 4: 'Severe', 5: 'Catastrophic' }
const field = 'mt-1 w-full rounded-lg border border-navy-600 bg-navy-900 px-3 py-2 text-sm'

const toForm = (values) => Object.fromEntries(Object.entries(values).map(([k, v]) => [k, String(v)]))

export default function ScenarioForm({ onRun, running, error, blockedReason }) {
  const [values, setValues] = useState(() => toForm(PRESETS[0].values))
  const [localError, setLocalError] = useState('')

  const set = (key, value) => setValues((prev) => ({ ...prev, [key]: value }))

  function submit() {
    const payload = { scenario_name: values.scenario_name.trim() || 'Untitled scenario' }
    for (const f of FIELDS) {
      const n = Number(values[f.key])
      if (values[f.key] === '' || !Number.isInteger(n) || n < f.min || n > f.max) {
        return setLocalError(`${f.label} must be a whole number from ${f.min} to ${f.max}.`)
      }
      payload[f.key] = n
    }
    payload.disaster_severity = Number(values.disaster_severity)
    setLocalError('')
    return onRun(payload)
  }

  const shownError = localError || error

  return (
    <Card>
      <CardHeader title="Scenario controls" subtitle="Describe a hypothetical disaster and the resources you have." />

      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-text-muted">Start from an example</p>
      <div className="mb-4 flex flex-wrap gap-2">
        {PRESETS.map((p) => (
          <Button key={p.label} size="sm" variant="secondary" onClick={() => setValues(toForm(p.values))}>{p.label}</Button>
        ))}
      </div>

      <div className="space-y-3">
        <label className="block text-sm">
          Scenario name
          <input value={values.scenario_name} onChange={(e) => set('scenario_name', e.target.value)} className={field} maxLength={80} />
        </label>

        <div className="grid gap-3 sm:grid-cols-2">
          {FIELDS.map((f) => (
            <label key={f.key} className="block text-sm">
              {f.label}
              <input
                type="number"
                inputMode="numeric"
                min={f.min}
                max={f.max}
                step={1}
                value={values[f.key]}
                onChange={(e) => set(f.key, e.target.value)}
                className={field}
              />
            </label>
          ))}
        </div>

        <label className="block text-sm">
          Disaster severity: <span className="font-medium text-accent">{values.disaster_severity} · {SEVERITY_TEXT[values.disaster_severity]}</span>
          <input
            type="range"
            min={1}
            max={5}
            step={1}
            value={values.disaster_severity}
            onChange={(e) => set('disaster_severity', e.target.value)}
            className="mt-2 h-2 w-full cursor-pointer accent-accent"
          />
          <span className="flex justify-between text-xs text-text-muted"><span>1</span><span>5</span></span>
        </label>
      </div>

      {shownError && <p role="alert" className="mt-3 rounded-lg border border-critical/40 bg-critical/10 px-3 py-2 text-sm text-red-300">{shownError}</p>}
      {blockedReason && <p className="mt-3 text-sm text-text-muted">{blockedReason}</p>}

      <Button className="mt-4" icon={FlaskConical} loading={running} disabled={Boolean(blockedReason)} onClick={submit}>
        Run simulation
      </Button>
      <p className="mt-2 text-xs text-text-muted">A simulation tests a hypothetical. It never changes real incidents or dispatches anyone.</p>
    </Card>
  )
}