import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";
import { STATUS_META } from "@/features/applications/domain/status";
import type { ApplicationSummaryDto } from "@/features/applications/domain/schemas";

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

/** Tappable application row — the list primitive on Home, Applications, Queue. */
export function ApplicationCard({ application }: { application: ApplicationSummaryDto }) {
  const status = STATUS_META[application.status];
  return (
    <Link href={`/applications/${application.id}`} className="block">
      <Card className="flex items-center gap-3 p-4 transition-colors active:bg-accent/60">
        <div className="min-w-0 flex-1 space-y-1.5">
          <span className="block truncate font-semibold">
            {application.co_applicant_name ?? "Co-applicant"}
          </span>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>{application.reference_no}</span>
            <span aria-hidden>•</span>
            <span>{currency.format(application.loan_amount)}</span>
          </div>
        </div>
        <Badge variant={status.variant}>{status.label}</Badge>
        <ChevronRight className="size-5 shrink-0 text-muted-foreground" />
      </Card>
    </Link>
  );
}
