"use client";

import * as React from "react";
import { Check, Loader2, Upload } from "lucide-react";
import { useUploadArtifact } from "@/features/applications/hooks/use-applications";
import type { ArtifactKind } from "@/features/applications/domain/schemas";
import { Card, CardContent } from "@/shared/ui/card";

const ACCEPT: Record<ArtifactKind, string> = {
  applicant_photo: "image/jpeg,image/png",
  coapplicant_photo: "image/jpeg,image/png",
  verification_video: "video/mp4,video/webm,video/quicktime",
  document: "application/pdf,image/jpeg,image/png",
};

interface UploadRowProps {
  applicationId: string;
  kind: ArtifactKind;
  label: string;
  description: string;
  uploaded: boolean;
  disabled?: boolean;
}

/** One artifact slot: shows uploaded state, or a file picker that runs the
 * init → PUT-to-storage → confirm flow. */
export function UploadRow({
  applicationId,
  kind,
  label,
  description,
  uploaded,
  disabled,
}: UploadRowProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const upload = useUploadArtifact(applicationId);
  const [error, setError] = React.useState<string | null>(null);

  async function onPick(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = ""; // allow re-selecting the same file
    if (!file) return;
    setError(null);
    try {
      await upload.mutateAsync({ kind, file });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    }
  }

  const busy = upload.isPending;

  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-4">
        <div
          className={`flex size-11 items-center justify-center rounded-xl ${
            uploaded ? "bg-success/15 text-success" : "bg-accent text-accent-foreground"
          }`}
        >
          {uploaded ? <Check className="size-5" /> : <Upload className="size-5" />}
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-medium">{label}</p>
          <p className="truncate text-xs text-muted-foreground">
            {error ? <span className="text-destructive">{error}</span> : uploaded ? "Uploaded" : description}
          </p>
        </div>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={disabled || busy}
          className="rounded-lg px-3 py-1.5 text-sm font-semibold text-primary transition active:scale-95 disabled:opacity-40"
        >
          {busy ? <Loader2 className="size-4 animate-spin" /> : uploaded ? "Replace" : "Upload"}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT[kind]}
          hidden
          onChange={onPick}
        />
      </CardContent>
    </Card>
  );
}
