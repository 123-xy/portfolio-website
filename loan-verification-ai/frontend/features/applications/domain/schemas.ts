import { z } from "zod";

export const APPLICATION_STATUSES = [
  "draft",
  "submitted",
  "processing",
  "pending_review",
  "needs_attention",
  "more_info_requested",
  "approved",
  "rejected",
] as const;

export const ARTIFACT_KINDS = [
  "applicant_photo",
  "coapplicant_photo",
  "verification_video",
  "document",
] as const;

export type ArtifactKind = (typeof ARTIFACT_KINDS)[number];

/** Kinds required before an application can be submitted (mirrors the backend). */
export const REQUIRED_KINDS: ArtifactKind[] = [
  "applicant_photo",
  "coapplicant_photo",
  "verification_video",
];

// --- Form input (create) ---
export const createApplicationSchema = z.object({
  loanAmount: z
    .number({ invalid_type_error: "Enter an amount" })
    .positive("Amount must be greater than zero"),
  loanPurpose: z.string().max(500).optional(),
  coApplicantName: z.string().min(2, "Enter the co-applicant's name"),
  coApplicantRelationship: z.string().max(100).optional(),
});
export type CreateApplicationInput = z.infer<typeof createApplicationSchema>;

// --- API response shapes (snake_case from backend), parsed at the boundary ---
export const artifactResponseSchema = z.object({
  id: z.string(),
  kind: z.enum(ARTIFACT_KINDS),
  status: z.string(),
  mime_type: z.string().nullable(),
  size_bytes: z.number().nullable(),
  original_filename: z.string().nullable(),
});

export const applicationSummarySchema = z.object({
  id: z.string(),
  reference_no: z.string(),
  loan_amount: z.coerce.number(),
  status: z.enum(APPLICATION_STATUSES),
  co_applicant_name: z.string().nullable(),
  submitted_at: z.string().nullable(),
  created_at: z.string().nullable(),
});

export const applicationDetailSchema = z.object({
  id: z.string(),
  reference_no: z.string(),
  loan_amount: z.coerce.number(),
  loan_purpose: z.string().nullable(),
  status: z.enum(APPLICATION_STATUSES),
  submitted_at: z.string().nullable(),
  created_at: z.string().nullable(),
  co_applicant: z
    .object({
      id: z.string(),
      full_name: z.string(),
      relationship: z.string().nullable(),
    })
    .nullable(),
  artifacts: z.array(artifactResponseSchema),
});

export const initUploadResponseSchema = z.object({
  artifact_id: z.string(),
  upload_url: z.string(),
  storage_key: z.string(),
  max_size_bytes: z.number(),
});

export type ApplicationDetail = z.infer<typeof applicationDetailSchema>;
export type ApplicationSummaryDto = z.infer<typeof applicationSummarySchema>;
export type ArtifactDto = z.infer<typeof artifactResponseSchema>;
