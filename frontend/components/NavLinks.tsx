"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"

const links = [
  { href: "/", label: "Chat" },
  { href: "/documents", label: "Documents" },
  { href: "/traces", label: "Traces" },
]

export function NavLinks() {
  const pathname = usePathname()

  return (
    <nav className="hidden items-center gap-1 md:flex">
      {links.map(({ href, label }) => {
        const active = pathname === href
        return (
          <Link
            key={href}
            href={href}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
              active
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            }`}
          >
            {label}
          </Link>
        )
      })}
    </nav>
  )
}
