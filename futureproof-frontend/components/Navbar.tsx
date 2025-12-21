'use client';

import { useState, useEffect } from 'react';
import { Sun, Moon, LayoutDashboard } from 'lucide-react';
import Link from 'next/link';

export default function Navbar() {
    const [theme, setTheme] = useState<'dark' | 'light'>('dark');

    // Sync with HTML class
    // Sync with HTML class & System Preference
    useEffect(() => {
        const root = document.documentElement;

        // Function to set theme based on preference
        const applyTheme = (isDark: boolean) => {
            if (isDark) {
                root.classList.add('dark');
                setTheme('dark');
            } else {
                root.classList.remove('dark');
                setTheme('light');
            }
        };

        // Check if user has explicitly toggled before (could add localStorage logic here)
        // For now, just respect class or system pref
        if (root.classList.contains('dark')) {
            setTheme('dark');
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            applyTheme(true);
        } else {
            applyTheme(false);
        }
    }, []);

    const toggleTheme = () => {
        const newTheme = theme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);

        if (newTheme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    };

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 px-8 py-4 bg-transparent backdrop-blur-sm border-b border-white/10">
            <div className="max-w-6xl mx-auto flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2 font-bold text-xl">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
                        <LayoutDashboard className="w-5 h-5 text-white" />
                    </div>
                    <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                        FutureProof
                    </span>
                </Link>

                <div className="flex items-center gap-6">
                    <Link href="/contact" className="text-[var(--text-main)] hover:text-purple-500 transition-colors font-medium">
                        Contact 
                    </Link>
                    <div className="flex items-center gap-4">
                        <button
                            onClick={toggleTheme}
                            className="p-2 rounded-full hover:bg-white/10 transition-colors border border-white/10 group"
                            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Backend`}
                        >
                            {theme === 'dark' ? (
                                <Sun className="w-5 h-5 text-yellow-400 group-hover:rotate-90 transition-transform" />
                            ) : (
                                <Moon className="w-5 h-5 text-purple-600 group-hover:-rotate-12 transition-transform" />
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}
