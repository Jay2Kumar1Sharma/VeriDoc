import type { Metadata } from "next";
import localFont from "next/font/local";
import Link from "next/link";
import "./globals.css";

import { NavLinks } from "@/components/NavLinks";
import { StatusPill } from "@/components/StatusPill";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Providers } from "@/app/providers";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "VeriDoc",
  description: "Self-corrective RAG assistant for technical documentation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} min-h-screen bg-background text-foreground antialiased`}
      >
        <Providers>
          <div className="flex min-h-screen flex-col">

            {/* ── Gradient canvas ───────────────────────────────────────────── */}
            <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
              <div className="absolute -left-48 -top-48 size-[750px] rounded-full bg-primary/25 blur-[140px] dark:bg-primary/55" />
              <div className="absolute -bottom-48 -right-48 size-[650px] rounded-full bg-violet-500/20 blur-[120px] dark:bg-violet-500/45" />
              <div className="absolute right-[8%] top-[38%] size-[520px] -translate-y-1/2 rounded-full bg-sky-400/15 blur-[100px] dark:bg-sky-400/30" />
              <div className="absolute bottom-[15%] left-[5%] size-[380px] rounded-full bg-fuchsia-500/10 blur-[90px] dark:bg-fuchsia-500/25" />
            </div>

            {/* ── Header ───────────────────────────────────────────────────── */}
            <header className="sticky top-0 z-40 h-14 border-b border-white/50 dark:border-white/[0.07] bg-white/50 dark:bg-white/[0.04] backdrop-blur-xl saturate-150">
              <div className="flex h-full w-full items-center justify-between px-4">
                <div className="flex items-center gap-6">
                  <Link href="/" className="flex items-center gap-2.5">
                    <div className="flex size-7 items-center justify-center rounded-lg bg-primary shadow-sm shadow-primary/40">
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        className="size-4 text-white"
                        stroke="currentColor"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                        <path d="m9 12 2 2 4-4" />
                      </svg>
                    </div>
                    <span className="font-semibold tracking-tight">VeriDoc</span>
                  </Link>
                  <NavLinks />
                </div>
                <div className="flex items-center gap-1.5">
                  <StatusPill />
                  <ThemeToggle />
                  <a
                    aria-label="GitHub repository"
                    href="https://github.com/Jay2Kumar1Sharma/VeriDoc"
                    target="_blank"
                    rel="noreferrer"
                    className="grid size-8 place-items-center rounded-md text-muted-foreground transition-colors hover:bg-white/30 dark:hover:bg-white/10 hover:text-foreground"
                  >
                    <svg viewBox="0 0 24 24" className="size-4" fill="currentColor">
                      <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                    </svg>
                  </a>
                </div>
              </div>
            </header>

            <main className="flex-1">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
