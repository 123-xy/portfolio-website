import * as React from "react";
import { AppBar } from "@/shared/ui/shell/app-bar";
import { BottomNav } from "@/shared/ui/shell/bottom-nav";
import { PageTransition } from "@/shared/ui/shell/page-transition";
import type { Persona } from "@/shared/ui/shell/navigation";

interface AppShellProps {
  title: string;
  subtitle?: string;
  showBack?: boolean;
  action?: React.ReactNode;
  /** When provided, renders the fixed bottom tab bar for this persona. */
  nav?: Persona;
  children: React.ReactNode;
}

/**
 * The screen chrome every authenticated page composes: top app bar, a
 * scrollable content region, and (optionally) the bottom tab bar. Content
 * scrolls between the two fixed bars — the classic mobile app layout.
 */
export function AppShell({ title, subtitle, showBack, action, nav, children }: AppShellProps) {
  return (
    <div className="flex min-h-dvh flex-col">
      <AppBar title={title} subtitle={subtitle} showBack={showBack} action={action} />
      <main className="no-scrollbar flex-1 overflow-y-auto px-4 py-4">
        <PageTransition>{children}</PageTransition>
      </main>
      {nav ? <BottomNav persona={nav} /> : null}
    </div>
  );
}
