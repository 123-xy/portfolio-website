"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createApplication,
  getApplication,
  listApplications,
  submitApplication,
  uploadArtifact,
} from "@/features/applications/api/applications-api";
import type { ArtifactKind, CreateApplicationInput } from "@/features/applications/domain/schemas";
import { isAuthenticated } from "@/shared/lib/auth-tokens";

const LIST_KEY = ["applications"] as const;
const detailKey = (id: string) => ["applications", id] as const;

export function useApplications() {
  return useQuery({
    queryKey: LIST_KEY,
    queryFn: listApplications,
    enabled: isAuthenticated(),
  });
}

export function useApplication(id: string) {
  return useQuery({
    queryKey: detailKey(id),
    queryFn: () => getApplication(id),
    enabled: isAuthenticated() && Boolean(id),
  });
}

export function useCreateApplication() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateApplicationInput) => createApplication(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: LIST_KEY }),
  });
}

export function useUploadArtifact(applicationId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ kind, file }: { kind: ArtifactKind; file: File }) =>
      uploadArtifact(applicationId, kind, file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: detailKey(applicationId) }),
  });
}

export function useSubmitApplication(applicationId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => submitApplication(applicationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: detailKey(applicationId) });
      queryClient.invalidateQueries({ queryKey: LIST_KEY });
    },
  });
}
