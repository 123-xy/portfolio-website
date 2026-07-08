import { apiClient } from "@/shared/lib/api-client";
import {
  analyticsSummarySchema,
  type AnalyticsSummary,
} from "@/features/analytics/domain/schemas";

export async function getAnalyticsSummary(): Promise<AnalyticsSummary> {
  const raw = await apiClient.get("/analytics");
  return analyticsSummarySchema.parse(raw);
}
