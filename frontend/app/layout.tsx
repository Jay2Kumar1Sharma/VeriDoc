import type { Metadata } from "next";
import localFont from "next/font/local";
import Link from "next/link";
import { ExternalLink } from "lucide-react";
import "./globals.css";

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
            <header className="sticky top-0 z-40 border-b bg-background/85 backdrop-blur">
              <div className="mx-auto flex h-14 w-full max-w-7xl items-center justify-between px-4">
                <Link href="/" className="flex items-center gap-2 font-semibold">
                  <span className="grid size-7 place-items-center rounded-md bg-primary text-primary-foreground">
                    V
                  </span>
                  VeriDoc
                </Link>
                <nav className="hidden items-center gap-5 text-sm text-muted-foreground md:flex">
                  <Link href="/" className="hover:text-foreground">Chat</Link>
                  <Link href="/documents" className="hover:text-foreground">Documents</Link>
                  <Link href="/traces" className="hover:text-foreground">Traces</Link>
                </nav>
                <div className="flex items-center gap-2">
                  <StatusPill />
                  <ThemeToggle />
                  <a
                    aria-label="GitHub repository"
                    href="https://github.com/Jay2Kumar1Sharma/VeriDoc"
                    target="_blank"
                    rel="noreferrer"
                    className="grid size-8 place-items-center rounded-md hover:bg-muted"
                  >
                    <ExternalLink className="size-4" />
                  </a>
                </div>
              </div>
            </header>
            <main className="flex-1">{children}</main>
            <footer className="border-t py-4">
              <div className="mx-auto flex max-w-7xl items-center justify-between px-4 text-xs text-muted-foreground">
                <span>VeriDoc 0.1.0</span>
                <span>Self-corrective RAG with Gemini</span>
              </div>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  );
}
