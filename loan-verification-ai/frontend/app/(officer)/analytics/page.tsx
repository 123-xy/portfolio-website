import type { Metadata } from "next";
import { CheckCircle2, Clock, TrendingUp, XCircle } from "lucide-react";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { ThemeToggle } from "@/shared/ui/theme-toggle";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";

export const metadata: Metadata = { title: "Analytics" };

// Live charts (risk trends, SLA) arrive in Phase 12; these tiles establish the layout.
const kpis = [
  { label: "Approved", value: "1,204", icon: CheckCircle2, tone: "text-success" },
  { label: "Rejected", value: "86", icon: XCircle, tone: "text-destructive" },
  { label: "Avg. decision", value: "3.2m", icon: Clock, tone: "text-primary" },
  { label: "Avg. confidence", value: "94%", icon: TrendingUp, tone: "text-primary" },
];

export default function AnalyticsPage() {
  return (
    <AppShell title="Analytics" nav="officer" action={<ThemeToggle />}>
      <div className="space-y-6">
        <div className="grid grid-cols-2 gap-3">
          {kpis.map(({ label, value, icon: Icon, tone }) => (
            <Card key={label} className="p-4">
              <Icon className={`size-5 ${tone}`} />
              <p className="mt-2 text-2xl font-bold leading-none">{value}</p>
              <p className="mt-1 text-xs text-muted-foreground">{label}</p>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Risk trend</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Interactive risk-trend and approval-rate charts render here in Phase 12.
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
