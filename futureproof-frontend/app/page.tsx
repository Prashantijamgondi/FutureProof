'use client';

import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, Zap, Code2, TrendingUp, Shield, Rocket } from 'lucide-react';
import Link from 'next/link';
import React from 'react';

export default function Home() {
  return (
    <div className="min-h-screen bg-[var(--bg-main)] text-[var(--text-main)] overflow-hidden transition-colors duration-300">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-purple-500/20 to-transparent blur-3xl animate-pulse-slow" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-blue-500/20 to-transparent blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
      </div>

      {/* Hero Section */}
      <section className="relative z-10 container mx-auto px-6 pt-32 pb-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-5xl mx-auto"
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8 border-[var(--border-main)]"
          >
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-medium gradient-text">
              AI-Powered Code Modernization
            </span>
          </motion.div>

          {/* Main Heading */}
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
              Transform Legacy Code
            </span>
            <br />
            <span className="text-[var(--text-main)]">
              to 2028 Standards
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-gray-500 dark:text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
            Automatically modernize your codebase with AI.
            <span className="text-purple-500 dark:text-purple-400 font-semibold"> +300% performance</span>,
            <span className="text-blue-500 dark:text-blue-400 font-semibold"> -70% bundle size</span>,
            <span className="text-green-500 dark:text-green-400 font-semibold"> zero manual work</span>.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/dashboard">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="group px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl font-semibold text-lg flex items-center gap-2 shadow-2xl shadow-purple-500/50 hover:shadow-purple-500/70 text-white transition-all"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </motion.button>
            </Link>

          <Link href={process.env.NEXT_PUBLIC_DEMO_VIDEO_URL || '#'} target="_blank">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 glass-hover rounded-xl font-semibold text-lg text-[var(--text-main)] border border-[var(--border-main)]"
            >
              Watch Demo
            </motion.button>
          </Link>
        </div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="grid grid-cols-3 gap-8 mt-20 max-w-3xl mx-auto"
        >
          <div className="text-center">
            <div className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
              +300%
            </div>
            <div className="text-gray-500 dark:text-gray-400">Performance Gain</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent mb-2">
              -70%
            </div>
            <div className="text-gray-500 dark:text-gray-400">Bundle Size</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent mb-2">
              100%
            </div>
            <div className="text-gray-500 dark:text-gray-400">Automated</div>
          </div>
        </motion.div>
      </motion.div>
    </section>

      {/* Features Section */ }
  <section className="relative z-10 container mx-auto px-6 py-20">
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      className="grid md:grid-cols-3 gap-8"
    >
      <FeatureCard
        icon={<Zap className="w-8 h-8" />}
        title="Lightning Fast"
        description="AI-powered transformations complete in minutes, not weeks"
        gradient="from-purple-500/10 to-pink-500/10"
      />

      <FeatureCard
        icon={<Code2 className="w-8 h-8" />}
        title="All Languages"
        description="Python, React, Java, Go, Rust, and 10+ more languages"
        gradient="from-blue-500/10 to-cyan-500/10"
      />

      <FeatureCard
        icon={<Sparkles className="w-8 h-8" />}
        title="ML Specialized"
        description="TensorFlow→PyTorch with 2x training speed improvements"
        gradient="from-green-500/10 to-emerald-500/10"
      />
    </motion.div>

    {/* Additional Features */}
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      className="grid md:grid-cols-3 gap-8 mt-8"
    >
      <FeatureCard
        icon={<TrendingUp className="w-8 h-8" />}
        title="Performance Boost"
        description="Average 3x performance improvement across all projects"
        gradient="from-orange-500/10 to-red-500/10"
      />

      <FeatureCard
        icon={<Shield className="w-8 h-8" />}
        title="Security First"
        description="Automatic security vulnerability detection and fixes"
        gradient="from-indigo-500/10 to-purple-500/10"
      />

      <FeatureCard
        icon={<Rocket className="w-8 h-8" />}
        title="Production Ready"
        description="Deploy-ready code with Docker, CI/CD, and best practices"
        gradient="from-pink-500/10 to-rose-500/10"
      />
    </motion.div>
  </section>

  {/* How It Works */ }
  <section className="relative z-10 container mx-auto px-6 py-20">
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="text-center mb-16"
    >
      <h2 className="text-4xl md:text-5xl font-bold mb-4">
        <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">How FutureProof Works</span>
      </h2>
      <p className="text-xl text-gray-500 dark:text-gray-400">Transform your code in 3 simple steps</p>
    </motion.div>

    <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
      <StepCard
        number="1"
        title="Connect Repository"
        description="Simply paste your GitHub URL and we'll analyze your codebase"
      />
      <StepCard
        number="2"
        title="AI Analysis"
        description="Our AI identifies issues and optimization opportunities"
      />
      <StepCard
        number="3"
        title="Get Modern Code"
        description="Download transformed code with 2028 best practices"
      />
    </div>
  </section>
    </div >
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  gradient: string;
}

function FeatureCard({ icon, title, description, gradient }: FeatureCardProps) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      className={`p-8 rounded-2xl bg-gradient-to-br ${gradient} backdrop-blur-sm border border-[var(--border-main)] hover:border-purple-500/30 transition-all bg-[var(--surface-main)]`}
    >
      <div className="text-purple-500 dark:text-purple-400 mb-4">{icon}</div>
      <h3 className="text-2xl font-bold mb-3 text-[var(--text-main)]">{title}</h3>
      <p className="text-gray-500 dark:text-gray-400">{description}</p>
    </motion.div>
  );
}

interface StepCardProps {
  number: string;
  title: string;
  description: string;
}

function StepCard({ number, title, description }: StepCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="text-center"
    >
      <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 flex items-center justify-center text-2xl font-bold text-white">
        {number}
      </div>
      <h3 className="text-xl font-bold mb-3 text-[var(--text-main)]">{title}</h3>
      <p className="text-gray-500 dark:text-gray-400">{description}</p>
    </motion.div>
  );
}
