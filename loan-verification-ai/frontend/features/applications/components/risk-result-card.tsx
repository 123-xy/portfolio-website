import { CheckCircle2, Gauge, ShieldAlert, ShieldCheck } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { RISK_META } from "@/features/applications/domain/status";
import type { RiskScoreDto } from "@/features/applications/domain/schemas";

const COMPONENT_LABELS: Record<string, string> = {
  face_match: "Face match",
  speech: "Consent",
  intent: "Intent",
  fraud: "Fraud-free",
};

const RECOMMENDATION_META: Record<string, { label: string; icon: typeof ShieldCheck }> = {
  auto_approve_candidate: { label: "Candidate for approval", icon: ShieldCheck },
  needs_review: { label: "Needs officer review", icon: Gauge },
  high_risk_reject_candidate: { label: "Candidate for rejection", icon: ShieldAlert },
};

/** Renders the AI pipeline's risk assessment: overall band, weighted component
 * breakdown, and the human-readable reasons behind the score. Every number
 * here traces back to a persisted verification_results row. */
export function RiskResultCard({ risk }: { risk: RiskScoreDto }) {
  const band = RISK_META[risk.band];
  const recommendation = RECOMMENDATION_META[risk.recommendation];
  const RecommendationIcon = recommendation?.icon ?? Gauge;

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle>Verification result</CardTitle>
        <Badge variant={band.variant}>{band.label}</Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-2 rounded-xl bg-accent px-3 py-2 text-sm font-medium text-accent-foreground">
          <RecommendationIcon className="size-4 shrink-0" />
          {recommendation?.label ?? risk.recommendation}
        </div>

        <div className="space-y-2">
          {Object.entries(risk.component_scores).map(([key, value]) => (
            <div key={key} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">{COMPONENT_LABELS[key] ?? key}</span>
                <span className="font-medium">{Math.round(value * 100)}%</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
                <div
                  className="h-full rounded-full bg-primary"
                  style={{ width: `${Math.round(value * 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        <ul className="space-y-1.5 border-t border-border pt-3">
          {risk.reasons.map((reason, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
              <CheckCircle2 className="mt-0.5 size-3.5 shrink-0 text-primary" />
              {reason}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
