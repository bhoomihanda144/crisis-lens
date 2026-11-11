import ComingSoon from '../components/ui/ComingSoon'

export default function AiAnalysisPage() {
  return <ComingSoon title="AI Analysis" description="Duplicates, independent sources, freshness and conflicts." endpoint="POST /analyze/{report_id}" phase={7} />
}
