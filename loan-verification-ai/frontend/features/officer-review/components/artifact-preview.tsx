"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { ImageOff, Loader2 } from "lucide-react";
import { getArtifactDownloadUrl } from "@/features/officer-review/api/officer-review-api";
import type { ArtifactDto } from "@/features/applications/domain/schemas";

interface ArtifactPreviewProps {
  applicationId: string;
  artifact: ArtifactDto;
  label: string;
}

/** Fetches a short-lived presigned URL on demand and renders the artifact as
 * an image or video. Every render issues an audit-on-read log entry
 * server-side — evidence access is traceable, not just upload. */
export function ArtifactPreview({ applicationId, artifact, label }: ArtifactPreviewProps) {
  const { data: url, isLoading, isError } = useQuery({
    queryKey: ["officer-review", "artifact-url", applicationId, artifact.id],
    queryFn: () => getArtifactDownloadUrl(applicationId, artifact.id),
    staleTime: 4 * 60 * 1000, // presigned URLs are short-lived; refetch before they'd expire
  });

  const isVideo = artifact.kind === "verification_video";

  return (
    <div className="space-y-1.5">
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <div className="flex aspect-[4/3] items-center justify-center overflow-hidden rounded-xl bg-secondary">
        {isLoading ? (
          <Loader2 className="size-6 animate-spin text-muted-foreground" />
        ) : isError || !url ? (
          <ImageOff className="size-6 text-muted-foreground" />
        ) : isVideo ? (
          // eslint-disable-next-line jsx-a11y/media-has-caption
          <video controls src={url} className="size-full object-cover" />
        ) : (
          // Presigned S3/MinIO URLs are dynamic and short-lived — not a fit for
          // next/image's static optimization pipeline.
          // eslint-disable-next-line @next/next/no-img-element
          <img src={url} alt={label} className="size-full object-cover" />
        )}
      </div>
    </div>
  );
}
