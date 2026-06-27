import type { Metadata } from 'next'
import ContactContent from './ContactContent'

export const metadata: Metadata = {
  title: 'Contact Us',
  description: 'Get in touch with NexaCore. Free consultation for your next project.',
}

export default function ContactPage() {
  return <ContactContent />
}
