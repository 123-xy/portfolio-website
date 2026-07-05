"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Star } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { SmartImage } from "@/components/ui/smart-image";

export function Hero() {
  return (
    <section className="relative flex min-h-screen items-center overflow-hidden pt-18">
      {/* Background image */}
      <div className="absolute inset-0 -z-10">
        <SmartImage
          src="https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1920&q=80"
          alt="Premium coffee being poured"
          className="h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-espresso via-espresso/85 to-espresso/40" />
        <div className="absolute inset-0 bg-gradient-to-t from-espresso via-transparent to-espresso/60" />
      </div>

      <div className="container grid items-center gap-12 py-20 lg:grid-cols-2">
        <div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-6 inline-flex items-center gap-2 rounded-full border border-gold/30 bg-gold/10 px-4 py-1.5 text-sm text-gold"
          >
            <Star className="h-3.5 w-3.5 fill-gold" />
            Rated 4.9 by 85,000+ coffee lovers
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="font-serif text-5xl font-bold leading-[1.05] text-cream text-balance sm:text-6xl lg:text-7xl"
          >
            Where every cup is a <span className="gold-text">masterpiece</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="mt-6 max-w-lg text-lg leading-relaxed text-cream/70"
          >
            Slow-roasted single-origin beans, hand-crafted by award-winning
            baristas. Indulge in luxury coffee, artisan food and an ambience made
            for moments that matter.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="mt-8 flex flex-wrap gap-4"
          >
            <Link href="/menu" className={buttonVariants({ size: "lg" })}>
              Order Now <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/reservation"
              className={buttonVariants({ variant: "outline", size: "lg" })}
            >
              Reserve a Table
            </Link>
          </motion.div>
        </div>

        {/* Floating feature card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="relative hidden lg:block"
        >
          <div className="animate-float glass rounded-3xl p-6 shadow-soft">
            <SmartImage
              src="https://images.unsplash.com/photo-1572442388796-11668a67e53d?auto=format&fit=crop&w=800&q=80"
              alt="Signature cappuccino"
              className="aspect-square w-full rounded-2xl object-cover"
            />
            <div className="mt-4 flex items-center justify-between">
              <div>
                <p className="font-serif text-xl font-semibold text-cream">
                  Velvet Cappuccino
                </p>
                <p className="text-sm text-cream/60">Barista&apos;s signature</p>
              </div>
              <span className="font-serif text-2xl font-bold text-gold">₹240</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Scroll cue */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2">
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ repeat: Infinity, duration: 1.8 }}
          className="flex h-10 w-6 items-start justify-center rounded-full border-2 border-cream/30 p-1.5"
        >
          <span className="h-2 w-1 rounded-full bg-gold" />
        </motion.div>
      </div>
    </section>
  );
}
