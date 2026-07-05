"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Image with graceful degradation: if the remote source fails to load
 * (offline, blocked host, expired URL) it fades to an elegant coffee
 * gradient instead of showing a broken image. Lazy-loaded by default.
 */
export function SmartImage({
  src,
  alt,
  className,
  ...props
}: React.ImgHTMLAttributes<HTMLImageElement>) {
  const [failed, setFailed] = React.useState(false);
  const [loaded, setLoaded] = React.useState(false);

  if (failed || !src) {
    return (
      <div
        className={cn(
          "flex aspect-[4/3] min-h-32 items-center justify-center bg-gradient-to-br from-mocha via-coffee to-espresso",
          className
        )}
        aria-label={alt}
        role="img"
      >
        <span className="font-serif text-2xl text-gold/40">☕</span>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      onError={() => setFailed(true)}
      onLoad={() => setLoaded(true)}
      className={cn(
        "transition-opacity duration-700",
        loaded ? "opacity-100" : "opacity-0",
        className
      )}
      {...props}
    />
  );
}
