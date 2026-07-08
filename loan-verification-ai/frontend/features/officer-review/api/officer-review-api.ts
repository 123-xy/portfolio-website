import { apiClient } from "@/shared/lib/api-client";
import {
  artifactDownloadSchema,
  auditEntrySchema,
  decisionResponseSchema,
  verificationDetailsSchema,
  type AuditEntry,
  type Decision,
  type DecisionResponse,
  type VerificationDetails,
} from "@/features/officer-review/domain/schemas";
import { z } from "zod";

export async function getVerificationDetails(applicationId: string): Promise<VerificationDetails> {
  const raw = await apiClient.get(`/applications/${applicationId}/verification`);
  return verificationDetailsSchema.parse(raw);
}

export async function getArtifactDownloadUrl(
  applicationId: string,
  artifactId: string,
): Promise<string> {
  const raw = await apiClient.get(
    `/applications/${applicationId}/artifacts/${artifactId}/download`,
  );
  return artifactDownloadSchema.parse(raw).download_url;
}

export async function recordDecision(
  applicationId: string,
  decision: Decision,
  reason: string,
): Promise<DecisionResponse> {
  const raw = await apiClient.post(`/applications/${applicationId}/decision`, {
    decision,
    reason,
  });
  return decisionResponseSchema.parse(raw);
}

export async function getAuditTrail(applicationId: string): Promise<AuditEntry[]> {
  const raw = await apiClient.get(`/applications/${applicationId}/audit`);
  return z.array(auditEntrySchema).parse(raw);
}
