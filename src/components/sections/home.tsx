"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Bike,
  Coffee,
  Flame,
  Leaf,
  Quote,
  Star,
  Instagram,
  ArrowRight,
} from "lucide-react";
import { bestSellers, featuredItems } from "@/data/menu";
import { offers, reviews, stats, whyChooseUs, galleryImages } from "@/data/content";
import { ProductCard } from "@/components/product-card";
import { SectionHeading } from "@/components/ui/section-heading";
import { SmartImage } from "@/components/ui/smart-image";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";

const icons = { Leaf, Flame, Coffee, Bike } as const;

export function FeaturedCoffee() {
  return (
    <section className="container py-24">
      <SectionHeading
        eyebrow="Handpicked for you"
        title="Featured Coffee"
        subtitle="Our roaster's current favourites — limited blends crafted to impress."
      />
      <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {featuredItems.map((item, i) => (
          <ProductCard key={item.id} item={item} index={i} />
        ))}
      </div>
    </section>
  );
}

export function BestSellers() {
  return (
    <section className="border-y border-cream/10 bg-coffee/20 py-24">
      <div className="container">
        <div className="flex flex-col items-center justify-between gap-6 sm:flex-row sm:items-end">
          <SectionHeading
            align="left"
            eyebrow="Loved by everyone"
            title="Best Selling Items"
            className="mx-0"
          />
          <Link
            href="/menu"
            className={buttonVariants({ variant: "outline" }) + " shrink-0"}
          >
            View Full Menu <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {bestSellers.slice(0, 4).map((item, i) => (
            <ProductCard key={item.id} item={item} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}

export function Stats() {
  return (
    <section className="container py-20">
      <div className="grid grid-cols-2 gap-6 rounded-3xl border border-gold/20 bg-gradient-to-br from-coffee/50 to-espresso/50 p-10 backdrop-blur-sm lg:grid-cols-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="text-center"
          >
            <p className="font-serif text-4xl font-bold text-gold lg:text-5xl">
              {stat.value}
            </p>
            <p className="mt-2 text-sm uppercase tracking-wider text-cream/60">
              {stat.label}
            </p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

export function WhyChooseUs() {
  return (
    <section className="container py-24">
      <SectionHeading
        eyebrow="The Premium difference"
        title="Why Choose Us"
        subtitle="Every detail, from bean to cup, is obsessed over so you don't have to."
      />
      <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {whyChooseUs.map((item, i) => {
          const Icon = icons[item.icon as keyof typeof icons];
          return (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ delay: i * 0.08 }}
              className="group rounded-3xl border border-cream/10 bg-coffee/30 p-7 transition-all hover:border-gold/40 hover:shadow-soft"
            >
              <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gold-gradient text-espresso transition-transform group-hover:scale-110">
                <Icon className="h-7 w-7" />
              </div>
              <h3 className="mb-2 font-serif text-xl font-semibold text-cream">
                {item.title}
              </h3>
              <p className="text-sm leading-relaxed text-cream/60">
                {item.description}
              </p>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}

export function Offers() {
  return (
    <section className="border-y border-cream/10 bg-coffee/20 py-24">
      <div className="container">
        <SectionHeading
          eyebrow="Limited time"
          title="Special Offers"
          subtitle="Treat yourself for less with our current promotions."
        />
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {offers.map((offer, i) => (
            <motion.div
              key={offer.title}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="relative overflow-hidden rounded-3xl border border-gold/25 bg-gradient-to-br from-mocha/60 to-espresso p-7"
            >
              <div className="absolute right-0 top-0 h-24 w-24 -translate-y-8 translate-x-8 rounded-full bg-gold/20 blur-2xl" />
              <Badge variant="bestseller" className="mb-4">
                {offer.badge}
              </Badge>
              <h3 className="mb-2 font-serif text-xl font-semibold text-cream">
                {offer.title}
              </h3>
              <p className="mb-5 text-sm text-cream/60">{offer.description}</p>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-cream/50">Use code</span>
                <code className="rounded-lg border border-dashed border-gold/40 bg-gold/10 px-2.5 py-1 font-mono font-semibold text-gold">
                  {offer.code}
                </code>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function Reviews() {
  return (
    <section className="container py-24">
      <SectionHeading
        eyebrow="Loved & trusted"
        title="What Our Guests Say"
        subtitle="Real words from the people who make Premium Café their second home."
      />
      <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {reviews.map((review, i) => (
          <motion.figure
            key={review.name}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ delay: i * 0.08 }}
            className="flex flex-col rounded-3xl border border-cream/10 bg-coffee/30 p-6"
          >
            <Quote className="mb-3 h-8 w-8 text-gold/40" />
            <blockquote className="flex-1 text-sm leading-relaxed text-cream/80">
              “{review.text}”
            </blockquote>
            <div className="mt-4 flex gap-0.5">
              {Array.from({ length: review.rating }).map((_, s) => (
                <Star key={s} className="h-4 w-4 fill-gold text-gold" />
              ))}
            </div>
            <figcaption className="mt-4 flex items-center gap-3 border-t border-cream/10 pt-4">
              <SmartImage
                src={review.avatar}
                alt={review.name}
                className="h-10 w-10 rounded-full object-cover"
              />
              <div>
                <p className="text-sm font-semibold text-cream">{review.name}</p>
                <p className="text-xs text-cream/50">{review.role}</p>
              </div>
            </figcaption>
          </motion.figure>
        ))}
      </div>
    </section>
  );
}

export function AboutPreview() {
  return (
    <section className="border-y border-cream/10 bg-coffee/20 py-24">
      <div className="container grid items-center gap-12 lg:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="relative"
        >
          <SmartImage
            src="https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=800&q=80"
            alt="Inside Premium Café"
            className="aspect-[4/5] w-full rounded-3xl object-cover shadow-soft"
          />
          <div className="absolute -bottom-6 -right-6 hidden rounded-3xl border border-gold/30 bg-espresso p-6 shadow-gold sm:block">
            <p className="font-serif text-3xl font-bold text-gold">12+</p>
            <p className="text-sm text-cream/60">Years of craft</p>
          </div>
        </motion.div>
        <div>
          <SectionHeading
            align="left"
            eyebrow="Our story"
            title="A passion for coffee, perfected over a decade"
            className="mx-0"
          />
          <p className="mt-5 leading-relaxed text-cream/70">
            What began as a six-seat roastery has grown into a beloved destination
            for coffee connoisseurs. We travel the world to source the finest
            beans, roast them in small batches, and serve them with the care they
            deserve.
          </p>
          <p className="mt-4 leading-relaxed text-cream/70">
            Every cup tells a story of the farmers who grew it, the roasters who
            coaxed out its flavour, and the baristas who bring it to life.
          </p>
          <Link
            href="/about"
            className={buttonVariants({ variant: "outline" }) + " mt-8"}
          >
            Read Our Story <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </section>
  );
}

export function GalleryPreview() {
  return (
    <section className="container py-24">
      <SectionHeading
        eyebrow="A feast for the eyes"
        title="Gallery Preview"
        subtitle="Step inside the Premium Café experience."
      />
      <div className="mt-12 grid grid-cols-2 gap-4 md:grid-cols-4">
        {galleryImages.slice(0, 8).map((image, i) => (
          <motion.div
            key={image.src}
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: (i % 4) * 0.06 }}
            className={`group relative overflow-hidden rounded-2xl ${
              i === 0 || i === 5 ? "row-span-2" : ""
            }`}
          >
            <SmartImage
              src={image.src}
              alt={image.alt}
              className="h-full min-h-40 w-full object-cover transition-transform duration-500 group-hover:scale-110"
            />
          </motion.div>
        ))}
      </div>
      <div className="mt-10 text-center">
        <Link href="/gallery" className={buttonVariants({ variant: "outline" })}>
          Explore Gallery <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </section>
  );
}

export function InstagramFeed() {
  return (
    <section className="border-t border-cream/10 bg-coffee/20 py-24">
      <div className="container">
        <SectionHeading
          eyebrow="@premiumcafe"
          title="Follow the Journey"
          subtitle="Tag us #PremiumCafe to be featured on our feed."
        />
        <div className="mt-12 grid grid-cols-3 gap-3 sm:grid-cols-6">
          {galleryImages.slice(0, 6).map((image, i) => (
            <a
              key={i}
              href="#"
              className="group relative aspect-square overflow-hidden rounded-2xl"
            >
              <SmartImage
                src={image.src}
                alt="Instagram post"
                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
              />
              <div className="absolute inset-0 flex items-center justify-center bg-espresso/60 opacity-0 transition-opacity group-hover:opacity-100">
                <Instagram className="h-6 w-6 text-gold" />
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
