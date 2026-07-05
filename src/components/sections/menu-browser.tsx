"use client";

import { useMemo, useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";
import { menu, categories } from "@/data/menu";
import { ProductCard } from "@/components/product-card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type SortKey = "popular" | "price-asc" | "price-desc" | "rating";

const sortOptions: { key: SortKey; label: string }[] = [
  { key: "popular", label: "Most Popular" },
  { key: "price-asc", label: "Price: Low to High" },
  { key: "price-desc", label: "Price: High to Low" },
  { key: "rating", label: "Top Rated" },
];

export function MenuBrowser() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string>("All");
  const [sort, setSort] = useState<SortKey>("popular");
  const [vegOnly, setVegOnly] = useState(false);

  const filtered = useMemo(() => {
    let items = menu.filter((item) => {
      const matchesCategory = category === "All" || item.category === category;
      const matchesQuery =
        !query ||
        item.name.toLowerCase().includes(query.toLowerCase()) ||
        item.description.toLowerCase().includes(query.toLowerCase()) ||
        item.ingredients.some((i) =>
          i.toLowerCase().includes(query.toLowerCase())
        );
      const matchesVeg = !vegOnly || item.veg;
      return matchesCategory && matchesQuery && matchesVeg;
    });

    items = [...items].sort((a, b) => {
      switch (sort) {
        case "price-asc":
          return a.price - b.price;
        case "price-desc":
          return b.price - a.price;
        case "rating":
          return b.rating - a.rating;
        default:
          return (b.bestseller ? 1 : 0) - (a.bestseller ? 1 : 0);
      }
    });
    return items;
  }, [query, category, sort, vegOnly]);

  return (
    <section className="container py-16">
      {/* Controls */}
      <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="relative w-full lg:max-w-sm">
          <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-cream/40" />
          <Input
            placeholder="Search the menu..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pl-11"
            aria-label="Search menu"
          />
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => setVegOnly((v) => !v)}
            className={cn(
              "rounded-full border px-4 py-2 text-sm font-medium transition-colors",
              vegOnly
                ? "border-green-500/40 bg-green-500/15 text-green-400"
                : "border-cream/15 text-cream/70 hover:border-cream/30"
            )}
          >
            Veg Only
          </button>
          <div className="flex items-center gap-2 rounded-full border border-cream/15 px-3 py-1.5">
            <SlidersHorizontal className="h-4 w-4 text-cream/40" />
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value as SortKey)}
              aria-label="Sort menu"
              className="bg-transparent text-sm text-cream/80 focus:outline-none [&>option]:bg-coffee"
            >
              {sortOptions.map((opt) => (
                <option key={opt.key} value={opt.key}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Category chips */}
      <div className="mb-10 flex flex-wrap gap-2">
        {["All", ...categories].map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={cn(
              "rounded-full px-4 py-2 text-sm font-medium transition-all",
              category === cat
                ? "bg-gold-gradient text-espresso shadow-gold"
                : "border border-cream/15 text-cream/70 hover:border-gold/40 hover:text-cream"
            )}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Grid */}
      {filtered.length > 0 ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((item, i) => (
            <ProductCard key={item.id} item={item} index={i} />
          ))}
        </div>
      ) : (
        <div className="rounded-3xl border border-cream/10 bg-coffee/20 py-20 text-center">
          <p className="font-serif text-2xl text-cream">No items found</p>
          <p className="mt-2 text-cream/60">
            Try a different search or category.
          </p>
        </div>
      )}
    </section>
  );
}
