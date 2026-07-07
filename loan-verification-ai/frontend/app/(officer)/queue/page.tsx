import type { Metadata } from "next";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { ThemeToggle } from "@/shared/ui/theme-toggle";
import { ApplicationCard } from "@/features/applications/components/application-card";
import { DEMO_APPLICATIONS } from "@/features/applications/api/fixtures";

export const metadata: Metadata = { title: "Verification queue" };

export default function QueuePage() {
  // Officers act on applications awaiting review; Phase 11 adds decision actions.
  const queue = DEMO_APPLICATIONS.filter(
    (a) => a.status === "pending_review" || a.status === "needs_attention",
  );

  return (
    <AppShell
      title="Verification queue"
      subtitle={`${queue.length} awaiting review`}
      nav="officer"
      action={<ThemeToggle />}
    >
      <div className="space-y-3">
        {queue.map((application) => (
          <ApplicationCard key={application.id} application={application} />
        ))}
      </div>
    </AppShell>
  );
}
