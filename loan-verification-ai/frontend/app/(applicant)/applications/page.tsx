import type { Metadata } from "next";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { ThemeToggle } from "@/shared/ui/theme-toggle";
import { ApplicationCard } from "@/features/applications/components/application-card";
import { DEMO_APPLICATIONS } from "@/features/applications/api/fixtures";

export const metadata: Metadata = { title: "Applications" };

export default function ApplicationsPage() {
  return (
    <AppShell
      title="Applications"
      subtitle={`${DEMO_APPLICATIONS.length} total`}
      nav="applicant"
      action={<ThemeToggle />}
    >
      <div className="space-y-3">
        {DEMO_APPLICATIONS.map((application) => (
          <ApplicationCard key={application.id} application={application} />
        ))}
      </div>
    </AppShell>
  );
}
