import { apiClient } from "@/shared/lib/api-client";
import {
  applicationDetailSchema,
  applicationSummarySchema,
  initUploadResponseSchema,
  type ApplicationDetail,
  type ApplicationSummaryDto,
  type ArtifactKind,
  type CreateApplicationInput,
} from "@/features/applications/domain/schemas";
import { z } from "zod";

export async function listApplications(): Promise<ApplicationSummaryDto[]> {
  const raw = await apiClient.get("/applications");
  return z.array(applicationSummarySchema).parse(raw);
}

export async function getApplication(id: string): Promise<ApplicationDetail> {
  const raw = await apiClient.get(`/applications/${id}`);
  return applicationDetailSchema.parse(raw);
}

export async function createApplication(
  input: CreateApplicationInput,
): Promise<ApplicationDetail> {
  const raw = await apiClient.post("/applications", {
    loan_amount: input.loanAmount.toFixed(2),
    loan_purpose: input.loanPurpose || null,
    co_applicant: {
      full_name: input.coApplicantName,
      relationship: input.coApplicantRelationship || null,
    },
  });
  return applicationDetailSchema.parse(raw);
}

export async function submitApplication(id: string): Promise<ApplicationDetail> {
  const raw = await apiClient.post(`/applications/${id}/submit`);
  return applicationDetailSchema.parse(raw);
}

/**
 * Upload one artifact end to end: ask the API for a presigned URL, PUT the file
 * bytes directly to storage (bypassing our API), then confirm so the server
 * verifies the object landed. Returns nothing; callers refetch the application.
 */
export async function uploadArtifact(
  applicationId: string,
  kind: ArtifactKind,
  file: File,
): Promise<void> {
  const initRaw = await apiClient.post(`/applications/${applicationId}/uploads/init`, {
    kind,
    content_type: file.type,
    filename: file.name,
  });
  const init = initUploadResponseSchema.parse(initRaw);

  if (file.size > init.max_size_bytes) {
    throw new Error("File is larger than the allowed size for this upload.");
  }

  const put = await fetch(init.upload_url, {
    method: "PUT",
    headers: { "Content-Type": file.type },
    body: file,
  });
  if (!put.ok) {
    throw new Error("Upload to storage failed. Please retry.");
  }

  await apiClient.post(`/applications/${applicationId}/uploads/confirm`, {
    artifact_id: init.artifact_id,
  });
}
