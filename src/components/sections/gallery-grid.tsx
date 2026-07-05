"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { galleryImages } from "@/data/content";
import { SmartImage } from "@/components/ui/smart-image";
import { cn } from "@/lib/utils";

const filters = ["All", "Interior", "Food", "Coffee", "Events"];

export function GalleryGrid() {
  const [filter, setFilter] = useState("All");
  const [lightbox, setLightbox] = useState<string | null>(null);

  const images =
    filter === "All"
      ? galleryImages
      : galleryImages.filter((i) => i.category === filter);

  return (
    <section className="container py-16">
      <div className="mb-10 flex flex-wrap justify-center gap-2">
        {filters.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              "rounded-full px-5 py-2 text-sm font-medium transition-all",
              filter === f
                ? "bg-gold-gradient text-espresso shadow-gold"
                : "border border-cream/15 text-cream/70 hover:border-gold/40 hover:text-cream"
            )}
          >
            {f}
          </button>
        ))}
      </div>

      <motion.div
        layout
        className="columns-2 gap-4 space-y-4 md:columns-3 lg:columns-4"
      >
        <AnimatePresence>
          {images.map((image, i) => (
            <motion.button
              layout
              key={image.src}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ delay: (i % 6) * 0.04 }}
              onClick={() => setLightbox(image.src)}
              className="group relative block w-full break-inside-avoid overflow-hidden rounded-2xl"
            >
              <SmartImage
                src={image.src}
                alt={image.alt}
                className="w-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
              <div className="absolute inset-0 flex items-end bg-gradient-to-t from-espresso/70 to-transparent p-4 opacity-0 transition-opacity group-hover:opacity-100">
                <span className="text-sm font-medium text-cream">{image.alt}</span>
              </div>
            </motion.button>
          ))}
        </AnimatePresence>
      </motion.div>

      <AnimatePresence>
        {lightbox && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setLightbox(null)}
            className="fixed inset-0 z-[60] flex items-center justify-center bg-espresso/90 p-6 backdrop-blur-md"
          >
            <button
              aria-label="Close"
              className="absolute right-6 top-6 rounded-full bg-cream/10 p-3 text-cream hover:bg-cream/20"
            >
              <X className="h-6 w-6" />
            </button>
            <motion.img
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              src={lightbox}
              alt="Gallery preview"
              className="max-h-[85vh] max-w-full rounded-2xl object-contain shadow-soft"
              onClick={(e) => e.stopPropagation()}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
