import type { Metadata } from "next";
import { Moon, ShieldCheck, UserCog } from "lucide-react";
import { AppShell } from "@/shared/ui/shell/app-shell";
import { Card, CardContent } from "@/shared/ui/card";
import { Badge } from "@/shared/ui/badge";
import { ThemeToggle } from "@/shared/ui/theme-toggle";
import { ProfileIdentity, SignOutButton } from "@/features/auth/components/profile-identity";

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
        <ProfileIdentity />

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

        <SignOutButton />
      </div>
    </AppShell>
  );
}
