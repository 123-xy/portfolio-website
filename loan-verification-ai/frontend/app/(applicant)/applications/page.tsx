import type { Metadata } from "next";
import Link from "next/link";
import { Plus } from "lucide-react";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { ThemeToggle } from "@/shared/ui/theme-toggle";
import { Button } from "@/shared/ui/button";
import { ApplicationList } from "@/features/applications/components/application-list";

export const metadata: Metadata = { title: "Applications" };

export default function ApplicationsPage() {
  return (
    <AppShell
      title="Applications"
      nav="applicant"
      action={
        <>
          <Link href="/applications/new" aria-label="New application">
            <Button variant="ghost" size="icon">
              <Plus />
            </Button>
          </Link>
          <ThemeToggle />
        </>
      }
    >
      <ApplicationList />
    </AppShell>
  );
}
