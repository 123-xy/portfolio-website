import Link from "next/link";
import { Compass } from "lucide-react";
import { buttonVariants } from "@/shared/ui/button";

export default function NotFound() {
  return (
    <div className="flex min-h-dvh flex-col items-center justify-center gap-4 px-8 text-center">
      <div className="flex size-16 items-center justify-center rounded-2xl bg-accent text-accent-foreground">
        <Compass className="size-8" />
      </div>
      <h1 className="text-2xl font-bold">Page not found</h1>
      <p className="max-w-xs text-sm text-muted-foreground">
        The screen you're looking for doesn't exist or has moved.
      </p>
      <Link href="/dashboard" className={buttonVariants({ size: "lg" })}>
        Back to home
      </Link>
    </div>
  );
}
