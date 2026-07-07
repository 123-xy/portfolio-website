import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Badge } from "@/shared/ui/badge";
import {
  RISK_META,
  STATUS_META,
} from "@/features/applications/domain/status";
import { DEMO_APPLICATIONS } from "@/features/applications/api/fixtures";

export const metadata: Metadata = { title: "Application" };

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

export default async function ApplicationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  // Read from fixtures for now; Phase 8 swaps this for a real query.
  const application = DEMO_APPLICATIONS.find((a) => a.id === id);
  if (!application) notFound();

  const status = STATUS_META[application.status];

  return (
    <AppShell title={application.coApplicantName} subtitle={application.referenceNo} showBack>
      <div className="space-y-5">
        <div className="flex flex-wrap gap-2">
          <Badge variant={status.variant}>{status.label}</Badge>
          {application.riskBand ? (
            <Badge variant={RISK_META[application.riskBand].variant}>
              {RISK_META[application.riskBand].label}
            </Badge>
          ) : null}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Loan details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <Row label="Amount" value={currency.format(application.loanAmount)} />
            <Row label="Co-applicant" value={application.coApplicantName} />
            <Row label="Reference" value={application.referenceNo} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Verification result</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            The AI pipeline breakdown (face match, consent, intent, fraud signals,
            and the weighted risk score) renders here once the pipeline and risk
            engine ship in Phases 9–10.
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}
