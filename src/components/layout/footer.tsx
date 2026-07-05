"use client";

import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";
import {
  Coffee,
  Facebook,
  Instagram,
  Mail,
  MapPin,
  Phone,
  Twitter,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const columns = [
  {
    title: "Explore",
    links: [
      { href: "/menu", label: "Menu" },
      { href: "/about", label: "About Us" },
      { href: "/gallery", label: "Gallery" },
      { href: "/blog", label: "Blog" },
    ],
  },
  {
    title: "Order",
    links: [
      { href: "/menu", label: "Delivery" },
      { href: "/reservation", label: "Reservations" },
      { href: "/checkout", label: "Checkout" },
      { href: "/contact", label: "Contact" },
    ],
  },
];

export function Footer() {
  const [email, setEmail] = useState("");

  return (
    <footer className="border-t border-cream/10 bg-espresso">
      <div className="container grid gap-12 py-16 md:grid-cols-2 lg:grid-cols-4">
        <div>
          <Link href="/" className="flex items-center gap-2 text-cream">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gold-gradient text-espresso">
              <Coffee className="h-5 w-5" />
            </span>
            <span className="font-serif text-xl font-bold">
              Premium<span className="text-gold">Café</span>
            </span>
          </Link>
          <p className="mt-4 max-w-xs text-sm leading-relaxed text-cream/60">
            Luxury coffee, hand-crafted food and an unforgettable ambience — served
            with passion since 2013.
          </p>
          <div className="mt-5 flex gap-2">
            {[Instagram, Facebook, Twitter].map((Icon, i) => (
              <a
                key={i}
                href="#"
                aria-label="Social link"
                className="flex h-9 w-9 items-center justify-center rounded-full border border-cream/15 text-cream/70 transition-colors hover:border-gold hover:text-gold"
              >
                <Icon className="h-4 w-4" />
              </a>
            ))}
          </div>
        </div>

        {columns.map((col) => (
          <div key={col.title}>
            <h4 className="mb-4 font-serif text-lg font-semibold text-cream">
              {col.title}
            </h4>
            <ul className="space-y-2.5">
              {col.links.map((l) => (
                <li key={l.label}>
                  <Link
                    href={l.href}
                    className="text-sm text-cream/60 transition-colors hover:text-gold"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}

        <div>
          <h4 className="mb-4 font-serif text-lg font-semibold text-cream">
            Stay in the loop
          </h4>
          <p className="mb-3 text-sm text-cream/60">
            Subscribe for offers, new blends and events.
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!email) return;
              toast.success("You're subscribed! Welcome to the club ☕");
              setEmail("");
            }}
            className="flex flex-col gap-2 sm:flex-row"
          >
            <Input
              type="email"
              required
              placeholder="you@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Button type="submit" size="sm">
              Join
            </Button>
          </form>
          <ul className="mt-6 space-y-2.5 text-sm text-cream/60">
            <li className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-gold" /> 42 Roasters Lane, Bengaluru
            </li>
            <li className="flex items-center gap-2">
              <Phone className="h-4 w-4 text-gold" /> +91 98765 43210
            </li>
            <li className="flex items-center gap-2">
              <Mail className="h-4 w-4 text-gold" /> hello@premiumcafe.example
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-cream/10">
        <div className="container flex flex-col items-center justify-between gap-3 py-6 text-sm text-cream/50 sm:flex-row">
          <p>© {new Date().getFullYear()} Premium Café. All rights reserved.</p>
          <p>Crafted with ☕ &amp; care.</p>
        </div>
      </div>
    </footer>
  );
}
