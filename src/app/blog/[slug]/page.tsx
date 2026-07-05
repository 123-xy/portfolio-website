import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, CalendarDays } from "lucide-react";
import { blogPosts } from "@/data/content";
import { SmartImage } from "@/components/ui/smart-image";
import { Badge } from "@/components/ui/badge";

export function generateStaticParams() {
  return blogPosts.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const post = blogPosts.find((p) => p.slug === slug);
  if (!post) return { title: "Article not found" };
  return { title: post.title, description: post.excerpt };
}

export default async function BlogPostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = blogPosts.find((p) => p.slug === slug);
  if (!post) notFound();

  return (
    <article className="pt-18">
      <div className="container max-w-3xl py-16">
        <Link
          href="/blog"
          className="mb-8 inline-flex items-center gap-2 text-sm text-cream/60 transition-colors hover:text-gold"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Journal
        </Link>

        <Badge variant="bestseller" className="mb-4">
          {post.category}
        </Badge>
        <h1 className="font-serif text-3xl font-bold leading-tight text-cream sm:text-4xl md:text-5xl">
          {post.title}
        </h1>
        <div className="mt-4 flex items-center gap-3 text-sm text-cream/50">
          <span className="flex items-center gap-1">
            <CalendarDays className="h-4 w-4" />
            {new Date(post.date).toLocaleDateString("en-IN", {
              day: "numeric",
              month: "long",
              year: "numeric",
            })}
          </span>
          <span>•</span>
          <span>{post.readTime}</span>
        </div>

        <SmartImage
          src={post.image}
          alt={post.title}
          className="mt-8 aspect-[16/9] w-full rounded-3xl object-cover shadow-soft"
        />

        <div className="prose-invert mt-10 space-y-5 text-lg leading-relaxed text-cream/80">
          <p className="text-xl text-cream/90">{post.excerpt}</p>
          <p>
            At Premium Café, we believe the details make all the difference. From
            the origin of the bean to the temperature of the water, every variable
            is an opportunity to elevate your cup.
          </p>
          <p>
            Our baristas spend months perfecting their craft, learning to read the
            subtle cues that separate a good coffee from a great one. In this piece
            we share the philosophy and the practical steps you can take to bring a
            little of that magic home.
          </p>
          <h2 className="font-serif text-2xl font-bold text-cream">
            The essentials
          </h2>
          <p>
            Start with freshly roasted beans, grind just before brewing, and mind
            your ratios. A kitchen scale and a thermometer are the two most
            underrated tools in any home setup.
          </p>
          <p>
            Ready to taste the difference for yourself? Visit us, or order your
            favourites online and let us bring the café experience to your door.
          </p>
        </div>

        <div className="mt-12 rounded-3xl border border-gold/25 bg-coffee/30 p-8 text-center">
          <h3 className="font-serif text-2xl font-bold text-cream">
            Craving a cup?
          </h3>
          <p className="mt-2 text-cream/70">
            Explore our menu and order in a few taps.
          </p>
          <Link
            href="/menu"
            className="mt-5 inline-flex h-11 items-center justify-center rounded-full bg-gold-gradient px-6 font-semibold text-espresso shadow-gold"
          >
            Order Now
          </Link>
        </div>
      </div>
    </article>
  );
}
