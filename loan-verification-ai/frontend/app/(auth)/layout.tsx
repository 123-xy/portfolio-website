import { ThemeToggle } from "@/shared/ui/theme-toggle";

/** Auth screens have no bottom nav — just a minimal top bar with theme toggle. */
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="safe-top flex min-h-dvh flex-col">
      <div className="flex justify-end px-3 pt-3">
        <ThemeToggle />
      </div>
      <div className="flex flex-1 flex-col justify-center px-6 pb-10">{children}</div>
    </div>
  );
}
