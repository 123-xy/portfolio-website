"use client";

import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Error({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6 text-center">
      <AlertTriangle className="h-16 w-16 text-gold" />
      <h1 className="mt-6 font-serif text-4xl font-bold text-cream">
        Something spilled
      </h1>
      <p className="mt-3 max-w-md text-lg text-cream/70">
        We hit an unexpected error. Please try again — it&apos;s usually just a
        hiccup.
      </p>
      <Button onClick={reset} className="mt-8">
        Try Again
      </Button>
    </div>
  );
}
