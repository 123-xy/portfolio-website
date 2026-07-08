import { AlertTriangle, CheckCircle2, MessageSquareQuote, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Badge } from "@/shared/ui/badge";
import type { VerificationDetails } from "@/features/officer-review/domain/schemas";

const CONSENT_LABEL: Record<string, string> = {
  explicit_yes: "Explicit consent",
  ambiguous: "Ambiguous",
  explicit_no: "Explicit refusal",
  not_detected: "Not detected",
};

function pct(value: number | null): string {
  return value === null ? "—" : `${Math.round(value * 100)}%`;
}

/** Renders the transcript and the consent/intent/fraud findings the pipeline
 * derived from it — the primary evidence an officer reads before deciding. */
export function EvidenceCard({ details }: { details: VerificationDetails }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquareQuote className="size-4" />
          Transcript & findings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <blockquote className="rounded-xl bg-secondary px-4 py-3 text-sm italic text-secondary-foreground">
          {details.transcript_text ?? "No transcript available."}
        </blockquote>

        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="space-y-1">
            <span className="text-muted-foreground">Consent</span>
            <div className="flex items-center gap-1.5">
              <Badge variant={details.consent_status === "explicit_yes" ? "success" : "warning"}>
                {details.consent_status
                  ? (CONSENT_LABEL[details.consent_status] ?? details.consent_status)
                  : "Unknown"}
              </Badge>
              <span className="text-muted-foreground">{pct(details.consent_confidence)}</span>
            </div>
          </div>
          <div className="space-y-1">
            <span className="text-muted-foreground">Intent</span>
            <div className="flex items-center gap-1.5">
              {details.intent_aligned ? (
                <CheckCircle2 className="size-4 text-success" />
              ) : (
                <XCircle className="size-4 text-destructive" />
              )}
              <span className="font-medium">{pct(details.intent_confidence)}</span>
            </div>
          </div>
        </div>

        {details.consent_matched_phrases.length > 0 ? (
          <p className="text-xs text-muted-foreground">
            Matched phrases: {details.consent_matched_phrases.join(", ")}
          </p>
        ) : null}

        {details.fraud_score !== null ? (
          <div className="flex items-start gap-2 rounded-xl bg-accent px-3 py-2 text-xs text-accent-foreground">
            <AlertTriangle className="mt-0.5 size-3.5 shrink-0" />
            <span>
              Fraud score {pct(details.fraud_score)}
              {details.fraud_signals.length > 0
                ? ` — ${details.fraud_signals.join(", ")}`
                : " — no signals detected"}
            </span>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
