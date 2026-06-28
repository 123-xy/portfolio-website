import type { Metadata } from 'next'
import ServicesContent from './ServicesContent'

export const metadata: Metadata = {
  title: 'Services',
  description: 'Explore NexaCore\'s full range of digital services — web development, design, cloud, and more.',
}

export default function ServicesPage() {
  return <ServicesContent />
}
