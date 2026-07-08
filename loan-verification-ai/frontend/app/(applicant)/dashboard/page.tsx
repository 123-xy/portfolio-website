import type { Metadata } from "next";
import { Bell } from "lucide-react";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { ThemeToggle } from "@/shared/ui/theme-toggle";
import { Button } from "@/shared/ui/button";
import { DashboardOverview } from "@/features/applications/components/dashboard-overview";

export const metadata: Metadata = { title: "Home" };

export default function DashboardPage() {
  return (
    <AppShell
      title="Welcome back"
      subtitle="Your verification overview"
      nav="applicant"
      action={
        <>
          <Button variant="ghost" size="icon" aria-label="Notifications">
            <Bell />
          </Button>
          <ThemeToggle />
        </>
      }
    >
      <DashboardOverview />
    </AppShell>
  );
}
