import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Calendar, Clock } from 'lucide-react'
import { posts, getPost } from '@/lib/blog'

export async function generateStaticParams() {
  return posts.map((p) => ({ slug: p.slug }))
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const post = getPost(params.slug)
  if (!post) return {}
  return { title: post.title, description: post.excerpt }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
}

export default function BlogPostPage({ params }: { params: { slug: string } }) {
  const post = getPost(params.slug)
  if (!post) notFound()

  return (
    <article className="min-h-screen bg-white dark:bg-slate-950">
      {/* Hero */}
      <div className="bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900 pt-32 pb-16">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <Link href="/blog" className="inline-flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 hover:text-primary-600 dark:hover:text-primary-400 mb-8 transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to Blog
          </Link>
          <span className="px-3 py-1 rounded-full bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300 text-xs font-semibold mb-4 inline-block">
            {post.category}
          </span>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 dark:text-white mt-3 mb-6 leading-tight">
            {post.title}
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-300 mb-8">{post.excerpt}</p>
          <div className="flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
            <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${post.authorGradient} flex items-center justify-center text-white text-sm font-bold`}>
              {post.authorInitials}
            </div>
            <div>
              <div className="font-semibold text-slate-700 dark:text-slate-300">{post.author}</div>
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" />{formatDate(post.date)}</span>
                <span>·</span>
                <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" />{post.readTime}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content placeholder */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="prose prose-slate dark:prose-invert max-w-none">
          <p className="text-lg leading-relaxed text-slate-600 dark:text-slate-400">
            This is a placeholder for the full article content. In a real implementation, content would be loaded from an MDX file, a headless CMS (like Contentful or Sanity), or a database.
          </p>
          <h2>Introduction</h2>
          <p>
            Performance is one of the most impactful dimensions of user experience. Studies consistently show that a 100ms improvement in page load time correlates with a 1% increase in conversion rate — and for high-traffic sites, that translates directly to revenue.
          </p>
          <h2>Key Strategies</h2>
          <p>
            The most impactful optimizations we've found include leveraging React Server Components to reduce client bundle size, using Next.js <code>Image</code> for automatic format conversion and lazy loading, and implementing granular code splitting with dynamic imports.
          </p>
          <p>
            Combined with edge caching via Vercel's CDN and proper <code>Cache-Control</code> headers, most Next.js apps can achieve a Lighthouse performance score above 95 with relatively little effort.
          </p>
          <h2>Conclusion</h2>
          <p>
            Performance is not a one-time project — it's an ongoing discipline. Set up a performance budget, monitor Core Web Vitals in production, and treat regressions the same way you treat bugs.
          </p>
        </div>

        <div className="mt-16 pt-8 border-t border-slate-200 dark:border-slate-800">
          <Link href="/blog" className="inline-flex items-center gap-2 text-primary-600 dark:text-primary-400 font-semibold hover:underline">
            <ArrowLeft className="w-4 h-4" />
            Back to all articles
          </Link>
        </div>
      </div>
    </article>
  )
}
