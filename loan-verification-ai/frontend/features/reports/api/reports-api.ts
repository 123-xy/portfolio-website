import { apiClient } from "@/shared/lib/api-client";
import { reportSchema, type Report, type ReportFormat } from "@/features/reports/domain/schemas";

export async function generateApplicationReport(
  applicationId: string,
  format: ReportFormat,
): Promise<Report> {
  const raw = await apiClient.post(`/applications/${applicationId}/reports`, { format });
  return reportSchema.parse(raw);
}

export async function generateBulkExport(format: ReportFormat): Promise<Report> {
  const raw = await apiClient.post("/reports/bulk", { format });
  return reportSchema.parse(raw);
}

export async function getReportDownloadUrl(reportId: string): Promise<Report> {
  const raw = await apiClient.get(`/reports/${reportId}/download`);
  return reportSchema.parse(raw);
}
