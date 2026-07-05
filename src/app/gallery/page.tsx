import type { Metadata } from "next";
import { GalleryGrid } from "@/components/sections/gallery-grid";

export const metadata: Metadata = {
  title: "Gallery",
  description:
    "A visual tour of Premium Café — our interiors, signature dishes, latte art and events.",
};

export default function GalleryPage() {
  return (
    <div className="pt-18">
      <section className="border-b border-cream/10 bg-coffee/20 py-16">
        <div className="container text-center">
          <span className="mb-3 inline-block text-sm font-medium uppercase tracking-[0.25em] text-gold">
            A visual feast
          </span>
          <h1 className="font-serif text-4xl font-bold text-cream sm:text-5xl md:text-6xl">
            Our <span className="gold-text">Gallery</span>
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-cream/70">
            Step inside the Premium Café world — every corner crafted for delight.
          </p>
        </div>
      </section>
      <GalleryGrid />
    </div>
  );
}
