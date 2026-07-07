/**
 * Applicant persona group. Kept as a passthrough for now; role-based route
 * protection (redirect unauthenticated/unauthorized users) is added with the
 * auth middleware in Phase 7. Pages compose their own AppShell with the
 * applicant bottom-nav.
 */
export default function ApplicantLayout({ children }: { children: React.ReactNode }) {
  return children;
}
