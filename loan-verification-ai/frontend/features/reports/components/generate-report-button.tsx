"use client";

import * as React from "react";
import { Download, FileText, Loader2 } from "lucide-react";
import { useGenerateApplicationReport } from "@/features/reports/hooks/use-reports";
import type { ReportFormat } from "@/features/reports/domain/schemas";
import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";

const FORMAT_LABEL: Record<ReportFormat, string> = { pdf: "PDF", json: "JSON", csv: "CSV" };

/** Staff-only affordance to render and download an official verification
 * report for this application — combines loan details, risk assessment,
 * evidence summary, and full decision history in the officer's chosen
 * format. Every generation is audit-logged server-side. */
export function GenerateReportButton({ applicationId }: { applicationId: string }) {
  const [error, setError] = React.useState<string | null>(null);
  const generate = useGenerateApplicationReport(applicationId);

  async function onGenerate(format: ReportFormat) {
    setError(null);
    try {
      const report = await generate.mutateAsync(format);
      if (report.download_url) {
        window.open(report.download_url, "_blank", "noopener,noreferrer");
      }
    } catch {
      setError("Couldn't generate the report. Please try again.");
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="size-4" />
          Report
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {error ? (
          <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">{error}</p>
        ) : null}
        <div className="grid grid-cols-3 gap-2">
          {(["pdf", "json", "csv"] as const).map((format) => (
            <Button
              key={format}
              variant="outline"
              size="sm"
              disabled={generate.isPending}
              onClick={() => onGenerate(format)}
            >
              {generate.isPending && generate.variables === format ? (
                <Loader2 className="animate-spin" />
              ) : (
                <Download />
              )}
              {FORMAT_LABEL[format]}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
