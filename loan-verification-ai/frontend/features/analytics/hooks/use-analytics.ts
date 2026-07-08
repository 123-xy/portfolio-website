"use client";

import { useQuery } from "@tanstack/react-query";
import { getAnalyticsSummary } from "@/features/analytics/api/analytics-api";
import { isAuthenticated } from "@/shared/lib/auth-tokens";

export function useAnalyticsSummary() {
  return useQuery({
    queryKey: ["analytics", "summary"],
    queryFn: getAnalyticsSummary,
    enabled: isAuthenticated(),
    staleTime: 30 * 1000,
  });
}
