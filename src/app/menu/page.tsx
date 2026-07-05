import type { Metadata } from "next";
import { MenuBrowser } from "@/components/sections/menu-browser";

export const metadata: Metadata = {
  title: "Menu",
  description:
    "Explore Premium Café's full menu — hot & cold coffee, espresso, teas, smoothies, pizzas, pasta, desserts and more. Order online for delivery.",
};

export default function MenuPage() {
  return (
    <div className="pt-18">
      <section className="border-b border-cream/10 bg-coffee/20 py-16">
        <div className="container text-center">
          <span className="mb-3 inline-block text-sm font-medium uppercase tracking-[0.25em] text-gold">
            Crafted with love
          </span>
          <h1 className="font-serif text-4xl font-bold text-cream sm:text-5xl md:text-6xl">
            Our <span className="gold-text">Menu</span>
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-cream/70">
            From single-origin espresso to indulgent desserts — every item is
            crafted fresh, to order.
          </p>
        </div>
      </section>
      <MenuBrowser />
    </div>
  );
}
