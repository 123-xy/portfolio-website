export interface BlogPost {
  slug: string
  title: string
  excerpt: string
  date: string
  author: string
  authorInitials: string
  authorGradient: string
  category: string
  readTime: string
  featured?: boolean
}

export const posts: BlogPost[] = [
  {
    slug: 'next-js-performance-tips',
    title: '10 Next.js Performance Optimizations You Should Know',
    excerpt: 'From server components to image optimization — practical tips to push your Next.js app from good to blazing fast.',
    date: '2026-06-10',
    author: 'Priya Sharma',
    authorInitials: 'PS',
    authorGradient: 'from-purple-500 to-pink-500',
    category: 'Engineering',
    readTime: '6 min read',
    featured: true,
  },
  {
    slug: 'tailwind-design-system',
    title: 'Building a Scalable Design System with Tailwind CSS',
    excerpt: 'How we structure Tailwind-based design systems that scale across multiple products without collapsing into chaos.',
    date: '2026-05-22',
    author: 'Tom Wu',
    authorInitials: 'TW',
    authorGradient: 'from-orange-500 to-red-500',
    category: 'Design',
    readTime: '8 min read',
  },
  {
    slug: 'typescript-patterns-2026',
    title: 'Advanced TypeScript Patterns for Production Apps',
    excerpt: 'Discriminated unions, branded types, and template literal types — the patterns our team uses every day.',
    date: '2026-05-05',
    author: 'Nina Johansson',
    authorInitials: 'NJ',
    authorGradient: 'from-teal-500 to-green-500',
    category: 'Engineering',
    readTime: '10 min read',
  },
  {
    slug: 'ai-product-strategy-2026',
    title: 'Integrating AI into Your Product Strategy in 2026',
    excerpt: 'Beyond the hype — a framework for identifying where AI creates real value versus where it adds complexity.',
    date: '2026-04-18',
    author: 'Alex Rivera',
    authorInitials: 'AR',
    authorGradient: 'from-blue-500 to-cyan-500',
    category: 'Strategy',
    readTime: '7 min read',
  },
  {
    slug: 'react-server-components',
    title: 'React Server Components: A Practical Deep Dive',
    excerpt: 'Understanding the mental model shift, data fetching patterns, and when NOT to use server components.',
    date: '2026-04-02',
    author: 'Priya Sharma',
    authorInitials: 'PS',
    authorGradient: 'from-purple-500 to-pink-500',
    category: 'Engineering',
    readTime: '12 min read',
  },
  {
    slug: 'ux-micro-interactions',
    title: 'Micro-interactions That Make Users Feel Delight',
    excerpt: 'Small animations and feedback loops that distinguish polished products from the rest. With Framer Motion examples.',
    date: '2026-03-15',
    author: 'Tom Wu',
    authorInitials: 'TW',
    authorGradient: 'from-orange-500 to-red-500',
    category: 'Design',
    readTime: '5 min read',
  },
]

export function getPost(slug: string): BlogPost | undefined {
  return posts.find((p) => p.slug === slug)
}
