import type { Metadata } from "next";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { OfficerReviewDetail } from "@/features/officer-review/components/officer-review-detail";

export const metadata: Metadata = { title: "Review application" };

export default async function OfficerReviewPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <AppShell title="Review" subtitle="Evidence & decision" showBack>
      <OfficerReviewDetail applicationId={id} />
    </AppShell>
  );
}
