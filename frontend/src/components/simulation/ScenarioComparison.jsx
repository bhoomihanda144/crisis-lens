import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { X } from 'lucide-react'
import Card, { CardHeader } from '../ui/Card'
import Badge from '../ui/Badge'
import Button from '../ui/Button'
import { shortfallOf } from './ScenarioResult'

const short = (text) => (text.length > 18 ? `${text.slice(0, 18)}…` : text)
const num = (n) => n.toLocaleString('en-IN')

export default function ScenarioComparison({ scenarios, onRemove, onClear }) {
  const rows = [
    { label: 'Affected population', cell: (s) => num(s.inputs.affected_population) },
    { label: 'Disaster severity', cell: (s) => `${s.inputs.disaster_severity} of 5` },
    { label: 'Blocked roads', cell: (s) => s.inputs.blocked_roads },
    { label: 'Rescue teams (required / available)', cell: (s) => `${s.results.resource_demand.rescue_teams} / ${s.inputs.rescue_teams}` },
    { label: 'Ambulances (required / available)', cell: (s) => `${s.results.resource_demand.ambulances} / ${s.inputs.available_ambulances}` },
    {
      label: 'Resource shortages',
      cell: (s) => {
        const teams = shortfallOf(s.results, 'rescue_teams')
        const ambulances = shortfallOf(s.results, 'ambulances')
        if (!teams && !ambulances) return <Badge tone="verified">None</Badge>
        return (
          <div className="flex flex-col items-start gap-1">
            {teams > 0 && <Badge tone="critical">Teams short by {teams}</Badge>}
            {ambulances > 0 && <Badge tone="critical">Ambulances short by {ambulances}</Badge>}
          </div>
        )
      },
    },
    { label: 'Estimated response delay', cell: (s) => `${s.results.estimated_response_delay_minutes} min` },
    {
      label: 'Changed priorities',
      cell: (s) =>
        s.results.priority_changes.length === 0 ? (
          <span className="text-text-muted">None</span>
        ) : (
          <ul className="space-y-1">
            {s.results.priority_changes.map((c) => (
              <li key={c.incident_id} className="text-xs">{c.title}: rank {c.baseline_rank} → {c.scenario_rank}</li>
            ))}
          </ul>
        ),
    },
  ]

  const chartData = scenarios.map((s) => ({
    name: short(s.inputs.scenario_name || 'Scenario'),
    'Teams required': s.results.resource_demand.rescue_teams,
    'Teams available': s.inputs.rescue_teams,
    'Ambulances required': s.results.resource_demand.ambulances,
    'Ambulances available': s.inputs.available_ambulances,
  }))

  return (
    <Card>
      <CardHeader
        title="Scenario comparison"
        subtitle={scenarios.length < 2 ? 'Run a second scenario to compare it with this one.' : 'Up to four scenarios side by side.'}
        action={<Button size="sm" variant="ghost" onClick={onClear}>Clear all</Button>}
      />

      <div className="overflow-x-auto rounded-xl border border-navy-700">
        <table className="w-full text-left text-sm">
          <caption className="sr-only">Comparison of simulated scenarios</caption>
          <thead className="bg-navy-900 text-xs text-text-muted">
            <tr>
              <th scope="col" className="px-4 py-3 font-medium uppercase tracking-wide">Measure</th>
              {scenarios.map((s) => (
                <th key={s.key} scope="col" className="min-w-44 px-4 py-3 font-medium">
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-sm text-text-primary">{s.inputs.scenario_name || 'Scenario'}</span>
                    <button
                      type="button"
                      onClick={() => onRemove(s.key)}
                      aria-label={`Remove ${s.inputs.scenario_name || 'scenario'}`}
                      className="rounded p-0.5 text-text-muted hover:bg-navy-700 hover:text-text-primary"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-navy-700 bg-navy-800">
            {rows.map((row) => (
              <tr key={row.label}>
                <th scope="row" className="px-4 py-3 text-left font-normal text-text-muted">{row.label}</th>
                {scenarios.map((s) => (
                  <td key={s.key} className="px-4 py-3 align-top">{row.cell(s)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3 className="mb-2 mt-6 text-sm font-medium">Resources required against available</h3>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid stroke="#223660" strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} stroke="#223660" />
            <YAxis allowDecimals={false} tick={{ fill: '#94a3b8', fontSize: 12 }} stroke="#223660" />
            <Tooltip
              cursor={{ fill: 'rgba(148,163,184,0.08)' }}
              contentStyle={{ background: '#0f1b33', border: '1px solid #223660', borderRadius: 8 }}
              labelStyle={{ color: '#e6edf8' }}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
            <Bar dataKey="Teams required" fill="#f97316" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Teams available" fill="#22d3ee" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Ambulances required" fill="#ef4444" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Ambulances available" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}