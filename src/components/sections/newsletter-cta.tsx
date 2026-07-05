"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Mail } from "lucide-react";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function NewsletterCTA() {
  const [email, setEmail] = useState("");

  return (
    <section className="container py-24">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="relative overflow-hidden rounded-[2rem] border border-gold/25 bg-gradient-to-br from-coffee to-espresso px-6 py-16 text-center shadow-soft sm:px-16"
      >
        <div className="absolute -left-20 top-0 h-64 w-64 rounded-full bg-gold/10 blur-3xl" />
        <div className="absolute -right-20 bottom-0 h-64 w-64 rounded-full bg-caramel/10 blur-3xl" />
        <div className="relative mx-auto max-w-xl">
          <span className="mb-5 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gold-gradient text-espresso">
            <Mail className="h-7 w-7" />
          </span>
          <h2 className="font-serif text-3xl font-bold text-cream sm:text-4xl">
            Join the Premium Club
          </h2>
          <p className="mx-auto mt-4 max-w-md text-cream/70">
            Get exclusive offers, first access to new blends and a welcome gift of
            15% off your first order.
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!email) return;
              toast.success("Welcome aboard! Check your inbox for 15% off ☕");
              setEmail("");
            }}
            className="mx-auto mt-8 flex max-w-md flex-col gap-3 sm:flex-row"
          >
            <Input
              type="email"
              required
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="h-12"
            />
            <Button type="submit" size="lg">
              Subscribe
            </Button>
          </form>
        </div>
      </motion.div>
    </section>
  );
}
