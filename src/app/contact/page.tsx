import type { Metadata } from "next";
import { Clock, Mail, MapPin, MessageCircle, Phone } from "lucide-react";
import { ContactForm } from "@/components/sections/contact-form";
import { faqs } from "@/data/content";

export const metadata: Metadata = {
  title: "Contact",
  description:
    "Get in touch with Premium Café — visit us, call, WhatsApp or send a message. Find our opening hours and location.",
};

const hours = [
  { day: "Monday – Friday", time: "7:00 AM – 11:00 PM" },
  { day: "Saturday", time: "8:00 AM – 12:00 AM" },
  { day: "Sunday", time: "8:00 AM – 10:00 PM" },
];

export default function ContactPage() {
  return (
    <div className="pt-18">
      <section className="border-b border-cream/10 bg-coffee/20 py-16">
        <div className="container text-center">
          <span className="mb-3 inline-block text-sm font-medium uppercase tracking-[0.25em] text-gold">
            We&apos;d love to hear from you
          </span>
          <h1 className="font-serif text-4xl font-bold text-cream sm:text-5xl md:text-6xl">
            Get in <span className="gold-text">Touch</span>
          </h1>
        </div>
      </section>

      <section className="container grid gap-10 py-16 lg:grid-cols-2">
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              { icon: Phone, label: "Call us", value: "+91 98765 43210" },
              { icon: MessageCircle, label: "WhatsApp", value: "+91 98765 43210" },
              { icon: Mail, label: "Email", value: "hello@premiumcafe.example" },
              { icon: MapPin, label: "Visit", value: "42 Roasters Lane, Bengaluru" },
            ].map((c) => {
              const Icon = c.icon;
              return (
                <div
                  key={c.label}
                  className="rounded-2xl border border-cream/10 bg-coffee/20 p-5"
                >
                  <Icon className="mb-3 h-6 w-6 text-gold" />
                  <p className="text-sm text-cream/50">{c.label}</p>
                  <p className="font-medium text-cream">{c.value}</p>
                </div>
              );
            })}
          </div>

          <div className="rounded-2xl border border-cream/10 bg-coffee/20 p-6">
            <h3 className="mb-4 flex items-center gap-2 font-serif text-lg font-semibold text-cream">
              <Clock className="h-5 w-5 text-gold" /> Opening Hours
            </h3>
            <ul className="space-y-2">
              {hours.map((h) => (
                <li
                  key={h.day}
                  className="flex justify-between border-b border-cream/5 pb-2 text-sm last:border-0"
                >
                  <span className="text-cream/70">{h.day}</span>
                  <span className="font-medium text-cream">{h.time}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Map placeholder — swap for Google Maps embed with your API key */}
          <div className="overflow-hidden rounded-2xl border border-cream/10">
            <iframe
              title="Premium Café location"
              src="https://www.openstreetmap.org/export/embed.html?bbox=77.55%2C12.95%2C77.65%2C13.02&layer=mapnik"
              className="h-64 w-full"
              loading="lazy"
            />
          </div>
        </div>

        <ContactForm />
      </section>

      {/* FAQ */}
      <section className="border-t border-cream/10 bg-coffee/20 py-16">
        <div className="container max-w-3xl">
          <h2 className="mb-8 text-center font-serif text-3xl font-bold text-cream">
            Frequently Asked Questions
          </h2>
          <div className="space-y-3">
            {faqs.map((faq) => (
              <details
                key={faq.q}
                className="group rounded-2xl border border-cream/10 bg-espresso/40 p-5"
              >
                <summary className="flex cursor-pointer list-none items-center justify-between font-medium text-cream">
                  {faq.q}
                  <span className="text-gold transition-transform group-open:rotate-45">
                    +
                  </span>
                </summary>
                <p className="mt-3 text-sm leading-relaxed text-cream/60">
                  {faq.a}
                </p>
              </details>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
