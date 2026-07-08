"use client";

import Link from "next/link";
import { CheckCircle2, Clock, FileCheck2, Plus } from "lucide-react";
import { useApplications } from "@/features/applications/hooks/use-applications";
import { ApplicationList } from "@/features/applications/components/application-list";
import { Card, CardContent } from "@/shared/ui/card";

const IN_REVIEW = new Set(["submitted", "processing", "pending_review", "needs_attention"]);

export function DashboardOverview() {
  const { data } = useApplications();
  const apps = data ?? [];

  const stats = [
    { label: "Total", value: apps.length, icon: FileCheck2 },
    {
      label: "In review",
      value: apps.filter((a) => IN_REVIEW.has(a.status)).length,
      icon: Clock,
    },
    {
      label: "Approved",
      value: apps.filter((a) => a.status === "approved").length,
      icon: CheckCircle2,
    },
  ];

  return (
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

      {/* Stat tiles (computed from the applicant's real applications) */}
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
        <ApplicationList limit={3} />
      </section>
    </div>
  );
}
