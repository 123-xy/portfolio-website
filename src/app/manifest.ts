import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Premium Café",
    short_name: "PremiumCafé",
    description:
      "Luxury coffee, artisan food and unforgettable ambience. Order online, reserve a table, explore the menu.",
    start_url: "/",
    display: "standalone",
    background_color: "#1c110a",
    theme_color: "#1c110a",
    icons: [
      {
        src: "/icon.svg",
        sizes: "any",
        type: "image/svg+xml",
        purpose: "any",
      },
    ],
  };
}
