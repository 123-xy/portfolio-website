import * as React from "react";
import { cn } from "@/lib/utils";

const variants = {
  gold: "bg-gold/15 text-gold border border-gold/30",
  veg: "bg-green-500/15 text-green-400 border border-green-500/30",
  nonveg: "bg-red-500/15 text-red-400 border border-red-500/30",
  bestseller: "bg-gold-gradient text-espresso font-semibold border-none",
  muted: "bg-cream/10 text-cream/80 border border-cream/15",
};

export function Badge({
  className,
  variant = "gold",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { variant?: keyof typeof variants }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}
