import { z } from "zod";

export const analyticsSummarySchema = z.object({
  total_applications: z.number(),
  status_counts: z.record(z.string(), z.number()),
  approved_count: z.number(),
  rejected_count: z.number(),
  approval_rate: z.number().nullable(),
  risk_band_counts: z.record(z.string(), z.number()),
  average_risk_score: z.number().nullable(),
  average_confidence: z.number().nullable(),
  average_decision_seconds: z.number().nullable(),
});
export type AnalyticsSummary = z.infer<typeof analyticsSummarySchema>;
