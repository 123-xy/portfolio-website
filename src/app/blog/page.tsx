import type { Metadata } from "next";
import Link from "next/link";
import { ArrowUpRight, CalendarDays } from "lucide-react";
import { blogPosts } from "@/data/content";
import { SmartImage } from "@/components/ui/smart-image";
import { Badge } from "@/components/ui/badge";

export const metadata: Metadata = {
  title: "Blog",
  description:
    "Coffee tips, recipes, café news, events and promotions from the Premium Café team.",
};

export default function BlogPage() {
  return (
    <div className="pt-18">
      <section className="border-b border-cream/10 bg-coffee/20 py-16">
        <div className="container text-center">
          <span className="mb-3 inline-block text-sm font-medium uppercase tracking-[0.25em] text-gold">
            Stories &amp; brews
          </span>
          <h1 className="font-serif text-4xl font-bold text-cream sm:text-5xl md:text-6xl">
            The <span className="gold-text">Journal</span>
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-cream/70">
            Coffee tips, recipes and the latest happenings at Premium Café.
          </p>
        </div>
      </section>

      <section className="container grid gap-8 py-16 md:grid-cols-2 lg:grid-cols-3">
        {blogPosts.map((post) => (
          <Link
            key={post.slug}
            href={`/blog/${post.slug}`}
            className="group flex flex-col overflow-hidden rounded-3xl border border-cream/10 bg-coffee/30 transition-all hover:border-gold/40 hover:shadow-soft"
          >
            <div className="relative aspect-[16/10] overflow-hidden">
              <SmartImage
                src={post.image}
                alt={post.title}
                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
              />
              <Badge variant="bestseller" className="absolute left-3 top-3">
                {post.category}
              </Badge>
            </div>
            <div className="flex flex-1 flex-col p-6">
              <div className="mb-3 flex items-center gap-3 text-xs text-cream/50">
                <span className="flex items-center gap-1">
                  <CalendarDays className="h-3.5 w-3.5" />
                  {new Date(post.date).toLocaleDateString("en-IN", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                  })}
                </span>
                <span>•</span>
                <span>{post.readTime}</span>
              </div>
              <h2 className="mb-2 font-serif text-xl font-semibold text-cream group-hover:text-gold">
                {post.title}
              </h2>
              <p className="mb-4 flex-1 text-sm text-cream/60">{post.excerpt}</p>
              <span className="inline-flex items-center gap-1 text-sm font-medium text-gold">
                Read more <ArrowUpRight className="h-4 w-4" />
              </span>
            </div>
          </Link>
        ))}
      </section>
    </div>
  );
}
