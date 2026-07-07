"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { cn } from "@/shared/lib/utils";
import { NAV_BY_PERSONA, type Persona } from "@/shared/ui/shell/navigation";

/**
 * Fixed bottom tab bar — the primary navigation pattern for the app. Uses a
 * shared-layout animated pill to indicate the active tab, the way native tab
 * bars highlight the current section. Resolves its own item list from the
 * persona so icon components never cross the RSC boundary.
 */
export function BottomNav({ persona }: { persona: Persona }) {
  const pathname = usePathname();
  const items = NAV_BY_PERSONA[persona];

  return (
    <nav className="safe-bottom sticky bottom-0 z-20 border-t border-border/60 bg-background/85 backdrop-blur-lg">
      <ul className="mx-auto flex max-w-[480px] items-stretch justify-around px-2 pt-1.5">
        {items.map((item) => {
          const active =
            pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <li key={item.href} className="flex-1">
              <Link
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "relative flex flex-col items-center gap-1 rounded-xl px-2 py-1.5 text-[11px] font-medium transition-colors",
                  active ? "text-primary" : "text-muted-foreground hover:text-foreground",
                )}
              >
                {active ? (
                  <motion.span
                    layoutId="bottom-nav-active"
                    className="absolute inset-0 rounded-xl bg-accent"
                    transition={{ type: "spring", stiffness: 500, damping: 40 }}
                  />
                ) : null}
                <Icon className="relative size-6" />
                <span className="relative">{item.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
