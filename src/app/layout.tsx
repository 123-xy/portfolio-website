import type { Metadata, Viewport } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/layout/providers";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Premium Café — Luxury Coffee, Crafted to Perfection",
    template: "%s | Premium Café",
  },
  description:
    "Premium Café serves luxury single-origin coffee, artisan food and unforgettable ambience. Order online for delivery, reserve a table or explore our menu.",
  keywords: [
    "premium cafe",
    "luxury coffee",
    "coffee shop",
    "online coffee order",
    "cafe near me",
    "specialty coffee",
  ],
  authors: [{ name: "Premium Café" }],
  openGraph: {
    type: "website",
    title: "Premium Café — Luxury Coffee, Crafted to Perfection",
    description:
      "Luxury single-origin coffee, artisan food and unforgettable ambience. Order online, reserve a table, explore the menu.",
    siteName: "Premium Café",
    url: siteUrl,
  },
  twitter: {
    card: "summary_large_image",
    title: "Premium Café",
    description: "Luxury coffee, crafted to perfection.",
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: "#1c110a",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "CafeOrCoffeeShop",
    name: "Premium Café",
    description:
      "Luxury single-origin coffee, artisan food and unforgettable ambience.",
    url: siteUrl,
    telephone: "+91 98765 43210",
    priceRange: "₹₹",
    servesCuisine: ["Coffee", "Continental", "Desserts"],
    address: {
      "@type": "PostalAddress",
      streetAddress: "42 Roasters Lane",
      addressLocality: "Bengaluru",
      addressCountry: "IN",
    },
    openingHours: ["Mo-Fr 07:00-23:00", "Sa 08:00-24:00", "Su 08:00-22:00"],
    aggregateRating: {
      "@type": "AggregateRating",
      ratingValue: "4.9",
      reviewCount: "85000",
    },
  };

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${playfair.variable}`}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <Providers>
          <Header />
          <main className="min-h-screen">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
