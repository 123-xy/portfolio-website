import type { Metadata } from 'next'
import BlogContent from './BlogContent'

export const metadata: Metadata = {
  title: 'Blog',
  description: 'Insights on web development, design, and digital strategy from the NexaCore team.',
}

export default function BlogPage() {
  return <BlogContent />
}
