import type { Metadata } from "next";
import { Checkout } from "@/components/sections/checkout";

export const metadata: Metadata = {
  title: "Checkout",
  description: "Complete your Premium Café order — delivery, pickup or dine-in.",
};

export default function CheckoutPage() {
  return (
    <div className="pt-18">
      <div className="container py-16">
        <h1 className="mb-2 font-serif text-4xl font-bold text-cream">Checkout</h1>
        <p className="mb-10 text-cream/60">
          Review your order and choose how you&apos;d like to enjoy it.
        </p>
        <Checkout />
      </div>
    </div>
  );
}
