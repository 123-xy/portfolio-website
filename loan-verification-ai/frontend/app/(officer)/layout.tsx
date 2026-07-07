import { AuthGuard } from "@/features/auth/components/auth-guard";

/**
 * Officer persona group. Client-side auth guard redirects unauthenticated
 * users to /login; the backend independently enforces RBAC on every request.
 * The full officer review workflow lands in Phase 11.
 */
export default function OfficerLayout({ children }: { children: React.ReactNode }) {
  return <AuthGuard>{children}</AuthGuard>;
}
