import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { Providers } from "@/app/providers";
import { env } from "@/shared/lib/env";
import "@/app/globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });

export const metadata: Metadata = {
  title: {
    default: `${env.NEXT_PUBLIC_APP_NAME} — Co-Applicant Verification`,
    template: `%s · ${env.NEXT_PUBLIC_APP_NAME}`,
  },
  description:
    "AI-assisted loan co-applicant verification: face match, spoken consent, intent analysis, and risk scoring with human officer review.",
  applicationName: env.NEXT_PUBLIC_APP_NAME,
  appleWebApp: { capable: true, statusBarStyle: "default", title: env.NEXT_PUBLIC_APP_NAME },
  formatDetection: { telephone: false },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f5f7fb" },
    { media: "(prefers-color-scheme: dark)", color: "#0d1220" },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans`}>
        <Providers>
          {/* Phone-shaped frame: full-bleed on mobile, centered device on desktop. */}
          <div className="app-frame">{children}</div>
        </Providers>
      </body>
    </html>
  );
}
