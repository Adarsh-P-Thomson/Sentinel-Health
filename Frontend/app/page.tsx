"use client";

import { motion } from "framer-motion";
import { 
  Activity, 
  Shield, 
  Zap, 
  TrendingUp, 
  Eye, 
  Lock,
  ArrowRight,
  CheckCircle2
} from "lucide-react";

export default function Home() {
  const features = [
    {
      icon: Activity,
      title: "Real-Time Monitoring",
      description: "Continuous surveillance across social platforms for emerging safety signals"
    },
    {
      icon: Shield,
      title: "HIPAA Compliant",
      description: "Automated PII/PHI scrubbing ensures patient privacy and regulatory compliance"
    },
    {
      icon: Zap,
      title: "Multi-Agent AI",
      description: "Specialized agents collaborate to extract, validate, and prioritize insights"
    },
    {
      icon: TrendingUp,
      title: "Trend Analysis",
      description: "Identify viral patterns and emerging adverse events before they escalate"
    },
    {
      icon: Eye,
      title: "Full Traceability",
      description: "Complete transparency with LangSmith integration for every AI decision"
    },
    {
      icon: Lock,
      title: "Secure & Scalable",
      description: "Enterprise-grade security with intelligent cost optimization"
    }
  ];

  const stats = [
    { value: "24/7", label: "Monitoring" },
    { value: "10+", label: "Data Sources" },
    { value: "<5min", label: "Alert Time" },
    { value: "99.9%", label: "Accuracy" }
  ];

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-neutral-200 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-2"
          >
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="font-display font-semibold text-xl text-neutral-900">
              Sentinel Health
            </span>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-6"
          >
            <a href="/" className="text-neutral-600 hover:text-primary-600 transition-colors">
              Home
            </a>
            <a href="/search" className="text-neutral-600 hover:text-primary-600 transition-colors">
              Search
            </a>
            <a href="/suggestions" className="text-neutral-600 hover:text-primary-600 transition-colors">
              Suggestions
            </a>
            <a href="#features" className="text-neutral-600 hover:text-primary-600 transition-colors">
              Features
            </a>
            <a href="#how-it-works" className="text-neutral-600 hover:text-primary-600 transition-colors">
              How It Works
            </a>
            <button className="px-5 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium">
              Get Started
            </button>
          </motion.div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-4xl mx-auto"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 rounded-full text-primary-700 text-sm font-medium mb-6">
              <Zap className="w-4 h-4" />
              AI-Powered Patient Safety Intelligence
            </div>
            
            <h1 className="font-display font-bold text-5xl md:text-6xl text-neutral-900 mb-6 text-balance">
              Transform Social Signals Into
              <span className="text-primary-600"> Actionable Insights</span>
            </h1>
            
            <p className="text-xl text-neutral-600 mb-10 text-balance max-w-3xl mx-auto">
              Sentinel Health autonomously monitors social platforms to detect adverse drug events 
              and patient safety concerns in real-time, empowering healthcare teams to act faster.
            </p>
            
            <div className="flex items-center justify-center gap-4">
              <button className="px-8 py-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-all font-semibold flex items-center gap-2 shadow-lg shadow-primary-600/20">
                Start Monitoring
                <ArrowRight className="w-5 h-5" />
              </button>
              <button className="px-8 py-4 bg-white text-neutral-900 rounded-lg hover:bg-neutral-50 transition-colors font-semibold border border-neutral-200">
                View Demo
              </button>
            </div>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto"
          >
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="font-display font-bold text-4xl text-primary-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-neutral-600 font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-display font-bold text-4xl text-neutral-900 mb-4">
              Intelligent Monitoring, Simplified
            </h2>
            <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
              Our multi-agent system handles the complexity so you can focus on patient safety
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="p-6 rounded-xl border border-neutral-200 hover:border-primary-300 hover:shadow-lg transition-all bg-white"
              >
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="font-display font-semibold text-xl text-neutral-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-neutral-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 px-6 bg-neutral-50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-display font-bold text-4xl text-neutral-900 mb-4">
              From Signal to Action in Minutes
            </h2>
            <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
              Our agentic workflow transforms raw social data into validated safety insights
            </p>
          </motion.div>

          <div className="max-w-4xl mx-auto space-y-6">
            {[
              {
                step: "01",
                title: "Configure & Monitor",
                description: "Set target keywords, data sources, and monitoring intervals through an intuitive admin interface"
              },
              {
                step: "02",
                title: "Intelligent Extraction",
                description: "MCP servers fetch data while specialized AI agents anonymize, extract entities, and analyze sentiment"
              },
              {
                step: "03",
                title: "Validation & Prioritization",
                description: "Safety auditor verifies signals against medical databases and flags high-risk events with virality metrics"
              },
              {
                step: "04",
                title: "Alert & Escalate",
                description: "Generate patient impact reports and instantly notify safety teams via WhatsApp, email, or CRM integration"
              }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="flex gap-6 p-6 bg-white rounded-xl border border-neutral-200"
              >
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-primary-600 text-white rounded-lg flex items-center justify-center font-display font-bold">
                    {item.step}
                  </div>
                </div>
                <div>
                  <h3 className="font-display font-semibold text-xl text-neutral-900 mb-2">
                    {item.title}
                  </h3>
                  <p className="text-neutral-600">
                    {item.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 bg-primary-600">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="font-display font-bold text-4xl text-white mb-6">
              Ready to Enhance Patient Safety?
            </h2>
            <p className="text-xl text-primary-100 mb-8">
              Join healthcare organizations using AI to detect safety signals faster
            </p>
            <button className="px-8 py-4 bg-white text-primary-600 rounded-lg hover:bg-neutral-50 transition-colors font-semibold shadow-xl">
              Request a Demo
            </button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 bg-neutral-900 text-neutral-400">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="font-display font-semibold text-xl text-white">
              Sentinel Health
            </span>
          </div>
          <p className="text-sm">
            © 2026 Sentinel Health. AI-Powered Patient Safety Monitoring.
          </p>
        </div>
      </footer>
    </div>
  );
}
