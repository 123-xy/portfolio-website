import type { Metadata } from "next";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { ThemeToggle } from "@/shared/ui/theme-toggle";
import { AnalyticsDashboard } from "@/features/analytics/components/analytics-dashboard";
import { BulkExportButton } from "@/features/reports/components/bulk-export-button";

export const metadata: Metadata = { title: "Analytics" };

export default function AnalyticsPage() {
  return (
    <AppShell title="Analytics" nav="officer" action={<ThemeToggle />}>
      <div className="space-y-6">
        <AnalyticsDashboard />
        <BulkExportButton />
      </div>
    </AppShell>
  );
}
