"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { registerSchema, type RegisterInput } from "@/features/auth/domain/schemas";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

/** Registration form. Token exchange is wired to the backend in Phase 7. */
export function RegisterForm() {
  const router = useRouter();
  const [submitError, setSubmitError] = React.useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterInput>({
    resolver: zodResolver(registerSchema),
    defaultValues: { fullName: "", email: "", password: "", confirmPassword: "" },
  });

  async function onSubmit(_values: RegisterInput) {
    setSubmitError(null);
    try {
      await new Promise((resolve) => setTimeout(resolve, 600));
      router.push("/dashboard");
    } catch {
      setSubmitError("Unable to create account. Please try again.");
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
      <Field id="fullName" label="Full name" error={errors.fullName?.message}>
        <Input id="fullName" autoComplete="name" placeholder="Jane Cooper" {...register("fullName")} />
      </Field>
      <Field id="email" label="Email" error={errors.email?.message}>
        <Input
          id="email"
          type="email"
          inputMode="email"
          autoComplete="email"
          placeholder="you@bank.com"
          {...register("email")}
        />
      </Field>
      <Field id="password" label="Password" error={errors.password?.message}>
        <Input
          id="password"
          type="password"
          autoComplete="new-password"
          placeholder="••••••••"
          {...register("password")}
        />
      </Field>
      <Field id="confirmPassword" label="Confirm password" error={errors.confirmPassword?.message}>
        <Input
          id="confirmPassword"
          type="password"
          autoComplete="new-password"
          placeholder="••••••••"
          {...register("confirmPassword")}
        />
      </Field>

      {submitError ? (
        <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {submitError}
        </p>
      ) : null}

      <Button type="submit" size="full" disabled={isSubmitting}>
        {isSubmitting ? <Loader2 className="animate-spin" /> : null}
        {isSubmitting ? "Creating account…" : "Create account"}
      </Button>
    </form>
  );
}

function Field({
  id,
  label,
  error,
  children,
}: {
  id: string;
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      {children}
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}
