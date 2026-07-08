import type { Metadata } from "next";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { CreateApplicationForm } from "@/features/applications/components/create-application-form";

export const metadata: Metadata = { title: "New verification" };

export default function NewApplicationPage() {
  return (
    <AppShell title="New verification" subtitle="Step 1 — application details" showBack>
      <div className="space-y-6">
        <p className="text-sm text-muted-foreground">
          Enter the loan and co-applicant details. Next you&apos;ll upload the
          photos and verification video, then submit for AI verification.
        </p>
        <CreateApplicationForm />
      </div>
    </AppShell>
  );
}
