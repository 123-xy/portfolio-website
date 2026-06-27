'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Calendar, Clock, ArrowRight } from 'lucide-react'
import { posts } from '@/lib/blog'

const categories = ['All', 'Engineering', 'Design', 'Strategy']

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
}

export default function BlogContent() {
  const featured = posts.find((p) => p.featured)
  const rest = posts.filter((p) => !p.featured)

  return (
    <>
      <section className="pt-32 pb-20 bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-primary-600 dark:text-primary-400 font-semibold text-sm uppercase tracking-wider">
            Insights
          </motion.span>
          <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mt-2 text-5xl font-extrabold text-slate-900 dark:text-white">
            The NexaCore Blog
          </motion.h1>
          <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="mt-4 text-xl text-slate-600 dark:text-slate-300">
            Engineering deep-dives, design thinking, and growth strategy.
          </motion.p>
        </div>
      </section>

      <section className="py-16 bg-white dark:bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Featured */}
          {featured && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-14"
            >
              <Link href={`/blog/${featured.slug}`} className="group block">
                <div className="grid lg:grid-cols-2 gap-8 p-8 rounded-3xl bg-gradient-to-br from-primary-50 to-purple-50 dark:from-primary-950/30 dark:to-purple-950/30 border border-primary-200/60 dark:border-primary-800/60 hover:shadow-xl transition-all hover:-translate-y-0.5">
                  <div className="flex flex-col justify-center">
                    <span className="inline-block px-3 py-1 rounded-full bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300 text-xs font-semibold mb-4 w-fit">
                      ✦ Featured · {featured.category}
                    </span>
                    <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors mb-4">
                      {featured.title}
                    </h2>
                    <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-6">{featured.excerpt}</p>
                    <div className="flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
                      <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${featured.authorGradient} flex items-center justify-center text-white text-xs font-bold`}>
                        {featured.authorInitials}
                      </div>
                      <span className="font-medium text-slate-700 dark:text-slate-300">{featured.author}</span>
                      <span>·</span>
                      <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" />{formatDate(featured.date)}</span>
                      <span>·</span>
                      <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" />{featured.readTime}</span>
                    </div>
                  </div>
                  <div className="rounded-2xl bg-gradient-to-br from-primary-600 to-purple-600 min-h-48 flex items-center justify-center">
                    <span className="text-white/30 text-9xl font-black select-none">{featured.category[0]}</span>
                  </div>
                </div>
              </Link>
            </motion.div>
          )}

          {/* Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {rest.map((post, i) => (
              <motion.article
                key={post.slug}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <Link href={`/blog/${post.slug}`} className="group block h-full">
                  <div className="h-full p-6 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 hover:border-primary-300 dark:hover:border-primary-700 hover:shadow-lg transition-all hover:-translate-y-0.5">
                    <div className="flex items-center justify-between mb-4">
                      <span className="px-3 py-1 rounded-full bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300 text-xs font-semibold">
                        {post.category}
                      </span>
                      <span className="text-xs text-slate-400 flex items-center gap-1">
                        <Clock className="w-3 h-3" />{post.readTime}
                      </span>
                    </div>
                    <h3 className="font-bold text-slate-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors mb-3 leading-snug">
                      {post.title}
                    </h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-6">{post.excerpt}</p>
                    <div className="mt-auto flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className={`w-7 h-7 rounded-full bg-gradient-to-br ${post.authorGradient} flex items-center justify-center text-white text-xs font-bold`}>
                          {post.authorInitials}
                        </div>
                        <div>
                          <div className="text-xs font-medium text-slate-700 dark:text-slate-300">{post.author}</div>
                          <div className="text-xs text-slate-400">{formatDate(post.date)}</div>
                        </div>
                      </div>
                      <ArrowRight className="w-4 h-4 text-primary-600 dark:text-primary-400 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </Link>
              </motion.article>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}
