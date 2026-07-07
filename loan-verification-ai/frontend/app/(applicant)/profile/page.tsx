import type { Metadata } from "next";
import Link from "next/link";
import { LogOut, Moon, ShieldCheck, UserCog } from "lucide-react";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { Card, CardContent } from "@/shared/ui/card";
import { Badge } from "@/shared/ui/badge";
import { ThemeToggle } from "@/shared/ui/theme-toggle";
import { buttonVariants } from "@/shared/ui/button";

export const metadata: Metadata = { title: "Profile" };

// Settings screens land in a later phase; shown here as upcoming so the menu
// reflects the intended IA without dead-ending navigation.
const menu = [
  { label: "Account settings", icon: UserCog },
  { label: "Security", icon: ShieldCheck },
];

export default function ProfilePage() {
  return (
    <AppShell title="Profile" nav="applicant">
      <div className="space-y-6">
        {/* Identity card — real user data wired in Phase 7. */}
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex size-14 items-center justify-center rounded-full bg-accent text-lg font-bold text-accent-foreground">
              JC
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate font-semibold">Jane Cooper</p>
              <p className="truncate text-sm text-muted-foreground">jane.cooper@bank.com</p>
            </div>
            <Badge variant="primary">Applicant</Badge>
          </CardContent>
        </Card>

        {/* Appearance */}
        <Card>
          <CardContent className="flex items-center justify-between p-4">
            <div className="flex items-center gap-3">
              <Moon className="size-5 text-muted-foreground" />
              <span className="text-sm font-medium">Appearance</span>
            </div>
            <ThemeToggle />
          </CardContent>
        </Card>

        {/* Menu */}
        <Card className="divide-y divide-border">
          {menu.map(({ label, icon: Icon }) => (
            <div key={label} className="flex items-center gap-3 p-4">
              <Icon className="size-5 text-muted-foreground" />
              <span className="flex-1 text-sm font-medium">{label}</span>
              <Badge variant="outline">Soon</Badge>
            </div>
          ))}
        </Card>

        <Link href="/login" className={buttonVariants({ variant: "outline", size: "full" })}>
          <LogOut />
          Sign out
        </Link>
      </div>
    </AppShell>
  );
}
