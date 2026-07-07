import type { LucideIcon } from "lucide-react";
import { LayoutDashboard, FileCheck2, ListChecks, BarChart3, User } from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

/** Persona keyed nav sets. A serializable `Persona` string crosses the RSC
 * boundary; the client BottomNav resolves it to the item list (icons are
 * component functions and cannot be passed server→client). */
export type Persona = "applicant" | "officer";

const applicantNav: NavItem[] = [
  { href: "/dashboard", label: "Home", icon: LayoutDashboard },
  { href: "/applications", label: "Applications", icon: FileCheck2 },
  { href: "/profile", label: "Profile", icon: User },
];

const officerNav: NavItem[] = [
  { href: "/queue", label: "Queue", icon: ListChecks },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/profile", label: "Profile", icon: User },
];

export const NAV_BY_PERSONA: Record<Persona, NavItem[]> = {
  applicant: applicantNav,
  officer: officerNav,
};
