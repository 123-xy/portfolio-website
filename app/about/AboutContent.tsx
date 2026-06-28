'use client'

import { motion } from 'framer-motion'
import { Target, Heart, Zap, Users } from 'lucide-react'
import CTA from '@/components/sections/CTA'

const values = [
  { icon: Target, title: 'Mission-driven', desc: 'Every decision aligns with your business goals, not just technical preferences.' },
  { icon: Heart, title: 'Client-first', desc: 'Transparent communication and genuine care for the outcomes we help you achieve.' },
  { icon: Zap, title: 'Excellence', desc: 'We ship performant, accessible, and maintainable code — no shortcuts.' },
  { icon: Users, title: 'Partnership', desc: 'We embed into your team, sharing context, risks, and wins together.' },
]

const team = [
  { name: 'Alex Rivera', role: 'CEO & Founder', initials: 'AR', bg: 'from-blue-500 to-cyan-500' },
  { name: 'Priya Sharma', role: 'CTO', initials: 'PS', bg: 'from-purple-500 to-pink-500' },
  { name: 'Tom Wu', role: 'Head of Design', initials: 'TW', bg: 'from-orange-500 to-red-500' },
  { name: 'Nina Johansson', role: 'Lead Engineer', initials: 'NJ', bg: 'from-teal-500 to-green-500' },
]

export default function AboutContent() {
  return (
    <>
      {/* Hero */}
      <section className="pt-32 pb-20 bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-primary-600 dark:text-primary-400 font-semibold text-sm uppercase tracking-wider"
          >
            Our Story
          </motion.span>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mt-2 text-5xl font-extrabold text-slate-900 dark:text-white"
          >
            We are NexaCore
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-6 text-xl text-slate-600 dark:text-slate-300 leading-relaxed"
          >
            Founded in 2014, NexaCore has grown from a two-person studio to a 40-person agency helping
            businesses across 30 countries build the digital products their customers love.
          </motion.p>
        </div>
      </section>

      {/* Values */}
      <section className="py-20 bg-white dark:bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white">Our values</h2>
          </motion.div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {values.map((v, i) => (
              <motion.div
                key={v.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center p-6 rounded-2xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
              >
                <div className="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center mx-auto mb-4">
                  <v.icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                </div>
                <h3 className="font-bold text-slate-900 dark:text-white mb-2">{v.title}</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">{v.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="py-20 bg-slate-50 dark:bg-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <span className="text-primary-600 dark:text-primary-400 font-semibold text-sm uppercase tracking-wider">Team</span>
            <h2 className="mt-2 text-3xl font-extrabold text-slate-900 dark:text-white">The people behind NexaCore</h2>
          </motion.div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {team.map((m, i) => (
              <motion.div
                key={m.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center group"
              >
                <div className={`w-24 h-24 mx-auto rounded-2xl bg-gradient-to-br ${m.bg} flex items-center justify-center text-white text-2xl font-bold mb-4 group-hover:scale-105 transition-transform shadow-lg`}>
                  {m.initials}
                </div>
                <div className="font-bold text-slate-900 dark:text-white">{m.name}</div>
                <div className="text-sm text-slate-500 dark:text-slate-400">{m.role}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <CTA />
    </>
  )
}
