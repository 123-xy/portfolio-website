import type { Metadata } from "next";
import { Eye, HeartHandshake, Sprout, Target } from "lucide-react";
import { team, timeline } from "@/data/content";
import { SectionHeading } from "@/components/ui/section-heading";
import { SmartImage } from "@/components/ui/smart-image";

export const metadata: Metadata = {
  title: "About",
  description:
    "The story of Premium Café — our founder's journey, our team, mission, vision and our commitment to ethically sourced, expertly roasted coffee.",
};

const values = [
  {
    icon: Target,
    title: "Our Mission",
    text: "To craft the finest coffee experience while championing the farmers and communities behind every bean.",
  },
  {
    icon: Eye,
    title: "Our Vision",
    text: "A world where great coffee brings people together and every cup is sustainable, ethical and unforgettable.",
  },
  {
    icon: HeartHandshake,
    title: "Quality Promise",
    text: "Small-batch roasting, rigorous cupping and freshness guaranteed — or your next cup is on us.",
  },
  {
    icon: Sprout,
    title: "Coffee Sourcing",
    text: "Direct-trade relationships with farms across four continents ensure fairness and traceability.",
  },
];

export default function AboutPage() {
  return (
    <div className="pt-18">
      {/* Hero */}
      <section className="relative overflow-hidden py-24">
        <div className="absolute inset-0 -z-10">
          <SmartImage
            src="https://images.unsplash.com/photo-1445116572660-236099ec97a0?auto=format&fit=crop&w=1920&q=80"
            alt="Café ambience"
            className="h-full w-full object-cover opacity-30"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-espresso/80 to-espresso" />
        </div>
        <div className="container text-center">
          <span className="mb-3 inline-block text-sm font-medium uppercase tracking-[0.25em] text-gold">
            Since 2013
          </span>
          <h1 className="mx-auto max-w-3xl font-serif text-4xl font-bold leading-tight text-cream text-balance sm:text-5xl md:text-6xl">
            More than coffee — a <span className="gold-text">craft</span> and a
            community
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-cream/70">
            Premium Café was born from a simple belief: that a truly great cup of
            coffee can transform an ordinary day into something memorable.
          </p>
        </div>
      </section>

      {/* Story + Founder */}
      <section className="container grid items-center gap-12 py-20 lg:grid-cols-2">
        <SmartImage
          src="https://images.unsplash.com/photo-1559496417-e7f25cb247f3?auto=format&fit=crop&w=800&q=80"
          alt="Founder pouring coffee"
          className="aspect-[4/5] w-full rounded-3xl object-cover shadow-soft"
        />
        <div>
          <SectionHeading
            align="left"
            eyebrow="A message from our founder"
            title="It started with one perfect cup"
            className="mx-0"
          />
          <p className="mt-5 leading-relaxed text-cream/70">
            &ldquo;I grew up watching my grandmother roast coffee over an open
            flame, filling the house with an aroma I&apos;ve chased ever since.
            Premium Café is my love letter to that memory — a place where
            tradition meets craft, and every guest is family.&rdquo;
          </p>
          <p className="mt-4 leading-relaxed text-cream/70">
            Today we roast over 40 signature blends, serve tens of thousands of
            guests, and remain as obsessed with quality as we were on day one.
          </p>
          <div className="mt-6">
            <p className="font-serif text-xl font-semibold text-gold">
              Isabella Rossi
            </p>
            <p className="text-sm text-cream/60">Founder &amp; Head Roaster</p>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="border-y border-cream/10 bg-coffee/20 py-20">
        <div className="container">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {values.map((v) => {
              const Icon = v.icon;
              return (
                <div
                  key={v.title}
                  className="rounded-3xl border border-cream/10 bg-espresso/40 p-7"
                >
                  <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gold-gradient text-espresso">
                    <Icon className="h-7 w-7" />
                  </div>
                  <h3 className="mb-2 font-serif text-lg font-semibold text-cream">
                    {v.title}
                  </h3>
                  <p className="text-sm leading-relaxed text-cream/60">{v.text}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="container py-24">
        <SectionHeading eyebrow="Our journey" title="A Decade of Craft" />
        <div className="mt-14 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {timeline.map((t) => (
            <div key={t.year} className="relative">
              <div className="mb-4 flex items-center gap-3">
                <span className="flex h-12 w-12 items-center justify-center rounded-full border border-gold/40 font-serif font-bold text-gold">
                  {t.year.slice(2)}
                </span>
                <span className="font-serif text-2xl font-bold text-cream">
                  {t.year}
                </span>
              </div>
              <h3 className="mb-1 font-semibold text-cream">{t.title}</h3>
              <p className="text-sm text-cream/60">{t.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Team */}
      <section className="border-t border-cream/10 bg-coffee/20 py-24">
        <div className="container">
          <SectionHeading
            eyebrow="The people behind the cup"
            title="Meet Our Team"
            subtitle="Passionate craftspeople dedicated to your perfect coffee moment."
          />
          <div className="mt-12 grid gap-8 sm:grid-cols-3">
            {team.map((member) => (
              <div key={member.name} className="text-center">
                <div className="relative mx-auto mb-5 h-48 w-48 overflow-hidden rounded-full border-2 border-gold/30">
                  <SmartImage
                    src={member.avatar}
                    alt={member.name}
                    className="h-full w-full object-cover"
                  />
                </div>
                <h3 className="font-serif text-xl font-semibold text-cream">
                  {member.name}
                </h3>
                <p className="text-sm text-gold">{member.role}</p>
                <p className="mt-2 text-sm text-cream/60">{member.bio}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
