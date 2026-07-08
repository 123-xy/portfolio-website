"use client";

import * as React from "react";
import { Check, Loader2, MessageCircleQuestion, X } from "lucide-react";
import { useRecordDecision } from "@/features/officer-review/hooks/use-officer-review";
import type { Decision } from "@/features/officer-review/domain/schemas";
import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";

interface DecisionPanelProps {
  applicationId: string;
}

/**
 * Approve / reject / request-more-info, each requiring a reason. Decision
 * buttons stay disabled until the officer explicitly confirms they reviewed
 * the evidence — a deliberate anti-rubber-stamp UX gate (Phase 1 risk: a
 * decision made without reviewing evidence undermines the whole verification
 * process), not just a permission check.
 */
export function DecisionPanel({ applicationId }: DecisionPanelProps) {
  const [reviewed, setReviewed] = React.useState(false);
  const [reason, setReason] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState<Decision | null>(null);
  const decide = useRecordDecision(applicationId);

  const canDecide = reviewed && reason.trim().length > 0 && !decide.isPending;

  async function onDecide(decision: Decision) {
    setError(null);
    try {
      await decide.mutateAsync({ decision, reason: reason.trim() });
      setSuccess(decision);
    } catch {
      setError("Couldn't record the decision. Please try again.");
    }
  }

  if (success) {
    return (
      <Card>
        <CardContent className="p-5 text-sm text-muted-foreground">
          Decision recorded: <span className="font-medium text-foreground">{success}</span>.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Decision</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <label className="flex items-start gap-2 text-sm">
          <input
            type="checkbox"
            checked={reviewed}
            onChange={(e) => setReviewed(e.target.checked)}
            className="mt-0.5 size-4 shrink-0 rounded border-input accent-primary"
          />
          I have reviewed the photos, video, and transcript for this application.
        </label>

        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Reason for your decision (required)"
          rows={3}
          className="w-full rounded-xl border border-input bg-background px-4 py-3 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />

        {error ? (
          <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">{error}</p>
        ) : null}

        <div className="grid grid-cols-3 gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={!canDecide}
            onClick={() => onDecide("request_more_info")}
          >
            {decide.isPending ? <Loader2 className="animate-spin" /> : <MessageCircleQuestion />}
            More info
          </Button>
          <Button
            variant="destructive"
            size="sm"
            disabled={!canDecide}
            onClick={() => onDecide("reject")}
          >
            <X />
            Reject
          </Button>
          <Button size="sm" disabled={!canDecide} onClick={() => onDecide("approve")}>
            <Check />
            Approve
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
