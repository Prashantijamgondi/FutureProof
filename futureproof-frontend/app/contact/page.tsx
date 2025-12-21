'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MessageCircle, Send, CheckCircle } from 'lucide-react';

export default function ContactPage() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        message: ''
    });
    const [submitted, setSubmitted] = useState(false);

    const handleWhatsApp = () => {
        const text = `*Name*: ${formData.name}%0a*Email*: ${formData.email}%0a*Message*: ${formData.message}`;
        window.open(`https://wa.me/919480772811?text=${text}`, '_blank');
    };

    const handleNormalSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Simulate API call
        setSubmitted(true);
        setTimeout(() => setSubmitted(false), 3000);
        setFormData({ name: '', email: '', message: '' });
    };

    return (
        <div className="min-h-screen bg-[var(--bg-main)] text-[var(--text-main)] pt-24 pb-12 px-6 transition-colors duration-300">
            <div className="max-w-xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-12"
                >
                    <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                        Get in Touch
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400">
                        We'd love to hear from you. Choose your preferred way to connect.
                    </p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="glass p-8 rounded-2xl border border-[var(--border-main)] bg-[var(--surface-main)]"
                >
                    {submitted ? (
                        <div className="text-center py-12">
                            <div className="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                                <CheckCircle className="w-8 h-8 text-green-500" />
                            </div>
                            <h3 className="text-2xl font-bold mb-2">Message Sent!</h3>
                            <p className="text-gray-500">We'll get back to you shortly.</p>
                            <button
                                onClick={() => setSubmitted(false)}
                                className="mt-6 text-purple-500 hover:text-purple-400 font-medium"
                            >
                                Send another message
                            </button>
                        </div>
                    ) : (
                        <form onSubmit={handleNormalSubmit} className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-[var(--text-main)] mb-2">Name</label>
                                <input
                                    required
                                    type="text"
                                    value={formData.name}
                                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full px-4 py-3 rounded-xl bg-[var(--bg-main)] border border-[var(--border-main)] focus:ring-2 focus:ring-purple-500 outline-none text-[var(--text-main)] placeholder-gray-500"
                                    placeholder="John Doe"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-[var(--text-main)] mb-2">Email</label>
                                <input
                                    required
                                    type="email"
                                    value={formData.email}
                                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full px-4 py-3 rounded-xl bg-[var(--bg-main)] border border-[var(--border-main)] focus:ring-2 focus:ring-purple-500 outline-none text-[var(--text-main)] placeholder-john@example.com"
                                    placeholder="john@example.com"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-[var(--text-main)] mb-2">Message</label>
                                <textarea
                                    required
                                    rows={4}
                                    value={formData.message}
                                    onChange={e => setFormData({ ...formData, message: e.target.value })}
                                    className="w-full px-4 py-3 rounded-xl bg-[var(--bg-main)] border border-[var(--border-main)] focus:ring-2 focus:ring-purple-500 outline-none text-[var(--text-main)] placeholder-gray-500"
                                    placeholder="I need help with..."
                                />
                            </div>

                            <div className="grid gap-4 pt-4">
                                <button
                                    type="submit"
                                    className="w-full py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-purple-500/20"
                                >
                                    <Send className="w-5 h-5" />
                                    Send Message
                                </button>

                                <div className="relative text-center my-2">
                                    <span className="bg-[var(--surface-main)] px-2 text-sm text-gray-500 relative z-10">OR</span>
                                    <div className="absolute inset-0 flex items-center">
                                        <div className="w-full border-t border-[var(--border-main)]"></div>
                                    </div>
                                </div>

                                <button
                                    type="button"
                                    onClick={handleWhatsApp}
                                    className="w-full py-4 bg-[#25D366] hover:bg-[#128C7E] text-white rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-green-500/20"
                                >
                                    <MessageCircle className="w-5 h-5" />
                                    Chat on WhatsApp
                                </button>
                            </div>
                        </form>
                    )}
                </motion.div>
            </div>
        </div>
    );
}
