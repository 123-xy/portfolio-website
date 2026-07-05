"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import { CalendarCheck } from "lucide-react";
import { toast } from "sonner";
import { Input, Textarea } from "@/components/ui/input";
import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const schema = z.object({
  name: z.string().min(2, "Please enter your name"),
  phone: z.string().min(10, "Enter a valid phone number"),
  email: z.string().email("Enter a valid email"),
  guests: z.coerce.number().min(1, "At least 1 guest").max(20, "Max 20 guests"),
  date: z.string().min(1, "Choose a date"),
  time: z.string().min(1, "Choose a time"),
  requests: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

const timeSlots = [
  "08:00",
  "10:00",
  "12:00",
  "14:00",
  "16:00",
  "18:00",
  "20:00",
];

export function ReservationForm() {
  const [done, setDone] = useState(false);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { guests: 2 },
  });

  const onSubmit = handleSubmit(async (values) => {
    // Wire to Supabase `reservations` table here.
    await new Promise((r) => setTimeout(r, 800));
    console.log("Reservation:", values);
    setDone(true);
    reset();
    toast.success("Table reserved! We've sent you a confirmation.");
  });

  if (done) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="rounded-3xl border border-gold/25 bg-coffee/30 p-8 text-center"
      >
        <CalendarCheck className="mx-auto h-14 w-14 text-green-400" />
        <h3 className="mt-4 font-serif text-2xl font-bold text-cream">
          Reservation Confirmed
        </h3>
        <p className="mt-2 text-cream/70">
          We can&apos;t wait to host you. A confirmation has been sent to your
          email.
        </p>
        <button
          onClick={() => setDone(false)}
          className={buttonVariants({ variant: "outline" }) + " mt-6"}
        >
          Book Another
        </button>
      </motion.div>
    );
  }

  return (
    <form
      onSubmit={onSubmit}
      className="space-y-4 rounded-3xl border border-cream/10 bg-coffee/20 p-6"
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Name" error={errors.name?.message}>
          <Input placeholder="Your name" {...register("name")} />
        </Field>
        <Field label="Phone" error={errors.phone?.message}>
          <Input placeholder="+91 98765 43210" {...register("phone")} />
        </Field>
        <Field label="Email" error={errors.email?.message} className="sm:col-span-2">
          <Input placeholder="you@email.com" {...register("email")} />
        </Field>
        <Field label="Guests" error={errors.guests?.message}>
          <Input type="number" min={1} max={20} {...register("guests")} />
        </Field>
        <Field label="Date" error={errors.date?.message}>
          <Input type="date" {...register("date")} />
        </Field>
        <Field label="Time slot" error={errors.time?.message} className="sm:col-span-2">
          <select
            {...register("time")}
            className={cn(
              "flex h-11 w-full rounded-xl border border-cream/15 bg-espresso/40 px-4 text-sm text-cream focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold/60 [&>option]:bg-coffee"
            )}
          >
            <option value="">Select a time</option>
            {timeSlots.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Special requests (optional)" className="sm:col-span-2">
          <Textarea
            placeholder="Birthday, dietary needs, seating preference..."
            {...register("requests")}
          />
        </Field>
      </div>
      <Button type="submit" size="lg" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? "Reserving..." : "Confirm Reservation"}
      </Button>
    </form>
  );
}

function Field({
  label,
  error,
  children,
  className,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <label className={cn("block", className)}>
      <span className="mb-1.5 block text-sm text-cream/70">{label}</span>
      {children}
      {error && <span className="mt-1 block text-xs text-red-400">{error}</span>}
    </label>
  );
}
