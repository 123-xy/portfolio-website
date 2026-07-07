import { AuthGuard } from "@/features/auth/components/auth-guard";

/**
 * Applicant persona group. Client-side auth guard redirects unauthenticated
 * users to /login; the backend independently enforces RBAC on every request.
 */
export default function ApplicantLayout({ children }: { children: React.ReactNode }) {
  return <AuthGuard>{children}</AuthGuard>;
}
