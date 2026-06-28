import type { Metadata, Viewport } from 'next'
import './globals.css'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import { ThemeProvider } from '@/components/ThemeProvider'

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0f172a' },
  ],
}

export const metadata: Metadata = {
  metadataBase: new URL('https://nexacore.com'),
  title: {
    default: 'NexaCore — Modern Business Solutions',
    template: '%s | NexaCore',
  },
  description:
    'NexaCore delivers cutting-edge digital solutions — web development, design, and strategy — to help your business thrive in the modern world.',
  keywords: ['business', 'web development', 'digital agency', 'design', 'strategy', 'technology'],
  authors: [{ name: 'NexaCore Team' }],
  creator: 'NexaCore',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://nexacore.com',
    title: 'NexaCore — Modern Business Solutions',
    description: 'Cutting-edge digital solutions for modern businesses.',
    siteName: 'NexaCore',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'NexaCore — Modern Business Solutions',
    description: 'Cutting-edge digital solutions for modern businesses.',
    creator: '@nexacore',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, 'max-image-preview': 'large' },
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-50 transition-colors duration-300">
        <ThemeProvider>
          <Navbar />
          <main>{children}</main>
          <Footer />
        </ThemeProvider>
      </body>
    </html>
  )
}
