"use client";

import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { Minus, Plus, ShoppingBag, Trash2, X } from "lucide-react";
import { useCart } from "@/store/cart";
import { formatPrice } from "@/lib/utils";
import { SmartImage } from "@/components/ui/smart-image";
import { buttonVariants } from "@/components/ui/button";

export function CartDrawer({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const { items, updateQuantity, removeItem, subtotal } = useCart();

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-espresso/70 backdrop-blur-sm"
          />
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-cream/10 bg-coffee shadow-soft"
          >
            <header className="flex items-center justify-between border-b border-cream/10 p-5">
              <h2 className="flex items-center gap-2 font-serif text-xl font-semibold text-cream">
                <ShoppingBag className="h-5 w-5 text-gold" /> Your Cart
              </h2>
              <button
                onClick={onClose}
                aria-label="Close cart"
                className="rounded-full p-2 text-cream/60 transition-colors hover:bg-cream/10 hover:text-cream"
              >
                <X className="h-5 w-5" />
              </button>
            </header>

            {items.length === 0 ? (
              <div className="flex flex-1 flex-col items-center justify-center gap-3 p-8 text-center">
                <ShoppingBag className="h-12 w-12 text-cream/20" />
                <p className="text-cream/60">Your cart is empty.</p>
                <Link
                  href="/menu"
                  onClick={onClose}
                  className={buttonVariants({ variant: "outline" })}
                >
                  Browse the menu
                </Link>
              </div>
            ) : (
              <>
                <div className="flex-1 space-y-4 overflow-y-auto p-5">
                  {items.map((item) => (
                    <div key={item.id} className="flex gap-3">
                      <SmartImage
                        src={item.image}
                        alt={item.name}
                        className="h-20 w-20 shrink-0 rounded-xl object-cover"
                      />
                      <div className="flex flex-1 flex-col">
                        <div className="flex justify-between gap-2">
                          <span className="font-medium text-cream">{item.name}</span>
                          <button
                            onClick={() => removeItem(item.id)}
                            aria-label={`Remove ${item.name}`}
                            className="text-cream/40 transition-colors hover:text-red-400"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                        <span className="text-sm text-gold">{formatPrice(item.price)}</span>
                        <div className="mt-auto flex items-center gap-2">
                          <button
                            onClick={() => updateQuantity(item.id, item.quantity - 1)}
                            aria-label="Decrease quantity"
                            className="flex h-7 w-7 items-center justify-center rounded-full border border-cream/20 text-cream/80 hover:border-gold hover:text-gold"
                          >
                            <Minus className="h-3.5 w-3.5" />
                          </button>
                          <span className="w-6 text-center text-sm text-cream">
                            {item.quantity}
                          </span>
                          <button
                            onClick={() => updateQuantity(item.id, item.quantity + 1)}
                            aria-label="Increase quantity"
                            className="flex h-7 w-7 items-center justify-center rounded-full border border-cream/20 text-cream/80 hover:border-gold hover:text-gold"
                          >
                            <Plus className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <footer className="border-t border-cream/10 p-5">
                  <div className="mb-4 flex items-center justify-between text-cream">
                    <span className="text-cream/70">Subtotal</span>
                    <span className="font-serif text-xl font-bold text-gold">
                      {formatPrice(subtotal())}
                    </span>
                  </div>
                  <Link
                    href="/checkout"
                    onClick={onClose}
                    className={buttonVariants({ size: "lg" }) + " w-full"}
                  >
                    Proceed to Checkout
                  </Link>
                </footer>
              </>
            )}
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
