import type { BadgeProps } from "@/shared/ui/badge";

/** Application lifecycle statuses — mirrors the backend `application_status` enum (Phase 3). */
export type ApplicationStatus =
  | "draft"
  | "submitted"
  | "processing"
  | "pending_review"
  | "needs_attention"
  | "more_info_requested"
  | "approved"
  | "rejected";

interface StatusMeta {
  label: string;
  variant: NonNullable<BadgeProps["variant"]>;
}

/** Presentation metadata for each status: label + badge variant. */
export const STATUS_META: Record<ApplicationStatus, StatusMeta> = {
  draft: { label: "Draft", variant: "outline" },
  submitted: { label: "Submitted", variant: "default" },
  processing: { label: "Processing", variant: "primary" },
  pending_review: { label: "In review", variant: "warning" },
  needs_attention: { label: "Needs attention", variant: "destructive" },
  more_info_requested: { label: "More info", variant: "warning" },
  approved: { label: "Approved", variant: "success" },
  rejected: { label: "Rejected", variant: "destructive" },
};

export type RiskBand = "low" | "medium" | "high";

export const RISK_META: Record<RiskBand, { label: string; variant: NonNullable<BadgeProps["variant"]> }> = {
  low: { label: "Low risk", variant: "success" },
  medium: { label: "Medium risk", variant: "warning" },
  high: { label: "High risk", variant: "destructive" },
};
