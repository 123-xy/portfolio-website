"use client";

import * as React from "react";
import { Download, Loader2, TableProperties } from "lucide-react";
import { useGenerateBulkExport } from "@/features/reports/hooks/use-reports";
import type { ReportFormat } from "@/features/reports/domain/schemas";
import { Button } from "@/shared/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";

const FORMAT_LABEL: Record<Exclude<ReportFormat, "pdf">, string> = { csv: "CSV", json: "JSON" };

/** Compliance export of every application (reference, status, risk band,
 * dates) — staff-only, audit-logged, CSV/JSON only (PDF isn't meaningful for
 * a tabular bulk record). */
export function BulkExportButton() {
  const [error, setError] = React.useState<string | null>(null);
  const generate = useGenerateBulkExport();

  async function onExport(format: Exclude<ReportFormat, "pdf">) {
    setError(null);
    try {
      const report = await generate.mutateAsync(format);
      if (report.download_url) {
        window.open(report.download_url, "_blank", "noopener,noreferrer");
      }
    } catch {
      setError("Couldn't generate the export. Please try again.");
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TableProperties className="size-4" />
          Bulk export
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground">
          Export every application's status, risk band, and timeline for compliance review.
        </p>
        {error ? (
          <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">{error}</p>
        ) : null}
        <div className="grid grid-cols-2 gap-2">
          {(["csv", "json"] as const).map((format) => (
            <Button
              key={format}
              variant="outline"
              size="sm"
              disabled={generate.isPending}
              onClick={() => onExport(format)}
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
