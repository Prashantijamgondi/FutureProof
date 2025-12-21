import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google"; // Ensure this is imported
import Navbar from "@/components/Navbar";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: '--font-inter',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: '--font-jetbrains-mono',
});

export const metadata: Metadata = {
  title: "FutureProof - AI-Powered Code Modernization",
  description: "Transform legacy code to 2028 standards with AI. +300% performance, -70% bundle size, zero manual work.",
  keywords: ["code modernization", "AI", "code transformation", "legacy code", "performance optimization"],
  authors: [{ name: "FutureProof" }],
  openGraph: {
    title: "FutureProof - AI-Powered Code Modernization",
    description: "Transform legacy code to 2028 standards with AI",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased transition-colors duration-300`}>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
