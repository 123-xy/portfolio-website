"use client";

import { CheckCircle2, Clock, ShieldAlert, TrendingUp, XCircle } from "lucide-react";
import { useAnalyticsSummary } from "@/features/analytics/hooks/use-analytics";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Skeleton } from "@/shared/ui/skeleton";
import { Badge } from "@/shared/ui/badge";

const STATUS_LABEL: Record<string, string> = {
  pending_review: "Pending review",
  approved: "Approved",
  rejected: "Rejected",
  processing: "Processing",
  draft: "Draft",
  submitted: "Submitted",
};

const RISK_BAND_VARIANT: Record<string, "success" | "warning" | "destructive" | "default"> = {
  low: "success",
  medium: "warning",
  high: "destructive",
};

function pct(value: number | null): string {
  return value === null ? "—" : `${Math.round(value * 100)}%`;
}

function seconds(value: number | null): string {
  if (value === null) return "—";
  if (value < 60) return `${Math.round(value)}s`;
  return `${(value / 60).toFixed(1)}m`;
}

export function AnalyticsDashboard() {
  const { data: summary, isLoading } = useAnalyticsSummary();

  if (isLoading || !summary) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  const kpis = [
    { label: "Approved", value: String(summary.approved_count), icon: CheckCircle2, tone: "text-success" },
    { label: "Rejected", value: String(summary.rejected_count), icon: XCircle, tone: "text-destructive" },
    { label: "Avg. decision", value: seconds(summary.average_decision_seconds), icon: Clock, tone: "text-primary" },
    { label: "Avg. confidence", value: pct(summary.average_confidence), icon: TrendingUp, tone: "text-primary" },
  ];

  const statusEntries = Object.entries(summary.status_counts);
  const riskEntries = Object.entries(summary.risk_band_counts);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3">
        {kpis.map(({ label, value, icon: Icon, tone }) => (
          <Card key={label} className="p-4">
            <Icon className={`size-5 ${tone}`} />
            <p className="mt-2 text-2xl font-bold leading-none">{value}</p>
            <p className="mt-1 text-xs text-muted-foreground">{label}</p>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Overview</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Total applications</span>
            <span className="font-medium">{summary.total_applications}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Approval rate</span>
            <span className="font-medium">{pct(summary.approval_rate)}</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>By status</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {statusEntries.length === 0 ? (
            <p className="text-sm text-muted-foreground">No applications yet.</p>
          ) : (
            statusEntries.map(([status, count]) => (
              <Badge key={status} variant="outline">
                {STATUS_LABEL[status] ?? status}: {count}
              </Badge>
            ))
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShieldAlert className="size-4" />
            Risk bands
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {riskEntries.length === 0 ? (
            <p className="text-sm text-muted-foreground">No scored applications yet.</p>
          ) : (
            riskEntries.map(([band, count]) => (
              <Badge key={band} variant={RISK_BAND_VARIANT[band] ?? "default"}>
                {band}: {count}
              </Badge>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
