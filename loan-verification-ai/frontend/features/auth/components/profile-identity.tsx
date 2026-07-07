"use client";

import { LogOut } from "lucide-react";
import { useCurrentUser, useLogout } from "@/features/auth/hooks/use-auth";
import { Card, CardContent } from "@/shared/ui/card";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import type { UserRole } from "@/features/auth/domain/schemas";

const ROLE_LABEL: Record<UserRole, string> = {
  admin: "Admin",
  officer: "Officer",
  applicant: "Applicant",
  auditor: "Auditor",
};

function initials(name: string): string {
  return name
    .split(" ")
    .map((part) => part[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export function ProfileIdentity() {
  const { data: user, isLoading } = useCurrentUser();

  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-5">
        <div className="flex size-14 items-center justify-center rounded-full bg-accent text-lg font-bold text-accent-foreground">
          {isLoading || !user ? "…" : initials(user.fullName)}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate font-semibold">{user?.fullName ?? "Loading…"}</p>
          <p className="truncate text-sm text-muted-foreground">{user?.email ?? ""}</p>
        </div>
        {user ? <Badge variant="primary">{ROLE_LABEL[user.role]}</Badge> : null}
      </CardContent>
    </Card>
  );
}

export function SignOutButton() {
  const logout = useLogout();
  return (
    <Button variant="outline" size="full" onClick={() => void logout()}>
      <LogOut />
      Sign out
    </Button>
  );
}
