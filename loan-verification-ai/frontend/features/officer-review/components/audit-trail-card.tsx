"use client";

import { History } from "lucide-react";
import { useAuditTrail } from "@/features/officer-review/hooks/use-officer-review";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Skeleton } from "@/shared/ui/skeleton";

const ACTION_LABEL: Record<string, string> = {
  officer_decision: "Officer decision",
  artifact_viewed: "Evidence viewed",
  risk_scored: "Risk scored",
  application_created: "Application created",
  artifact_uploaded: "Artifact uploaded",
};

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

/** Tamper-evident action history for this application — every decision and
 * evidence access, timestamped and attributed. */
export function AuditTrailCard({ applicationId }: { applicationId: string }) {
  const { data: entries, isLoading } = useAuditTrail(applicationId);

  if (isLoading) return <Skeleton className="h-32 w-full" />;
  if (!entries || entries.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <History className="size-4" />
          Audit trail
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {entries.map((entry) => (
          <div key={entry.id} className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">
              {ACTION_LABEL[entry.action] ?? entry.action}
            </span>
            <span className="text-muted-foreground">{formatTime(entry.created_at)}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
