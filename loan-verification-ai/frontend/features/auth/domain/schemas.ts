import { z } from "zod";

/**
 * Auth contracts. These Zod schemas are the single source of truth for both
 * form validation (React Hook Form resolver) and API response parsing, so a
 * backend contract drift fails at the boundary instead of rendering undefined.
 */
export const loginSchema = z.object({
  email: z.string().min(1, "Email is required").email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});
export type LoginInput = z.infer<typeof loginSchema>;

export const registerSchema = z
  .object({
    fullName: z.string().min(2, "Enter your full name"),
    email: z.string().email("Enter a valid email"),
    password: z
      .string()
      .min(8, "At least 8 characters")
      .regex(/[A-Z]/, "Include an uppercase letter")
      .regex(/[a-z]/, "Include a lowercase letter")
      .regex(/[0-9]/, "Include a number"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });
export type RegisterInput = z.infer<typeof registerSchema>;

export const userRoleSchema = z.enum(["admin", "officer", "applicant", "auditor"]);
export type UserRole = z.infer<typeof userRoleSchema>;

export const authTokensSchema = z.object({
  accessToken: z.string(),
  refreshToken: z.string(),
  tokenType: z.literal("bearer").default("bearer"),
});
export type AuthTokens = z.infer<typeof authTokensSchema>;

export const authUserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  fullName: z.string(),
  role: userRoleSchema,
});
export type AuthUser = z.infer<typeof authUserSchema>;
