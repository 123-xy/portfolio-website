import type { Metadata } from "next";
import { ReservationForm } from "@/components/sections/reservation-form";
import { SmartImage } from "@/components/ui/smart-image";

export const metadata: Metadata = {
  title: "Reservation",
  description:
    "Reserve your table at Premium Café. Book online for dine-in, celebrations and special occasions.",
};

export default function ReservationPage() {
  return (
    <div className="pt-18">
      <section className="container py-16">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div className="order-2 lg:order-1">
            <span className="mb-3 inline-block text-sm font-medium uppercase tracking-[0.25em] text-gold">
              Dine with us
            </span>
            <h1 className="font-serif text-4xl font-bold text-cream sm:text-5xl">
              Reserve Your <span className="gold-text">Table</span>
            </h1>
            <p className="mt-4 max-w-md text-cream/70">
              Secure your spot for an unforgettable coffee experience. Perfect for
              catch-ups, celebrations or a quiet moment to yourself.
            </p>
            <div className="mt-8">
              <ReservationForm />
            </div>
          </div>
          <div className="order-1 lg:order-2">
            <SmartImage
              src="https://images.unsplash.com/photo-1600093463592-8e36ae95ef56?auto=format&fit=crop&w=800&q=80"
              alt="Elegant café interior"
              className="aspect-[4/5] w-full rounded-3xl object-cover shadow-soft"
            />
          </div>
        </div>
      </section>
    </div>
  );
}
