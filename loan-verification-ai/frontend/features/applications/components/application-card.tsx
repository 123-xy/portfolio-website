import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Card } from "@/shared/ui/card";
import {
  RISK_META,
  STATUS_META,
  type ApplicationStatus,
  type RiskBand,
} from "@/features/applications/domain/status";

export interface ApplicationSummary {
  id: string;
  referenceNo: string;
  coApplicantName: string;
  loanAmount: number;
  status: ApplicationStatus;
  riskBand?: RiskBand;
  updatedAt: string;
}

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

/** Tappable application row — the list primitive on Home and Applications. */
export function ApplicationCard({ application }: { application: ApplicationSummary }) {
  const status = STATUS_META[application.status];
  return (
    <Link href={`/applications/${application.id}`} className="block">
      <Card className="flex items-center gap-3 p-4 transition-colors active:bg-accent/60">
        <div className="min-w-0 flex-1 space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="truncate font-semibold">{application.coApplicantName}</span>
            {application.riskBand ? (
              <Badge variant={RISK_META[application.riskBand].variant}>
                {RISK_META[application.riskBand].label}
              </Badge>
            ) : null}
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>{application.referenceNo}</span>
            <span aria-hidden>•</span>
            <span>{currency.format(application.loanAmount)}</span>
          </div>
        </div>
        <Badge variant={status.variant}>{status.label}</Badge>
        <ChevronRight className="size-5 shrink-0 text-muted-foreground" />
      </Card>
    </Link>
  );
}
