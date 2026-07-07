"use client";

import * as React from "react";
import { Loader2 } from "lucide-react";
import { useAuthGuard } from "@/features/auth/hooks/use-auth";

/**
 * Renders children only for an authenticated session; otherwise redirects to
 * /login (handled inside useAuthGuard). Server-side RBAC remains the real
 * access control — this is a UX guard so protected shells don't flash.
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const ready = useAuthGuard();

  if (!ready) {
    return (
      <div className="flex min-h-dvh items-center justify-center">
        <Loader2 className="size-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return <>{children}</>;
}
