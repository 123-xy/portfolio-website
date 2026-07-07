import { z } from "zod";

/**
 * Public runtime configuration. Only NEXT_PUBLIC_* vars are available in the
 * browser; validated once here so a missing/misspelled var fails loudly at
 * startup rather than as an undefined at a fetch call site.
 */
const publicEnvSchema = z.object({
  NEXT_PUBLIC_API_BASE_URL: z.string().url().default("http://localhost:8000/api/v1"),
  NEXT_PUBLIC_APP_NAME: z.string().default("VerifyCo"),
});

export const env = publicEnvSchema.parse({
  NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
  NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
});
