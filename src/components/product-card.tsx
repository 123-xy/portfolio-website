"use client";

import { motion } from "framer-motion";
import { Plus, Star, Flame } from "lucide-react";
import { toast } from "sonner";
import type { MenuItem } from "@/lib/types";
import { useCart } from "@/store/cart";
import { formatPrice } from "@/lib/utils";
import { SmartImage } from "@/components/ui/smart-image";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function ProductCard({ item, index = 0 }: { item: MenuItem; index?: number }) {
  const addItem = useCart((s) => s.addItem);

  return (
    <motion.article
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.5, delay: (index % 4) * 0.08 }}
      className="group relative flex flex-col overflow-hidden rounded-3xl border border-cream/10 bg-coffee/40 backdrop-blur-sm transition-all duration-300 hover:border-gold/40 hover:shadow-soft"
    >
      <div className="relative aspect-[4/3] overflow-hidden">
        <SmartImage
          src={item.image}
          alt={item.name}
          className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-espresso/80 via-transparent to-transparent" />
        <div className="absolute left-3 top-3 flex flex-wrap gap-1.5">
          {item.bestseller && (
            <Badge variant="bestseller">
              <Flame className="h-3 w-3" /> Bestseller
            </Badge>
          )}
          <Badge variant={item.veg ? "veg" : "nonveg"}>
            {item.veg ? "Veg" : "Non-Veg"}
          </Badge>
        </div>
        <div className="absolute bottom-3 right-3 flex items-center gap-1 rounded-full bg-espresso/70 px-2.5 py-1 text-xs font-medium text-gold backdrop-blur-sm">
          <Star className="h-3 w-3 fill-gold text-gold" /> {item.rating}
        </div>
      </div>

      <div className="flex flex-1 flex-col p-5">
        <div className="mb-1 flex items-start justify-between gap-3">
          <h3 className="font-serif text-lg font-semibold text-cream">{item.name}</h3>
          <span className="shrink-0 font-serif text-lg font-bold text-gold">
            {formatPrice(item.price)}
          </span>
        </div>
        <p className="mb-3 line-clamp-2 text-sm text-cream/60">{item.description}</p>
        <div className="mb-4 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-cream/50">
          <span>{item.calories} cal</span>
          <span className="text-cream/25">•</span>
          <span className="line-clamp-1">{item.ingredients.slice(0, 3).join(", ")}</span>
        </div>
        <Button
          size="sm"
          className="mt-auto w-full"
          onClick={() => {
            addItem(item);
            toast.success(`${item.name} added to cart`);
          }}
        >
          <Plus className="h-4 w-4" /> Add to Cart
        </Button>
      </div>
    </motion.article>
  );
}
