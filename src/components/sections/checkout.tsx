"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import {
  Bike,
  CheckCircle2,
  Clock,
  CreditCard,
  Store,
  Tag,
  UtensilsCrossed,
} from "lucide-react";
import { toast } from "sonner";
import { useCart, COUPONS, DELIVERY_FEE, GST_RATE } from "@/store/cart";
import { formatPrice, cn } from "@/lib/utils";
import { SmartImage } from "@/components/ui/smart-image";
import { Input } from "@/components/ui/input";
import { Button, buttonVariants } from "@/components/ui/button";

const schema = z.object({
  name: z.string().min(2, "Please enter your name"),
  phone: z.string().min(10, "Enter a valid phone number"),
  email: z.string().email("Enter a valid email"),
  address: z.string().optional(),
  instructions: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

type OrderType = "delivery" | "pickup" | "dinein";

const orderTypes: { key: OrderType; label: string; icon: typeof Bike }[] = [
  { key: "delivery", label: "Delivery", icon: Bike },
  { key: "pickup", label: "Pickup", icon: Store },
  { key: "dinein", label: "Dine-In", icon: UtensilsCrossed },
];

export function Checkout() {
  const { items, subtotal, updateQuantity, removeItem, clear } = useCart();
  const [orderType, setOrderType] = useState<OrderType>("delivery");
  const [couponInput, setCouponInput] = useState("");
  const [coupon, setCoupon] = useState<keyof typeof COUPONS | null>(null);
  const [payment, setPayment] = useState<"card" | "upi" | "cod">("card");
  const [placed, setPlaced] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const sub = subtotal();
  const deliveryFee = orderType === "delivery" ? DELIVERY_FEE : 0;
  const discount = coupon ? Math.round((sub * COUPONS[coupon].percent) / 100) : 0;
  const gst = Math.round((sub - discount) * GST_RATE);
  const total = Math.max(0, sub - discount + gst + deliveryFee);

  const eta = useMemo(() => {
    if (orderType === "delivery") return "25–35 min";
    if (orderType === "pickup") return "Ready in 15 min";
    return "Table held for 15 min";
  }, [orderType]);

  const applyCoupon = () => {
    const code = couponInput.trim().toUpperCase() as keyof typeof COUPONS;
    if (COUPONS[code]) {
      setCoupon(code);
      toast.success(`Coupon applied — ${COUPONS[code].label}`);
    } else {
      toast.error("Invalid coupon code");
    }
  };

  const onSubmit = handleSubmit(async (values) => {
    if (orderType === "delivery" && (!values.address || values.address.length < 6)) {
      toast.error("Please enter a delivery address");
      return;
    }
    // Simulate payment + order creation. Wire to Stripe/Razorpay + Supabase here.
    await new Promise((r) => setTimeout(r, 900));
    const orderId = "PC" + Math.random().toString(36).slice(2, 8).toUpperCase();
    setPlaced(orderId);
    clear();
    toast.success("Order confirmed! A receipt has been emailed to you.");
  });

  if (placed) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="mx-auto max-w-lg rounded-3xl border border-gold/25 bg-coffee/30 p-10 text-center"
      >
        <CheckCircle2 className="mx-auto h-16 w-16 text-green-400" />
        <h2 className="mt-5 font-serif text-3xl font-bold text-cream">
          Order Confirmed!
        </h2>
        <p className="mt-2 text-cream/70">
          Thank you for your order. Your order ID is{" "}
          <span className="font-mono font-semibold text-gold">{placed}</span>.
        </p>
        <div className="mt-6 flex items-center justify-center gap-2 rounded-2xl border border-cream/10 bg-espresso/40 p-4 text-cream/80">
          <Clock className="h-5 w-5 text-gold" />
          Estimated {eta}
        </div>
        <p className="mt-4 text-sm text-cream/50">
          A confirmation and invoice have been sent to your email. You can track
          your order status in real time.
        </p>
        <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
          <Link href="/menu" className={buttonVariants({})}>
            Order More
          </Link>
          <Link href="/" className={buttonVariants({ variant: "outline" })}>
            Back Home
          </Link>
        </div>
      </motion.div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="rounded-3xl border border-cream/10 bg-coffee/20 py-20 text-center">
        <p className="font-serif text-2xl text-cream">Your cart is empty</p>
        <p className="mt-2 text-cream/60">Add some delicious items to get started.</p>
        <Link href="/menu" className={buttonVariants({}) + " mt-6"}>
          Browse Menu
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_400px]">
      {/* Left: details */}
      <form onSubmit={onSubmit} className="space-y-8">
        {/* Order type */}
        <div className="rounded-3xl border border-cream/10 bg-coffee/20 p-6">
          <h3 className="mb-4 font-serif text-xl font-semibold text-cream">
            How would you like it?
          </h3>
          <div className="grid grid-cols-3 gap-3">
            {orderTypes.map((t) => {
              const Icon = t.icon;
              return (
                <button
                  key={t.key}
                  type="button"
                  onClick={() => setOrderType(t.key)}
                  className={cn(
                    "flex flex-col items-center gap-2 rounded-2xl border p-4 transition-all",
                    orderType === t.key
                      ? "border-gold bg-gold/10 text-gold"
                      : "border-cream/15 text-cream/70 hover:border-cream/30"
                  )}
                >
                  <Icon className="h-6 w-6" />
                  <span className="text-sm font-medium">{t.label}</span>
                </button>
              );
            })}
          </div>
          <div className="mt-4 flex items-center gap-2 text-sm text-cream/60">
            <Clock className="h-4 w-4 text-gold" /> {eta}
          </div>
        </div>

        {/* Contact + address */}
        <div className="rounded-3xl border border-cream/10 bg-coffee/20 p-6">
          <h3 className="mb-4 font-serif text-xl font-semibold text-cream">
            Your details
          </h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Full name" error={errors.name?.message}>
              <Input placeholder="Jane Doe" {...register("name")} />
            </Field>
            <Field label="Phone" error={errors.phone?.message}>
              <Input placeholder="+91 98765 43210" {...register("phone")} />
            </Field>
            <Field label="Email" error={errors.email?.message} className="sm:col-span-2">
              <Input placeholder="jane@email.com" {...register("email")} />
            </Field>
            {orderType === "delivery" && (
              <Field label="Delivery address" className="sm:col-span-2">
                <Input placeholder="Flat, street, area, city" {...register("address")} />
              </Field>
            )}
            <Field label="Instructions (optional)" className="sm:col-span-2">
              <Input
                placeholder="e.g. Leave at the door, extra napkins"
                {...register("instructions")}
              />
            </Field>
          </div>
        </div>

        {/* Payment */}
        <div className="rounded-3xl border border-cream/10 bg-coffee/20 p-6">
          <h3 className="mb-4 flex items-center gap-2 font-serif text-xl font-semibold text-cream">
            <CreditCard className="h-5 w-5 text-gold" /> Payment method
          </h3>
          <div className="grid gap-3 sm:grid-cols-3">
            {[
              { key: "card", label: "Card" },
              { key: "upi", label: "UPI" },
              { key: "cod", label: "Cash on Delivery" },
            ].map((p) => (
              <button
                key={p.key}
                type="button"
                onClick={() => setPayment(p.key as typeof payment)}
                className={cn(
                  "rounded-2xl border p-4 text-sm font-medium transition-all",
                  payment === p.key
                    ? "border-gold bg-gold/10 text-gold"
                    : "border-cream/15 text-cream/70 hover:border-cream/30"
                )}
              >
                {p.label}
              </button>
            ))}
          </div>
          <p className="mt-3 text-xs text-cream/40">
            Demo checkout — connect Stripe or Razorpay keys in{" "}
            <code>.env.local</code> to process real payments.
          </p>
        </div>

        <Button type="submit" size="lg" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? "Placing order..." : `Place Order · ${formatPrice(total)}`}
        </Button>
      </form>

      {/* Right: summary */}
      <aside className="h-fit rounded-3xl border border-cream/10 bg-coffee/30 p-6 lg:sticky lg:top-24">
        <h3 className="mb-4 font-serif text-xl font-semibold text-cream">
          Order Summary
        </h3>
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.id} className="flex items-center gap-3">
              <SmartImage
                src={item.image}
                alt={item.name}
                className="h-14 w-14 rounded-xl object-cover"
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-cream">{item.name}</p>
                <div className="mt-1 flex items-center gap-2 text-xs">
                  <button
                    type="button"
                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                    className="h-6 w-6 rounded-full border border-cream/20 text-cream/70 hover:border-gold"
                  >
                    −
                  </button>
                  <span className="text-cream/80">{item.quantity}</span>
                  <button
                    type="button"
                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                    className="h-6 w-6 rounded-full border border-cream/20 text-cream/70 hover:border-gold"
                  >
                    +
                  </button>
                  <button
                    type="button"
                    onClick={() => removeItem(item.id)}
                    className="ml-1 text-cream/40 hover:text-red-400"
                  >
                    Remove
                  </button>
                </div>
              </div>
              <span className="text-sm font-medium text-gold">
                {formatPrice(item.price * item.quantity)}
              </span>
            </div>
          ))}
        </div>

        {/* Coupon */}
        <div className="mt-5 flex gap-2">
          <div className="relative flex-1">
            <Tag className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-cream/40" />
            <Input
              placeholder="Coupon code"
              value={couponInput}
              onChange={(e) => setCouponInput(e.target.value)}
              className="pl-9"
            />
          </div>
          <Button type="button" variant="outline" size="sm" onClick={applyCoupon}>
            Apply
          </Button>
        </div>
        <p className="mt-2 text-xs text-cream/40">
          Try <code className="text-gold">WELCOME15</code> for 15% off.
        </p>

        {/* Totals */}
        <dl className="mt-5 space-y-2 border-t border-cream/10 pt-5 text-sm">
          <Row label="Subtotal" value={formatPrice(sub)} />
          {discount > 0 && (
            <Row label={`Discount (${coupon})`} value={`− ${formatPrice(discount)}`} accent />
          )}
          <Row label={`GST (${Math.round(GST_RATE * 100)}%)`} value={formatPrice(gst)} />
          <Row
            label="Delivery"
            value={deliveryFee === 0 ? "Free" : formatPrice(deliveryFee)}
          />
          <div className="flex items-center justify-between border-t border-cream/10 pt-3">
            <dt className="font-serif text-lg font-semibold text-cream">Total</dt>
            <dd className="font-serif text-2xl font-bold text-gold">
              {formatPrice(total)}
            </dd>
          </div>
        </dl>
      </aside>
    </div>
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

function Row({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div className="flex items-center justify-between">
      <dt className="text-cream/60">{label}</dt>
      <dd className={accent ? "text-green-400" : "text-cream/90"}>{value}</dd>
    </div>
  );
}
