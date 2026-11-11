import { useState } from 'react'
import { Activity, AlertTriangle, BadgeCheck, ShieldQuestion } from 'lucide-react'
import PageHeader from '../components/ui/PageHeader'
import Card, { CardHeader } from '../components/ui/Card'
import StatCard from '../components/ui/StatCard'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Table from '../components/ui/Table'
import Modal from '../components/ui/Modal'
import Skeleton from '../components/ui/Skeleton'
import EmptyState from '../components/ui/EmptyState'
import ErrorState from '../components/ui/ErrorState'
import { SearchInput, Select } from '../components/ui/Input'
import { mockReports, mockIncidents } from '../data/mockData'
import { timeAgo, labelOf } from '../utils/format'
import { freshnessTone, reportStatusTone } from '../utils/tones'

const columns = [
  { key: 'id', header: 'Report', render: (r) => <span className="font-mono text-xs text-accent">{r.id}</span> },
  { key: 'text', header: 'Text', render: (r) => <span className="line-clamp-1 max-w-xs">{r.text}</span> },
  { key: 'source', header: 'Source', render: (r) => r.source.name },
  {
    key: 'freshness',
    header: 'Freshness',
    render: (r) => <Badge tone={freshnessTone[r.analysis.freshness.status]}>{labelOf(r.analysis.freshness.status)}</Badge>,
  },
  { key: 'status', header: 'Status', render: (r) => <Badge tone={reportStatusTone[r.status]}>{labelOf(r.status)}</Badge> },
  { key: 'reported', header: 'Reported', render: (r) => timeAgo(r.reported_at) },
]

export default function OverviewPage() {
  const [search, setSearch] = useState('')
  const [freshness, setFreshness] = useState('all')
  const [modalOpen, setModalOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showError, setShowError] = useState(false)

  const rows = mockReports.filter(
    (r) =>
      r.text.toLowerCase().includes(search.toLowerCase()) &&
      (freshness === 'all' || r.analysis.freshness.status === freshness),
  )

  const needVerification = mockReports.filter((r) => r.analysis.scores.verification_priority.level === 'high').length
  const critical = mockIncidents.filter((i) => i.severity === 'critical').length

  function simulateLoading() {
    setLoading(true)
    setTimeout(() => setLoading(false), 1500)
  }

  return (
    <>
      <PageHeader
        title="Overview (design system preview)"
        description="Temporary page to test every reusable component. Phase 6 replaces it with the real dashboard."
        actions={<Button onClick={() => setModalOpen(true)}>Open modal</Button>}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Reports" value={mockReports.length} icon={Activity} hint="Simulated" />
        <StatCard label="Critical incidents" value={critical} icon={AlertTriangle} tone="critical" />
        <StatCard label="Need verification first" value={needVerification} icon={ShieldQuestion} tone="verify" />
        <StatCard label="Verified reports" value={mockReports.filter((r) => r.status === 'verified').length} icon={BadgeCheck} tone="verified" />
      </div>

      <Card className="mt-6">
        <CardHeader title="Buttons and badges" />
        <div className="flex flex-wrap gap-2">
          <Button>Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="danger">Danger</Button>
          <Button variant="ghost">Ghost</Button>
          <Button loading>Loading</Button>
          <Button disabled>Disabled</Button>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Badge tone="critical">Critical</Badge>
          <Badge tone="verify">Needs verification</Badge>
          <Badge tone="verified">Verified</Badge>
          <Badge tone="info">Info</Badge>
          <Badge>Neutral</Badge>
        </div>
      </Card>

      <Card className="mt-6">
        <CardHeader
          title="Filterable table"
          subtitle="Search by text and filter by freshness."
          action={<Button size="sm" variant="secondary" onClick={simulateLoading}>Simulate loading</Button>}
        />
        <div className="mb-4 grid gap-3 sm:grid-cols-[1fr_200px]">
          <SearchInput value={search} onChange={setSearch} placeholder="Search report text…" label="Search reports" />
          <Select
            value={freshness}
            onChange={setFreshness}
            label="Filter by freshness"
            options={[
              { value: 'all', label: 'All freshness' },
              { value: 'recent', label: 'Recent' },
              { value: 'aging', label: 'Aging' },
              { value: 'stale', label: 'Stale' },
            ]}
          />
        </div>
        {loading ? (
          <div className="space-y-2">
            {[1, 2, 3, 4].map((n) => <Skeleton key={n} className="h-10 w-full" />)}
          </div>
        ) : rows.length === 0 ? (
          <EmptyState title="No reports match" description="Try a different search or filter." />
        ) : (
          <Table columns={columns} rows={rows} rowKey={(r) => r.id} caption="Simulated reports" />
        )}
      </Card>

      <Card className="mt-6">
        <CardHeader
          title="Error state"
          action={<Button size="sm" variant="secondary" onClick={() => setShowError((v) => !v)}>{showError ? 'Hide' : 'Show'} error</Button>}
        />
        {showError ? (
          <ErrorState message="Could not reach the backend. This is a test message." onRetry={() => setShowError(false)} />
        ) : (
          <p className="text-sm text-text-muted">Press the button to preview the error state.</p>
        )}
      </Card>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Example dialog"
        footer={<Button onClick={() => setModalOpen(false)}>Close</Button>}
      >
        Press Escape, click outside, or use the buttons to close this dialog.
      </Modal>
    </>
  )
}