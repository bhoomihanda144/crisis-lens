import ComingSoon from '../components/ui/ComingSoon'

export default function EvidenceGraphPage() {
  return <ComingSoon title="Evidence Relationship Graph" description="How reports relate: original, duplicate, forwarded, corroborating, conflicting." endpoint="GET /incidents/{id}/evidence-graph" phase={8} />
}
