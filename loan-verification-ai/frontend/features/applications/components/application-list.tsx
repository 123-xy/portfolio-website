"use client";

import Link from "next/link";
import { FileText, Plus } from "lucide-react";
import { useApplications } from "@/features/applications/hooks/use-applications";
import { ApplicationCard } from "@/features/applications/components/application-card";
import { Skeleton } from "@/shared/ui/skeleton";
import { buttonVariants } from "@/shared/ui/button";

interface ApplicationListProps {
  /** Cap the number shown (e.g. the dashboard's recent list). */
  limit?: number;
  /** Show a create button in the empty state (applicants only). */
  showCreate?: boolean;
}

export function ApplicationList({ limit, showCreate = true }: ApplicationListProps) {
  const { data, isLoading, isError } = useApplications();

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: limit ?? 3 }).map((_, i) => (
          <Skeleton key={i} className="h-[76px] w-full" />
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <p className="rounded-xl bg-destructive/10 px-4 py-3 text-sm text-destructive">
        Couldn&apos;t load applications. Please try again.
      </p>
    );
  }

  const items = limit ? (data ?? []).slice(0, limit) : (data ?? []);

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-border py-10 text-center">
        <div className="flex size-12 items-center justify-center rounded-2xl bg-accent text-accent-foreground">
          <FileText className="size-6" />
        </div>
        <p className="text-sm text-muted-foreground">No applications yet.</p>
        {showCreate ? (
          <Link href="/applications/new" className={buttonVariants({ size: "sm" })}>
            <Plus className="size-4" />
            New verification
          </Link>
        ) : null}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {items.map((application) => (
        <ApplicationCard key={application.id} application={application} />
      ))}
    </div>
  );
}
