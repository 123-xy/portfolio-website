"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import {
  createApplicationSchema,
  type CreateApplicationInput,
} from "@/features/applications/domain/schemas";
import { useCreateApplication } from "@/features/applications/hooks/use-applications";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

export function CreateApplicationForm() {
  const router = useRouter();
  const createApplication = useCreateApplication();
  const [submitError, setSubmitError] = React.useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateApplicationInput>({
    resolver: zodResolver(createApplicationSchema),
  });

  async function onSubmit(values: CreateApplicationInput) {
    setSubmitError(null);
    try {
      const app = await createApplication.mutateAsync(values);
      // Continue to the upload step for the new application.
      router.replace(`/applications/${app.id}`);
    } catch {
      setSubmitError("Couldn't create the application. Please try again.");
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
      <div className="space-y-2">
        <Label htmlFor="loanAmount">Loan amount (₹)</Label>
        <Input
          id="loanAmount"
          type="number"
          inputMode="decimal"
          step="1000"
          placeholder="1500000"
          aria-invalid={!!errors.loanAmount}
          {...register("loanAmount", { valueAsNumber: true })}
        />
        {errors.loanAmount ? (
          <p className="text-xs text-destructive">{errors.loanAmount.message}</p>
        ) : null}
      </div>

      <div className="space-y-2">
        <Label htmlFor="loanPurpose">Purpose (optional)</Label>
        <Input id="loanPurpose" placeholder="Home loan" {...register("loanPurpose")} />
      </div>

      <div className="space-y-2">
        <Label htmlFor="coApplicantName">Co-applicant name</Label>
        <Input
          id="coApplicantName"
          placeholder="Full name"
          aria-invalid={!!errors.coApplicantName}
          {...register("coApplicantName")}
        />
        {errors.coApplicantName ? (
          <p className="text-xs text-destructive">{errors.coApplicantName.message}</p>
        ) : null}
      </div>

      <div className="space-y-2">
        <Label htmlFor="coApplicantRelationship">Relationship (optional)</Label>
        <Input
          id="coApplicantRelationship"
          placeholder="Spouse, guarantor…"
          {...register("coApplicantRelationship")}
        />
      </div>

      {submitError ? (
        <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {submitError}
        </p>
      ) : null}

      <Button type="submit" size="full" disabled={isSubmitting}>
        {isSubmitting ? <Loader2 className="animate-spin" /> : null}
        {isSubmitting ? "Creating…" : "Create & continue to upload"}
      </Button>
    </form>
  );
}
