import type { Metadata } from "next";
import Link from "next/link";
import { Bell, Plus, ScanFace, ShieldCheck, TrendingUp } from "lucide-react";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { ThemeToggle } from "@/shared/ui/theme-toggle";
import { Button } from "@/shared/ui/button";
import { Card, CardContent } from "@/shared/ui/card";
import { ApplicationCard } from "@/features/applications/components/application-card";
import { DEMO_APPLICATIONS } from "@/features/applications/api/fixtures";

export const metadata: Metadata = { title: "Home" };

const stats = [
  { label: "Verified", value: "128", icon: ShieldCheck },
  { label: "In review", value: "6", icon: ScanFace },
  { label: "Avg. confidence", value: "94%", icon: TrendingUp },
];

export default function DashboardPage() {
  const recent = DEMO_APPLICATIONS.slice(0, 3);

  return (
    <AppShell
      title="Good morning"
      subtitle="Here's your verification overview"
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
      <div className="space-y-6">
        {/* Hero CTA */}
        <Card className="overflow-hidden border-0 bg-primary text-primary-foreground shadow-lg">
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex-1 space-y-1">
              <p className="text-sm/relaxed opacity-90">Start a new</p>
              <p className="text-xl font-bold">Co-applicant verification</p>
            </div>
            <Link
              href="/applications/new"
              aria-label="New verification"
              className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-primary-foreground/15 backdrop-blur transition active:scale-95"
            >
              <Plus className="size-7" />
            </Link>
          </CardContent>
        </Card>

        {/* Stat tiles */}
        <div className="grid grid-cols-3 gap-3">
          {stats.map(({ label, value, icon: Icon }) => (
            <Card key={label} className="p-3">
              <Icon className="size-5 text-primary" />
              <p className="mt-2 text-lg font-bold leading-none">{value}</p>
              <p className="mt-1 text-[11px] text-muted-foreground">{label}</p>
            </Card>
          ))}
        </div>

        {/* Recent applications */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Recent applications</h2>
            <Link href="/applications" className="text-xs font-semibold text-primary">
              View all
            </Link>
          </div>
          <div className="space-y-3">
            {recent.map((application) => (
              <ApplicationCard key={application.id} application={application} />
            ))}
          </div>
        </section>
      </div>
    </AppShell>
  );
}
