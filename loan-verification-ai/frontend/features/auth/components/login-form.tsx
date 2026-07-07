"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { Loader2, Lock, Mail } from "lucide-react";
import { loginSchema, type LoginInput } from "@/features/auth/domain/schemas";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

/**
 * Login form. Wired to validation + submit UX now; the real token exchange is
 * connected to the backend in the authentication phase (Phase 7). Until then a
 * successful validate routes to the applicant dashboard so the shell is
 * navigable end to end.
 */
export function LoginForm() {
  const router = useRouter();
  const [submitError, setSubmitError] = React.useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  async function onSubmit(_values: LoginInput) {
    setSubmitError(null);
    try {
      // Phase 7 replaces this with apiClient.post('/auth/login', values).
      await new Promise((resolve) => setTimeout(resolve, 600));
      router.push("/dashboard");
    } catch {
      setSubmitError("Unable to sign in. Please try again.");
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <div className="relative">
          <Mail className="pointer-events-none absolute left-3.5 top-1/2 size-5 -translate-y-1/2 text-muted-foreground" />
          <Input
            id="email"
            type="email"
            inputMode="email"
            autoComplete="email"
            placeholder="you@bank.com"
            className="pl-11"
            aria-invalid={!!errors.email}
            {...register("email")}
          />
        </div>
        {errors.email ? <p className="text-xs text-destructive">{errors.email.message}</p> : null}
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <div className="relative">
          <Lock className="pointer-events-none absolute left-3.5 top-1/2 size-5 -translate-y-1/2 text-muted-foreground" />
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            placeholder="••••••••"
            className="pl-11"
            aria-invalid={!!errors.password}
            {...register("password")}
          />
        </div>
        {errors.password ? (
          <p className="text-xs text-destructive">{errors.password.message}</p>
        ) : null}
      </div>

      {submitError ? (
        <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {submitError}
        </p>
      ) : null}

      <Button type="submit" size="full" disabled={isSubmitting}>
        {isSubmitting ? <Loader2 className="animate-spin" /> : null}
        {isSubmitting ? "Signing in…" : "Sign in"}
      </Button>
    </form>
  );
}
