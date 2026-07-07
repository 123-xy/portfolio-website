"use client";

import * as React from "react";
import { ChevronLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import { cn } from "@/shared/lib/utils";
import { Button } from "@/shared/ui/button";

interface AppBarProps {
  title: string;
  subtitle?: string;
  /** Show a back chevron that pops the router history. */
  showBack?: boolean;
  /** Optional trailing action(s), e.g. theme toggle or notifications. */
  action?: React.ReactNode;
  className?: string;
}

/** Sticky top app bar with safe-area padding — the native-app header pattern. */
export function AppBar({ title, subtitle, showBack, action, className }: AppBarProps) {
  const router = useRouter();

  return (
    <header
      className={cn(
        "safe-top sticky top-0 z-20 flex items-center gap-2 border-b border-border/60 bg-background/80 px-3 pb-3 pt-3 backdrop-blur-lg",
        className,
      )}
    >
      {showBack ? (
        <Button variant="ghost" size="icon" aria-label="Go back" onClick={() => router.back()}>
          <ChevronLeft />
        </Button>
      ) : (
        <div className="w-1" />
      )}
      <div className="min-w-0 flex-1">
        <h1 className="truncate text-lg font-bold leading-tight">{title}</h1>
        {subtitle ? <p className="truncate text-xs text-muted-foreground">{subtitle}</p> : null}
      </div>
      {action ? <div className="flex items-center gap-1">{action}</div> : null}
    </header>
  );
}
