import Link from "next/link";
import { Coffee } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6 text-center">
      <Coffee className="h-16 w-16 text-gold" />
      <h1 className="mt-6 font-serif text-6xl font-bold text-cream">404</h1>
      <p className="mt-3 max-w-md text-lg text-cream/70">
        This page has gone cold. Let&apos;s get you back to something warm.
      </p>
      <Link href="/" className={buttonVariants({}) + " mt-8"}>
        Back to Home
      </Link>
    </div>
  );
}
