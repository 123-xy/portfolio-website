import { z } from "zod";

export const REPORT_FORMATS = ["pdf", "json", "csv"] as const;
export type ReportFormat = (typeof REPORT_FORMATS)[number];

export const reportSchema = z.object({
  id: z.string(),
  application_id: z.string().nullable(),
  format: z.enum(REPORT_FORMATS),
  version: z.number(),
  created_at: z.string(),
  download_url: z.string().nullable(),
});
export type Report = z.infer<typeof reportSchema>;
