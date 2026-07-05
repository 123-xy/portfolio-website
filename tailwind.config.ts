import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1.5rem",
      screens: { "2xl": "1280px" },
    },
    extend: {
      height: { 13: "3.25rem", 18: "4.5rem" },
      spacing: { 13: "3.25rem", 18: "4.5rem" },
      colors: {
        // Luxury coffee palette
        espresso: "#1c110a",
        coffee: "#3a2318",
        mocha: "#5b3a29",
        caramel: "#a9754f",
        latte: "#c9a27e",
        cream: "#f6efe6",
        gold: "#c9a24b",
        "gold-soft": "#e3c988",
      },
      fontFamily: {
        serif: ["var(--font-playfair)", "Georgia", "serif"],
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "gold-gradient":
          "linear-gradient(135deg, #e3c988 0%, #c9a24b 50%, #a9754f 100%)",
        "coffee-radial":
          "radial-gradient(ellipse at top, rgba(90,58,41,0.35), transparent 60%)",
      },
      boxShadow: {
        gold: "0 10px 40px -12px rgba(201,162,75,0.45)",
        soft: "0 20px 50px -20px rgba(28,17,10,0.45)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(24px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-12px)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.7s ease-out forwards",
        float: "float 6s ease-in-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
