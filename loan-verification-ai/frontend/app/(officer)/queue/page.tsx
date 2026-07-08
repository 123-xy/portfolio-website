import type { Metadata } from "next";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { ThemeToggle } from "@/shared/ui/theme-toggle";
import { ApplicationList } from "@/features/applications/components/application-list";

export const metadata: Metadata = { title: "Verification queue" };

export default function QueuePage() {
  // For officers, the applications list endpoint returns the review queue.
  return (
    <AppShell title="Verification queue" nav="officer" action={<ThemeToggle />}>
      <ApplicationList showCreate={false} hrefBase="/review" />
    </AppShell>
  );
}
