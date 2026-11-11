import ComingSoon from '../components/ui/ComingSoon'

export default function VerificationPage() {
  return <ComingSoon title="Verification Centre" description="Human verification of reports." endpoint="PATCH /reports/{id}/verify" phase={7} />
}
