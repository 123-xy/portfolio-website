import type { Metadata } from 'next'
import Hero from '@/components/sections/Hero'
import ServicesSection from '@/components/sections/Services'
import Testimonials from '@/components/sections/Testimonials'
import FAQ from '@/components/sections/FAQ'
import CTA from '@/components/sections/CTA'

export const metadata: Metadata = {
  title: 'NexaCore — Modern Business Solutions',
  description:
    'Build the future faster with NexaCore. Expert web development, design, and digital strategy for ambitious businesses.',
}

export default function HomePage() {
  return (
    <>
      <Hero />
      <ServicesSection />
      <Testimonials />
      <FAQ />
      <CTA />
    </>
  )
}
