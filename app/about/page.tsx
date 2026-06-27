import type { Metadata } from 'next'
import AboutContent from './AboutContent'

export const metadata: Metadata = {
  title: 'About Us',
  description: 'Learn about NexaCore — our mission, team, and values that drive everything we build.',
}

export default function AboutPage() {
  return <AboutContent />
}
