"use client";

import { useApplication } from "@/features/applications/hooks/use-applications";
import { RiskResultCard } from "@/features/applications/components/risk-result-card";
import { STATUS_META } from "@/features/applications/domain/status";
import { useVerificationDetails } from "@/features/officer-review/hooks/use-officer-review";
import { ArtifactPreview } from "@/features/officer-review/components/artifact-preview";
import { EvidenceCard } from "@/features/officer-review/components/evidence-card";
import { DecisionPanel } from "@/features/officer-review/components/decision-panel";
import { AuditTrailCard } from "@/features/officer-review/components/audit-trail-card";
import { GenerateReportButton } from "@/features/reports/components/generate-report-button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Badge } from "@/shared/ui/badge";
import { Skeleton } from "@/shared/ui/skeleton";

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const KIND_LABEL: Record<string, string> = {
  applicant_photo: "Applicant",
  coapplicant_photo: "Co-applicant",
  verification_video: "Verification video",
};

export function OfficerReviewDetail({ applicationId }: { applicationId: string }) {
  const { data: app, isLoading: appLoading } = useApplication(applicationId);
  const { data: details, isLoading: detailsLoading } = useVerificationDetails(applicationId);

  if (appLoading || !app) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  const status = STATUS_META[app.status];
  const photoArtifacts = app.artifacts.filter((a) => a.kind !== "document");
  const decidable = app.status === "pending_review";

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant={status.variant}>{status.label}</Badge>
        <span className="text-sm text-muted-foreground">{app.reference_no}</span>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Applicant details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <Row label="Amount" value={currency.format(app.loan_amount)} />
          {app.loan_purpose ? <Row label="Purpose" value={app.loan_purpose} /> : null}
          <Row label="Co-applicant" value={app.co_applicant?.full_name ?? "—"} />
        </CardContent>
      </Card>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold">Evidence</h2>
        <div className="grid grid-cols-2 gap-3">
          {photoArtifacts.map((artifact) => (
            <ArtifactPreview
              key={artifact.id}
              applicationId={app.id}
              artifact={artifact}
              label={KIND_LABEL[artifact.kind] ?? artifact.kind}
            />
          ))}
        </div>
      </section>

      {detailsLoading || !details ? (
        <Skeleton className="h-48 w-full" />
      ) : (
        <EvidenceCard details={details} />
      )}

      {app.risk ? <RiskResultCard risk={app.risk} /> : null}

      {decidable ? (
        <DecisionPanel applicationId={app.id} />
      ) : (
        <Card>
          <CardContent className="p-5 text-sm text-muted-foreground">
            This application is not currently awaiting review.
          </CardContent>
        </Card>
      )}

      <GenerateReportButton applicationId={app.id} />

      <AuditTrailCard applicationId={app.id} />
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-muted-foreground">{label}</span>
      <span className="text-right font-medium">{value}</span>
    </div>
  );
}
