import type { Metadata } from "next";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { ApplicationDetail } from "@/features/applications/components/application-detail";

export const metadata: Metadata = { title: "Application" };

export default async function ApplicationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <AppShell title="Application" subtitle="Upload & submit" showBack>
      <ApplicationDetail applicationId={id} />
    </AppShell>
  );
}
