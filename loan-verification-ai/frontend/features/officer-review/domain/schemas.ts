import { z } from "zod";

export const DECISIONS = ["approve", "reject", "request_more_info"] as const;
export type Decision = (typeof DECISIONS)[number];

export const verificationDetailsSchema = z.object({
  face_similarity: z.number().nullable(),
  face_confidence: z.number().nullable(),
  transcript_text: z.string().nullable(),
  transcript_language: z.string().nullable(),
  transcript_confidence: z.number().nullable(),
  consent_status: z.string().nullable(),
  consent_confidence: z.number().nullable(),
  consent_matched_phrases: z.array(z.string()),
  intent_aligned: z.boolean().nullable(),
  intent_confidence: z.number().nullable(),
  intent_label: z.string().nullable(),
  intent_reasons: z.array(z.string()),
  fraud_score: z.number().nullable(),
  fraud_confidence: z.number().nullable(),
  fraud_signals: z.array(z.string()),
});
export type VerificationDetails = z.infer<typeof verificationDetailsSchema>;

export const artifactDownloadSchema = z.object({
  download_url: z.string(),
});

export const decisionResponseSchema = z.object({
  id: z.string(),
  decision: z.enum(DECISIONS),
  reason: z.string(),
  created_at: z.string(),
});
export type DecisionResponse = z.infer<typeof decisionResponseSchema>;

export const auditEntrySchema = z.object({
  id: z.string(),
  action: z.string(),
  actor_user_id: z.string().nullable(),
  is_system: z.boolean(),
  target_type: z.string().nullable(),
  target_id: z.string().nullable(),
  metadata: z.record(z.string(), z.unknown()).nullable(),
  created_at: z.string(),
});
export type AuditEntry = z.infer<typeof auditEntrySchema>;
