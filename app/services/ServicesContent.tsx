'use client'

import { motion } from 'framer-motion'
import { Code2, Palette, BarChart3, Cloud, Shield, Smartphone, CheckCircle } from 'lucide-react'
import CTA from '@/components/sections/CTA'
import FAQ from '@/components/sections/FAQ'

const services = [
  {
    id: 'web',
    icon: Code2,
    title: 'Web Development',
    description: 'Full-stack applications built for performance, scalability, and developer experience.',
    color: 'from-blue-500 to-cyan-500',
    features: ['React / Next.js', 'TypeScript', 'REST & GraphQL APIs', 'CMS Integration', 'Performance Optimization', 'Accessibility (WCAG 2.1)'],
    price: 'From $8,000',
  },
  {
    id: 'design',
    icon: Palette,
    title: 'UI/UX Design',
    description: 'Research-driven interfaces that delight users and convert visitors into customers.',
    color: 'from-purple-500 to-pink-500',
    features: ['User Research', 'Wireframing', 'Interactive Prototypes', 'Design Systems', 'Brand Identity', 'Usability Testing'],
    price: 'From $4,000',
  },
  {
    id: 'strategy',
    icon: BarChart3,
    title: 'Digital Strategy',
    description: 'Data-driven roadmaps that align technology investment with business growth.',
    color: 'from-orange-500 to-red-500',
    features: ['Market Analysis', 'Growth Roadmaps', 'Competitive Audit', 'Analytics Setup', 'SEO Strategy', 'Conversion Optimization'],
    price: 'From $3,000',
  },
  {
    id: 'cloud',
    icon: Cloud,
    title: 'Cloud Solutions',
    description: 'Modern infrastructure that scales with demand and reduces operational overhead.',
    color: 'from-teal-500 to-green-500',
    features: ['AWS / GCP / Azure', 'Kubernetes & Docker', 'CI/CD Pipelines', 'Cost Optimization', 'Monitoring & Alerting', 'Disaster Recovery'],
    price: 'From $5,000',
  },
  {
    id: 'security',
    icon: Shield,
    title: 'Security & Compliance',
    description: 'Enterprise-grade security to protect your data and meet regulatory requirements.',
    color: 'from-red-500 to-rose-500',
    features: ['Penetration Testing', 'Code Audit', 'SOC 2 / GDPR', 'IAM & Zero Trust', 'SIEM Setup', 'Incident Response'],
    price: 'From $4,500',
  },
  {
    id: 'mobile',
    icon: Smartphone,
    title: 'Mobile Apps',
    description: 'Cross-platform native-feeling apps that users love, built with React Native.',
    color: 'from-indigo-500 to-blue-500',
    features: ['iOS & Android', 'React Native', 'Offline Support', 'Push Notifications', 'App Store Submission', 'Analytics Integration'],
    price: 'From $12,000',
  },
]

export default function ServicesContent() {
  return (
    <>
      <section className="pt-32 pb-20 bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-slate-900">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-primary-600 dark:text-primary-400 font-semibold text-sm uppercase tracking-wider">
            What We Do
          </motion.span>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mt-2 text-5xl font-extrabold text-slate-900 dark:text-white"
          >
            Our Services
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-6 text-xl text-slate-600 dark:text-slate-300"
          >
            End-to-end digital services tailored for ambitious businesses.
          </motion.p>
        </div>
      </section>

      <section className="py-20 bg-white dark:bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {services.map((s, i) => (
              <motion.div
                key={s.id}
                id={s.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-8 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all hover:shadow-lg bg-slate-50 dark:bg-slate-800/50"
              >
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${s.color} flex items-center justify-center mb-5 shadow-lg`}>
                  <s.icon className="w-7 h-7 text-white" />
                </div>
                <div className="flex items-start justify-between mb-3">
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{s.title}</h2>
                  <span className="text-sm font-semibold text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-3 py-1 rounded-full">{s.price}</span>
                </div>
                <p className="text-slate-600 dark:text-slate-400 mb-6">{s.description}</p>
                <div className="grid grid-cols-2 gap-2">
                  {s.features.map((f) => (
                    <div key={f} className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
                      <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                      {f}
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <FAQ />
      <CTA />
    </>
  )
}
