'use client'

import { motion } from 'framer-motion'
import { Code2, Palette, BarChart3, Cloud, Shield, Smartphone } from 'lucide-react'
import Link from 'next/link'

const services = [
  {
    icon: Code2,
    title: 'Web Development',
    description: 'Full-stack applications built with React, Next.js, and modern tooling for maximum performance.',
    color: 'from-blue-500 to-cyan-500',
    bg: 'bg-blue-50 dark:bg-blue-950/30',
  },
  {
    icon: Palette,
    title: 'UI/UX Design',
    description: 'Beautiful, user-centric interfaces that convert visitors into loyal customers.',
    color: 'from-purple-500 to-pink-500',
    bg: 'bg-purple-50 dark:bg-purple-950/30',
  },
  {
    icon: BarChart3,
    title: 'Digital Strategy',
    description: 'Data-driven growth strategies that align technology with your business goals.',
    color: 'from-orange-500 to-red-500',
    bg: 'bg-orange-50 dark:bg-orange-950/30',
  },
  {
    icon: Cloud,
    title: 'Cloud Solutions',
    description: 'Scalable cloud infrastructure on AWS, GCP, and Azure to power your applications.',
    color: 'from-teal-500 to-green-500',
    bg: 'bg-teal-50 dark:bg-teal-950/30',
  },
  {
    icon: Shield,
    title: 'Security & Compliance',
    description: 'Enterprise-grade security audits and compliance frameworks to protect your data.',
    color: 'from-red-500 to-rose-500',
    bg: 'bg-red-50 dark:bg-red-950/30',
  },
  {
    icon: Smartphone,
    title: 'Mobile Apps',
    description: 'Cross-platform mobile applications built with React Native for iOS and Android.',
    color: 'from-indigo-500 to-blue-500',
    bg: 'bg-indigo-50 dark:bg-indigo-950/30',
  },
]

export default function ServicesSection() {
  return (
    <section id="services" className="py-24 bg-slate-50 dark:bg-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="text-primary-600 dark:text-primary-400 font-semibold text-sm uppercase tracking-wider">What We Do</span>
          <h2 className="mt-2 text-4xl font-extrabold text-slate-900 dark:text-white">Services that drive results</h2>
          <p className="mt-4 text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            From idea to launch, we provide end-to-end digital services tailored to your needs.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className={`group relative p-6 rounded-2xl ${s.bg} border border-slate-200/60 dark:border-slate-700/60 hover:border-primary-300 dark:hover:border-primary-700 transition-all hover:-translate-y-1 hover:shadow-lg`}
            >
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${s.color} flex items-center justify-center mb-4 shadow-lg`}>
                <s.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">{s.title}</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">{s.description}</p>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mt-12"
        >
          <Link
            href="/services"
            className="inline-flex items-center px-6 py-3 rounded-xl bg-primary-600 text-white font-semibold hover:bg-primary-700 transition-all shadow-md"
          >
            View All Services
          </Link>
        </motion.div>
      </div>
    </section>
  )
}
