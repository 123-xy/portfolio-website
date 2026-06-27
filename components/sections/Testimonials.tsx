'use client'

import { motion } from 'framer-motion'
import { Star, Quote } from 'lucide-react'

const testimonials = [
  {
    name: 'Sarah Johnson',
    role: 'CEO, TechVenture',
    body: "NexaCore transformed our entire digital presence. The team's expertise in Next.js and design is unmatched. Our conversion rate increased by 140% after the redesign.",
    rating: 5,
    avatar: 'SJ',
  },
  {
    name: 'Marcus Williams',
    role: 'CTO, FinScale',
    body: "The cloud migration NexaCore handled was seamless. Zero downtime, 60% cost reduction, and our team now deploys 3x faster. I can't recommend them enough.",
    rating: 5,
    avatar: 'MW',
  },
  {
    name: 'Emily Chen',
    role: 'Founder, GrowthLab',
    body: "From strategy to execution, NexaCore was there every step of the way. They feel like a true partner, not just a vendor. Our ARR doubled in 8 months.",
    rating: 5,
    avatar: 'EC',
  },
  {
    name: 'David Park',
    role: 'VP Product, RetailX',
    body: "The mobile app NexaCore built has over 50k downloads and a 4.8 App Store rating. The attention to UX detail is exceptional. On time, on budget.",
    rating: 5,
    avatar: 'DP',
  },
  {
    name: 'Lisa Rodriguez',
    role: 'CMO, BrandForge',
    body: "Our website performance went from 45 to 98 on PageSpeed Insights. NexaCore's frontend skills are genuinely world-class. The ROI has been incredible.",
    rating: 5,
    avatar: 'LR',
  },
  {
    name: 'James Miller',
    role: 'Director, DataSmart',
    body: "Security audit uncovered 12 critical vulnerabilities we had no idea about. NexaCore's team fixed everything and set up monitoring. Peace of mind restored.",
    rating: 5,
    avatar: 'JM',
  },
]

function Stars({ count }: { count: number }) {
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: count }).map((_, i) => (
        <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
      ))}
    </div>
  )
}

export default function Testimonials() {
  return (
    <section id="testimonials" className="py-24 bg-white dark:bg-slate-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="text-primary-600 dark:text-primary-400 font-semibold text-sm uppercase tracking-wider">Testimonials</span>
          <h2 className="mt-2 text-4xl font-extrabold text-slate-900 dark:text-white">Trusted by leaders</h2>
          <p className="mt-4 text-lg text-slate-600 dark:text-slate-400">
            Don't take our word for it — hear from our clients.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="relative p-6 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all hover:shadow-lg"
            >
              <Quote className="absolute top-4 right-4 w-8 h-8 text-slate-200 dark:text-slate-700" />
              <Stars count={t.rating} />
              <p className="mt-4 text-slate-700 dark:text-slate-300 text-sm leading-relaxed">{t.body}</p>
              <div className="mt-6 flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
                  {t.avatar}
                </div>
                <div>
                  <div className="font-semibold text-slate-900 dark:text-white text-sm">{t.name}</div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">{t.role}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
