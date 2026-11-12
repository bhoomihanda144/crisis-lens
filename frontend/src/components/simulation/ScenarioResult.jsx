import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import Card, { CardHeader } from '../ui/Card'
import Badge from '../ui/Badge'
import { labelOf } from '../../utils/format'

export function shortfallOf(results, resource) {
  return results?.shortages?.find((s) => s.resource === resource)?.shortfall ?? 0
}

export default function ScenarioResult({ scenario }) {
  if (!scenario) return null
  const { inputs = {}, results = {} } = scenario
  const resourceDemand = results.resource_demand || {}
  
  const rows = [
    { label: 'Rescue teams', required: resourceDemand.rescue_teams ?? 0, available: inputs.rescue_teams ?? 0, shortfall: shortfallOf(results, 'rescue_teams') },
    { label: 'Ambulances', required: resourceDemand.ambulances ?? 0, available: inputs.available_ambulances ?? 0, shortfall: shortfallOf(results, 'ambulances') },
  ]

  return (
    <Card className="border-accent/30">
      <CardHeader
        title={inputs.scenario_name || 'Scenario result'}
        subtitle="Latest result"
        action={<Badge tone="verify">SIMULATION</Badge>}
      />
      <p className="text-sm">{results.summary}</p>

      <div className="mt-4 overflow-x-auto rounded-xl border border-navy-700">
        <table className="w-full text-left text-sm">
          <caption className="sr-only">Resources required compared with available</caption>
          <thead className="bg-navy-900 text-xs uppercase tracking-wide text-text-muted">
            <tr>
              <th scope="col" className="px-4 py-2 font-medium">Resource</th>
              <th scope="col" className="px-4 py-2 font-medium">Required</th>
              <th scope="col" className="px-4 py-2 font-medium">Available</th>
              <th scope="col" className="px-4 py-2 font-medium">Shortfall</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-navy-700">
            {rows.map((r) => (
              <tr key={r.label}>
                <td className="px-4 py-2">{r.label}</td>
                <td className="px-4 py-2 font-mono">{r.required}</td>
                <td className="px-4 py-2 font-mono">{r.available}</td>
                <td className="px-4 py-2">
                  {r.shortfall > 0 ? <Badge tone="critical">Short by {r.shortfall}</Badge> : <Badge tone="verified">Covered</Badge>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="mt-4 text-sm">
        Estimated response delay: <span className="font-mono font-medium text-accent">{results.estimated_response_delay_minutes ?? 0} min</span>
      </p>

      <h3 className="mb-2 mt-4 text-sm font-medium">Changed priorities</h3>
      {(!results.priority_changes || results.priority_changes.length === 0) ? (
        <p className="text-sm text-text-muted">No incident changes rank in this scenario.</p>
      ) : (
        <ul className="space-y-2 text-sm">
          {results.priority_changes.map((c) => (
            <li key={c.incident_id} className="rounded-md bg-navy-900 px-3 py-2">
              <Link to={`/incidents/${c.incident_id}`} className="font-medium text-accent hover:underline">{c.title}</Link>
              <span className="ml-2 inline-flex items-center gap-1 font-mono text-xs">
                rank {c.baseline_rank} <ArrowRight className="h-3 w-3" aria-hidden="true" /> {c.scenario_rank}
              </span>
              <span className="block text-xs text-text-muted">{c.reason}</span>
            </li>
          ))}
        </ul>
      )}
      <p className="mt-4 text-xs text-text-muted">
        This is a what-if estimate. Real incident scores are unchanged, and a human decides how to use these results.
      </p>
    </Card>
  )
}