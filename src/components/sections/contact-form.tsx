"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Send } from "lucide-react";
import { toast } from "sonner";
import { Input, Textarea } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const schema = z.object({
  name: z.string().min(2, "Please enter your name"),
  email: z.string().email("Enter a valid email"),
  subject: z.string().min(3, "Add a subject"),
  message: z.string().min(10, "Tell us a little more"),
});

type FormValues = z.infer<typeof schema>;

export function ContactForm() {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = handleSubmit(async (values) => {
    // Wire to an API route (e.g. Resend) here.
    await new Promise((r) => setTimeout(r, 700));
    console.log("Contact message:", values);
    toast.success("Message sent! We'll get back to you shortly.");
    reset();
  });

  return (
    <form
      onSubmit={onSubmit}
      className="h-fit rounded-3xl border border-cream/10 bg-coffee/20 p-6"
    >
      <h2 className="mb-5 font-serif text-2xl font-bold text-cream">
        Send us a message
      </h2>
      <div className="space-y-4">
        <Field label="Name" error={errors.name?.message}>
          <Input placeholder="Your name" {...register("name")} />
        </Field>
        <Field label="Email" error={errors.email?.message}>
          <Input placeholder="you@email.com" {...register("email")} />
        </Field>
        <Field label="Subject" error={errors.subject?.message}>
          <Input placeholder="How can we help?" {...register("subject")} />
        </Field>
        <Field label="Message" error={errors.message?.message}>
          <Textarea placeholder="Write your message..." {...register("message")} />
        </Field>
        <Button type="submit" size="lg" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? "Sending..." : "Send Message"}
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </form>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <label className={cn("block")}>
      <span className="mb-1.5 block text-sm text-cream/70">{label}</span>
      {children}
      {error && <span className="mt-1 block text-xs text-red-400">{error}</span>}
    </label>
  );
}
