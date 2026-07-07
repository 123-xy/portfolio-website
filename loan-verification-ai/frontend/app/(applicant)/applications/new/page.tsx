import type { Metadata } from "next";
import { FileText, ScanFace, Upload, Video } from "lucide-react";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { Card, CardContent } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";

export const metadata: Metadata = { title: "New verification" };

// The upload flow (presigned direct-to-storage) is implemented in Phase 8.
// This screen establishes the step layout the flow will fill in.
const steps = [
  { icon: ScanFace, title: "Applicant photo", desc: "A clear photo of the primary applicant" },
  { icon: ScanFace, title: "Co-applicant photo", desc: "A clear photo of the co-applicant" },
  { icon: Video, title: "Verification video", desc: "Co-applicant states consent on camera" },
  { icon: FileText, title: "Documents", desc: "KYC and supporting documents" },
];

export default function NewApplicationPage() {
  return (
    <AppShell title="New verification" subtitle="Step 1 of 4" showBack>
      <div className="space-y-6">
        <p className="text-sm text-muted-foreground">
          Provide the artifacts below. Each is uploaded securely and processed by
          the AI verification pipeline before an officer reviews the result.
        </p>

        <div className="space-y-3">
          {steps.map(({ icon: Icon, title, desc }) => (
            <Card key={title}>
              <CardContent className="flex items-center gap-4 p-4">
                <div className="flex size-11 items-center justify-center rounded-xl bg-accent text-accent-foreground">
                  <Icon className="size-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-medium">{title}</p>
                  <p className="truncate text-xs text-muted-foreground">{desc}</p>
                </div>
                <Upload className="size-5 text-muted-foreground" />
              </CardContent>
            </Card>
          ))}
        </div>

        <Button size="full" disabled>
          Continue — available in Phase 8
        </Button>
      </div>
    </AppShell>
  );
}
