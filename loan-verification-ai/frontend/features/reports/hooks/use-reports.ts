"use client";

import { useMutation } from "@tanstack/react-query";
import {
  generateApplicationReport,
  generateBulkExport,
} from "@/features/reports/api/reports-api";
import type { ReportFormat } from "@/features/reports/domain/schemas";

export function useGenerateApplicationReport(applicationId: string) {
  return useMutation({
    mutationFn: (format: ReportFormat) => generateApplicationReport(applicationId, format),
  });
}

export function useGenerateBulkExport() {
  return useMutation({
    mutationFn: (format: ReportFormat) => generateBulkExport(format),
  });
}
