import type { ApplicationSummary } from "@/features/applications/components/application-card";

/**
 * Placeholder data so the UI is demonstrable before the backend exists. These
 * are replaced by real TanStack Query hooks against /api/v1/applications in
 * Phase 8. Kept in one file so the swap is a single deletion.
 */
export const DEMO_APPLICATIONS: ApplicationSummary[] = [
  {
    id: "a1f3d2e4-0000-4000-8000-000000000001",
    referenceNo: "APP-2026-000318",
    coApplicantName: "Priya Sharma",
    loanAmount: 4500000,
    status: "approved",
    riskBand: "low",
    updatedAt: "2026-07-06T09:12:00Z",
  },
  {
    id: "a1f3d2e4-0000-4000-8000-000000000002",
    referenceNo: "APP-2026-000317",
    coApplicantName: "Rahul Verma",
    loanAmount: 1200000,
    status: "pending_review",
    riskBand: "medium",
    updatedAt: "2026-07-07T06:40:00Z",
  },
  {
    id: "a1f3d2e4-0000-4000-8000-000000000003",
    referenceNo: "APP-2026-000316",
    coApplicantName: "Aisha Khan",
    loanAmount: 800000,
    status: "processing",
    updatedAt: "2026-07-07T07:05:00Z",
  },
  {
    id: "a1f3d2e4-0000-4000-8000-000000000004",
    referenceNo: "APP-2026-000311",
    coApplicantName: "Vikram Nair",
    loanAmount: 2600000,
    status: "needs_attention",
    riskBand: "high",
    updatedAt: "2026-07-05T15:30:00Z",
  },
];
