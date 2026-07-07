/**
 * Officer persona group. Passthrough for now; role-gated route protection is
 * added with the auth middleware in Phase 7. The full officer review workflow
 * lands in Phase 11 and analytics in Phase 12.
 */
export default function OfficerLayout({ children }: { children: React.ReactNode }) {
  return children;
}
