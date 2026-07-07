"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchCurrentUser, logout as logoutRequest } from "@/features/auth/api/auth-api";
import { isAuthenticated } from "@/shared/lib/auth-tokens";
import type { AuthUser, UserRole } from "@/features/auth/domain/schemas";

const CURRENT_USER_KEY = ["auth", "me"] as const;

/** The signed-in user, resolved from the backend. Disabled when no token is
 * present so it never fires an unauthenticated request. */
export function useCurrentUser() {
  return useQuery<AuthUser>({
    queryKey: CURRENT_USER_KEY,
    queryFn: fetchCurrentUser,
    enabled: isAuthenticated(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

/** Client-side route guard: redirect to /login when there is no session. Server
 * enforces RBAC on every endpoint; this only improves UX by not rendering a
 * shell the user cannot use. */
export function useAuthGuard(): boolean {
  const router = useRouter();
  const [ready, setReady] = React.useState(false);

  React.useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    } else {
      setReady(true);
    }
  }, [router]);

  return ready;
}

/** The landing route for a given role after authentication. */
export function homeRouteForRole(role: UserRole): string {
  return role === "officer" || role === "admin" || role === "auditor" ? "/queue" : "/dashboard";
}

export function useLogout(): () => Promise<void> {
  const router = useRouter();
  const queryClient = useQueryClient();

  return React.useCallback(async () => {
    await logoutRequest();
    queryClient.clear();
    router.replace("/login");
  }, [router, queryClient]);
}
