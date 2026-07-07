import { z } from "zod";
import { apiClient } from "@/shared/lib/api-client";
import { setTokens, clearTokens, getRefreshToken } from "@/shared/lib/auth-tokens";
import { authUserSchema, type AuthUser, userRoleSchema } from "@/features/auth/domain/schemas";

// Backend responses are snake_case; parse-and-map to the app's camelCase shape
// at this boundary so the rest of the UI never sees wire formatting.
const tokenResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
});

const userResponseSchema = z.object({
  id: z.string(),
  email: z.string(),
  full_name: z.string(),
  role: userRoleSchema,
});

function persist(raw: unknown): void {
  const parsed = tokenResponseSchema.parse(raw);
  setTokens({ accessToken: parsed.access_token, refreshToken: parsed.refresh_token });
}

export async function register(input: {
  email: string;
  fullName: string;
  password: string;
}): Promise<void> {
  const raw = await apiClient.post(
    "/auth/register",
    { email: input.email, full_name: input.fullName, password: input.password },
    { skipAuth: true },
  );
  persist(raw);
}

export async function login(input: { email: string; password: string }): Promise<void> {
  const raw = await apiClient.post("/auth/login", input, { skipAuth: true });
  persist(raw);
}

export async function logout(): Promise<void> {
  const refreshToken = getRefreshToken();
  try {
    if (refreshToken) {
      await apiClient.post("/auth/logout", { refresh_token: refreshToken }, { skipAuth: true });
    }
  } finally {
    // Always clear locally, even if the server call fails — the user intends
    // to end the session regardless.
    clearTokens();
  }
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  const raw = await apiClient.get("/auth/me");
  const parsed = userResponseSchema.parse(raw);
  return authUserSchema.parse({
    id: parsed.id,
    email: parsed.email,
    fullName: parsed.full_name,
    role: parsed.role,
  });
}
