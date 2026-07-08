"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  getAuditTrail,
  getVerificationDetails,
  recordDecision,
} from "@/features/officer-review/api/officer-review-api";
import type { Decision } from "@/features/officer-review/domain/schemas";
import { isAuthenticated } from "@/shared/lib/auth-tokens";

export function useVerificationDetails(applicationId: string) {
  return useQuery({
    queryKey: ["officer-review", "verification", applicationId],
    queryFn: () => getVerificationDetails(applicationId),
    enabled: isAuthenticated() && Boolean(applicationId),
  });
}

export function useAuditTrail(applicationId: string) {
  return useQuery({
    queryKey: ["officer-review", "audit", applicationId],
    queryFn: () => getAuditTrail(applicationId),
    enabled: isAuthenticated() && Boolean(applicationId),
  });
}

export function useRecordDecision(applicationId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ decision, reason }: { decision: Decision; reason: string }) =>
      recordDecision(applicationId, decision, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications", applicationId] });
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      queryClient.invalidateQueries({ queryKey: ["officer-review", "audit", applicationId] });
    },
  });
}
