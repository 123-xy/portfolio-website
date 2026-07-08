import { cn } from "@/shared/lib/utils";

/** Shimmering placeholder block for loading states. */
export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("animate-pulse rounded-xl bg-muted", className)} {...props} />;
}
