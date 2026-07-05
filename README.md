# Premium Café ☕

A modern, premium, fully-responsive café website for a high-end coffee shop — built with **Next.js 15 (App Router)**, **TypeScript**, **Tailwind CSS** and **Framer Motion**. Luxury design, smooth animations, online ordering, reservations and more.

> **Live-runnable out of the box.** The site works fully with bundled sample data — no external accounts required. Add API keys in `.env.local` to switch on real payments, database, maps and email.

---

## ✨ Features

**Pages**
- **Home** — full-screen hero, featured coffee, best sellers, reviews, about preview, stats, special offers, why-choose-us, gallery preview, Instagram feed, newsletter
- **Menu** — 18 categories, live search, category filter, sorting, veg-only toggle, full product cards (image, description, ingredients, price, calories, rating, veg/non-veg & bestseller badges, add-to-cart)
- **About** — story, founder's message, mission, vision, quality promise, sourcing, timeline, team
- **Gallery** — filterable masonry grid with lightbox
- **Blog** — article listing + individual post pages (SSG)
- **Reservation** — validated booking form (dine-in)
- **Contact** — validated contact form, map embed, hours, WhatsApp/phone/email, FAQ
- **Checkout** — full cart flow: quantity, remove, coupon codes, GST, delivery fee, order type (delivery / pickup / dine-in), payment selection, order confirmation with ETA

**Commerce & UX**
- Persistent cart (Zustand + `localStorage`) with slide-out drawer
- Coupon engine, tax (GST) & delivery calculation
- Dark / light mode (`next-themes`)
- Toast notifications (`sonner`)
- Form validation (`react-hook-form` + `zod`)
- Graceful image fallbacks, loading skeletons, custom 404 & error pages

**SEO & Performance**
- Per-page metadata, Open Graph, Twitter cards
- `sitemap.xml`, `robots.txt`, JSON-LD structured data (`CafeOrCoffeeShop`)
- PWA manifest, static generation, lazy-loaded images, accessible markup

---

## 🧱 Tech Stack

| Concern | Choice |
| --- | --- |
| Framework | Next.js 15 (App Router) + React 19 |
| Language | TypeScript |
| Styling | Tailwind CSS + custom luxury design tokens |
| Animation | Framer Motion |
| Icons | Lucide React |
| State | Zustand (persisted cart) |
| Forms | React Hook Form + Zod |
| Theming | next-themes |
| Toasts | Sonner |

**Integration-ready** (scaffolded, wire your keys): Supabase (DB + Auth), Stripe / Razorpay (payments), Cloudinary (images), Google Maps, Resend (email).

---

## 🚀 Getting Started

```bash
# 1. Install dependencies
npm install

# 2. (optional) configure integrations
cp .env.example .env.local     # fill in any keys you have

# 3. Run the dev server
npm run dev                     # http://localhost:3000

# Production build
npm run build && npm start
```

Requires **Node.js 18.18+** (tested on Node 22).

---

## 📁 Project Structure

```
src/
├── app/                      # App Router pages & routes
│   ├── layout.tsx            # Root layout, fonts, metadata, JSON-LD
│   ├── page.tsx              # Home
│   ├── menu/                 # Menu page
│   ├── about/                # About page
│   ├── gallery/              # Gallery page
│   ├── blog/                 # Blog listing + [slug] posts
│   ├── reservation/          # Reservation page
│   ├── contact/              # Contact page
│   ├── checkout/             # Checkout / ordering flow
│   ├── sitemap.ts            # Dynamic sitemap
│   ├── robots.ts             # robots.txt
│   ├── manifest.ts           # PWA manifest
│   ├── not-found.tsx         # 404
│   ├── error.tsx             # Error boundary
│   └── loading.tsx           # Loading skeleton
├── components/
│   ├── layout/               # Header, Footer, CartDrawer, Providers
│   ├── sections/             # Page sections (hero, home blocks, forms…)
│   ├── ui/                   # Reusable primitives (button, input, badge…)
│   └── product-card.tsx
├── data/                     # Sample menu & content data
├── store/                    # Zustand cart store
└── lib/                      # types & utils
```

---

## 🔌 Wiring Up Integrations

The app is deliberately structured so each integration is a drop-in.

| Integration | Where to connect |
| --- | --- |
| **Supabase** (DB/Auth) | Replace `src/data/*` reads with Supabase queries; persist reservations in `reservation-form.tsx`, orders in `checkout.tsx`. See suggested schema below. |
| **Stripe / Razorpay** | `checkout.tsx` `onSubmit` — swap the simulated payment for a real payment intent + API route. |
| **Cloudinary** | Replace Unsplash URLs with Cloudinary; `next.config.mjs` already allows the host. |
| **Google Maps** | `contact/page.tsx` — swap the OpenStreetMap embed for the Google Maps Embed API using `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`. |
| **Email** | `contact-form.tsx` & checkout — post to an API route that calls Resend. |

### Suggested database schema (Supabase / Postgres)

```sql
create table products (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  ingredients text[],
  price integer not null,          -- in paise/cents
  calories integer,
  rating numeric(2,1) default 0,
  category text not null,
  image text,
  veg boolean default true,
  bestseller boolean default false,
  featured boolean default false,
  created_at timestamptz default now()
);

create table orders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users,
  order_type text check (order_type in ('delivery','pickup','dinein')),
  items jsonb not null,
  subtotal integer, discount integer, gst integer,
  delivery_fee integer, total integer,
  coupon text, status text default 'pending',
  address text, phone text, email text, instructions text,
  created_at timestamptz default now()
);

create table reservations (
  id uuid primary key default gen_random_uuid(),
  name text, phone text, email text,
  guests int, reserved_date date, reserved_time text,
  requests text, status text default 'pending',
  created_at timestamptz default now()
);

create table coupons (
  code text primary key,
  percent int not null,
  label text, active boolean default true
);
```

---

## 🌐 Environment Variables

See [`.env.example`](./.env.example). All are optional — the site runs on sample data without them. Keys cover Supabase, Stripe, Razorpay, Cloudinary, Google Maps and email.

---

## ☁️ Deployment

Optimised for **Vercel**:

1. Push this repo to GitHub.
2. Import the project into [Vercel](https://vercel.com/new).
3. Add environment variables from `.env.example` in the Vercel dashboard.
4. Deploy — Vercel auto-detects Next.js.

Also runs anywhere Node runs:

```bash
npm run build
npm start          # serves the production build on :3000
```

Or containerise with a standard Node 20+ image running `npm run build && npm start`.

---

## 🎨 Design System

Luxury coffee palette defined in `tailwind.config.ts`:

- **espresso** `#1c110a` · **coffee** `#3a2318` · **mocha** `#5b3a29`
- **caramel** `#a9754f` · **latte** `#c9a27e` · **cream** `#f6efe6`
- **gold** `#c9a24b` (accents & CTAs)

Typography: **Playfair Display** (serif headings) + **Inter** (body). Glassmorphism, rounded cards, gold-gradient CTAs and Framer Motion micro-interactions throughout.

---

## 📌 Scope Notes

This repository delivers a **production-quality front-end** with a complete, working ordering and reservation experience on sample data. Backend-heavy features from the original brief — live payment processing, Supabase auth (Google login / OTP), the admin dashboard, real-time delivery tracking, loyalty/referrals, and multi-language — are **scaffolded with clear extension points** (documented above) rather than fully wired to third-party accounts, since those require live credentials and services. The architecture is intentionally modular so each can be added incrementally.

---

Crafted with ☕ & care.
