import Link from "next/link";
import { ShieldCheck, ScanFace, AudioLines, Gauge } from "lucide-react";
import { buttonVariants } from "@/shared/ui/button";
import { env } from "@/shared/lib/env";

const highlights = [
  { icon: ScanFace, label: "Face match" },
  { icon: AudioLines, label: "Voice consent" },
  { icon: Gauge, label: "Risk score" },
];

export default function WelcomePage() {
  return (
    <div className="safe-top safe-bottom flex flex-1 flex-col justify-between px-6 py-10">
      <div className="flex items-center gap-2 text-primary">
        <ShieldCheck className="size-7" />
        <span className="text-lg font-bold tracking-tight">{env.NEXT_PUBLIC_APP_NAME}</span>
      </div>

      <div className="space-y-6">
        <div className="inline-flex items-center gap-2 rounded-full bg-accent px-3 py-1 text-xs font-medium text-accent-foreground">
          <span className="relative flex size-2">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-60" />
            <span className="relative inline-flex size-2 rounded-full bg-primary" />
          </span>
          Bank-grade verification
        </div>

        <h1 className="text-4xl font-extrabold leading-[1.1] tracking-tight">
          Verify loan
          <br />
          co-applicants in
          <br />
          <span className="text-primary">minutes.</span>
        </h1>

        <p className="max-w-xs text-base text-muted-foreground">
          AI-assisted face matching, spoken consent, and intent analysis — every
          decision reviewed by a human officer and fully audited.
        </p>

        <div className="flex flex-wrap gap-2">
          {highlights.map(({ icon: Icon, label }) => (
            <span
              key={label}
              className="inline-flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-xs font-medium text-card-foreground"
            >
              <Icon className="size-4 text-primary" />
              {label}
            </span>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <Link href="/login" className={buttonVariants({ size: "full" })}>
          Get started
        </Link>
        <p className="text-center text-sm text-muted-foreground">
          Already onboarded?{" "}
          <Link href="/login" className="font-semibold text-primary">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
