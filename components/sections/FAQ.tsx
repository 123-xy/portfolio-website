'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown } from 'lucide-react'

const faqs = [
  {
    q: 'How long does a typical project take?',
    a: 'Project timelines vary by scope. A landing page takes 1–2 weeks, a full web application 6–12 weeks, and enterprise projects 3–6 months. We provide a detailed timeline estimate during the initial consultation.',
  },
  {
    q: 'What is your pricing model?',
    a: 'We offer both fixed-price projects and time-and-materials engagements. Fixed-price works well for well-defined projects, while T&M suits evolving requirements. We provide transparent quotes with no hidden fees.',
  },
  {
    q: 'Do you provide post-launch support?',
    a: 'Yes — all projects include 30 days of free bug-fix support post-launch. We also offer ongoing maintenance retainers with 24/7 monitoring, security updates, and priority response times.',
  },
  {
    q: 'What technologies do you specialize in?',
    a: 'Our core stack is React, Next.js, TypeScript, Node.js, and PostgreSQL. For infrastructure, we use AWS, GCP, and Vercel. We adopt the best tool for each project rather than forcing one stack.',
  },
  {
    q: 'Can I own the source code?',
    a: 'Absolutely. Upon final payment, full intellectual property rights transfer to you. You receive all source code, assets, and documentation. No vendor lock-in.',
  },
  {
    q: 'How do we communicate during the project?',
    a: 'We use Slack for daily communication, weekly video standups, and a shared project board (Linear/Notion). You always have full visibility into progress, blockers, and upcoming milestones.',
  },
]

function FAQItem({ q, a, index }: { q: string; a: string; index: number }) {
  const [open, setOpen] = useState(false)
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.05 }}
      className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden"
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-5 text-left bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-750 transition-colors"
      >
        <span className="font-semibold text-slate-900 dark:text-white pr-4">{q}</span>
        <ChevronDown className={`w-5 h-5 text-slate-400 flex-shrink-0 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="px-5 pb-5 pt-0 text-sm text-slate-600 dark:text-slate-400 leading-relaxed bg-white dark:bg-slate-800">
              {a}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function FAQ() {
  return (
    <section id="faq" className="py-24 bg-slate-50 dark:bg-slate-900">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <span className="text-primary-600 dark:text-primary-400 font-semibold text-sm uppercase tracking-wider">FAQ</span>
          <h2 className="mt-2 text-4xl font-extrabold text-slate-900 dark:text-white">Common questions</h2>
          <p className="mt-4 text-slate-600 dark:text-slate-400">
            Everything you need to know before we start working together.
          </p>
        </motion.div>

        <div className="space-y-3">
          {faqs.map((f, i) => (
            <FAQItem key={f.q} q={f.q} a={f.a} index={i} />
          ))}
        </div>
      </div>
    </section>
  )
}
