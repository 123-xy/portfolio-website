"use client";

import * as React from "react";
import { Loader2, Send } from "lucide-react";
import { useApplication, useSubmitApplication } from "@/features/applications/hooks/use-applications";
import { UploadRow } from "@/features/applications/components/upload-row";
import { STATUS_META } from "@/features/applications/domain/status";
import { REQUIRED_KINDS, type ArtifactKind } from "@/features/applications/domain/schemas";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Skeleton } from "@/shared/ui/skeleton";

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const KIND_META: Record<ArtifactKind, { label: string; description: string }> = {
  applicant_photo: { label: "Applicant photo", description: "A clear photo of the applicant" },
  coapplicant_photo: { label: "Co-applicant photo", description: "A clear photo of the co-applicant" },
  verification_video: { label: "Verification video", description: "Co-applicant states consent on camera" },
  document: { label: "Document", description: "Supporting document" },
};

const PRESENT = new Set(["uploaded", "ingested", "validated"]);

export function ApplicationDetail({ applicationId }: { applicationId: string }) {
  const { data: app, isLoading } = useApplication(applicationId);
  const submit = useSubmitApplication(applicationId);
  const [submitError, setSubmitError] = React.useState<string | null>(null);

  if (isLoading || !app) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  const status = STATUS_META[app.status];
  const uploadedKinds = new Set(
    app.artifacts.filter((a) => PRESENT.has(a.status)).map((a) => a.kind),
  );
  const allRequiredUploaded = REQUIRED_KINDS.every((k) => uploadedKinds.has(k));
  const editable = app.status === "draft" || app.status === "more_info_requested";

  async function onSubmit() {
    setSubmitError(null);
    try {
      await submit.mutateAsync();
    } catch (err) {
      setSubmitError(
        err instanceof Error && "status" in err ? "Please complete all required uploads." : "Submit failed.",
      );
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant={status.variant}>{status.label}</Badge>
        <span className="text-sm text-muted-foreground">{app.reference_no}</span>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Loan details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <Row label="Amount" value={currency.format(app.loan_amount)} />
          {app.loan_purpose ? <Row label="Purpose" value={app.loan_purpose} /> : null}
          <Row label="Co-applicant" value={app.co_applicant?.full_name ?? "—"} />
        </CardContent>
      </Card>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold">Verification artifacts</h2>
        {REQUIRED_KINDS.map((kind) => (
          <UploadRow
            key={kind}
            applicationId={app.id}
            kind={kind}
            label={KIND_META[kind].label}
            description={KIND_META[kind].description}
            uploaded={uploadedKinds.has(kind)}
            disabled={!editable}
          />
        ))}
      </section>

      {editable ? (
        <div className="space-y-2">
          {submitError ? (
            <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {submitError}
            </p>
          ) : null}
          <Button
            size="full"
            onClick={onSubmit}
            disabled={!allRequiredUploaded || submit.isPending}
          >
            {submit.isPending ? <Loader2 className="animate-spin" /> : <Send />}
            {allRequiredUploaded ? "Submit for verification" : "Upload all artifacts to submit"}
          </Button>
        </div>
      ) : (
        <Card>
          <CardContent className="p-5 text-sm text-muted-foreground">
            This application has been submitted. The AI verification result and risk
            breakdown appear here once the pipeline completes (Phases 9–10).
          </CardContent>
        </Card>
      )}
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
