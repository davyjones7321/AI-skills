"use client"

import Image from "next/image"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"
import { BrainCircuit, ChevronDown, ExternalLink, Menu, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/lib/auth"
import { cn } from "@/lib/utils"

type NavItem = {
  href: string
  label: string
  external?: boolean
}

const navItems: NavItem[] = [
  { href: "/skills", label: "Browse Skills" },
  { href: "/publish", label: "Publish" },
  { href: "https://github.com/davyjones7321/AI-skills/blob/main/docs/SPEC.md", label: "Docs", external: true },
  { href: "https://github.com/davyjones7321/AI-skills", label: "GitHub", external: true },
]

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/"
  return pathname === href || pathname.startsWith(`${href}/`)
}

export function SiteHeader() {
  const pathname = usePathname()
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const { user, isLoading, isAuthenticated, signOut } = useAuth()

  const authControl = isLoading ? (
    <div className="flex items-center gap-2">
      <Skeleton className="h-8 w-8 rounded-full" />
      <Skeleton className="h-4 w-20" />
    </div>
  ) : isAuthenticated && user ? (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-md px-2 py-1 text-sm hover:bg-accent hover:text-accent-foreground"
        >
          {user.avatar_url ? (
            <Image
              src={user.avatar_url}
              width={32}
              height={32}
              className="h-8 w-8 rounded-full object-cover"
              alt={user.username}
            />
          ) : (
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-200 text-xs font-semibold uppercase text-zinc-700">
              {user.username.slice(0, 1)}
            </div>
          )}
          <span className="max-w-28 truncate">{user.username}</span>
          <ChevronDown className="h-4 w-4" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onSelect={signOut}>Sign Out</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  ) : (
    <Button asChild size="sm" variant="ghost">
      <Link href="/login">Sign In</Link>
    </Button>
  )

  return (
    <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur-sm">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2" onClick={() => setIsMobileOpen(false)}>
            <BrainCircuit className="h-5 w-5 text-zinc-700 dark:text-zinc-300" />
            <span className="text-lg font-semibold tracking-tight">ai-skills</span>
          </Link>

          <nav className="hidden items-center gap-6 md:flex">
            {navItems.map((item) => {
              if (item.external) {
                return (
                  <a
                    key={item.label}
                    href={item.href}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-sm text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                  >
                    {item.label}
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                )
              }

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "text-sm transition-colors",
                    isActive(pathname, item.href)
                      ? "font-semibold text-zinc-900 dark:text-zinc-100"
                      : "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                  )}
                >
                  {item.label}
                </Link>
              )
            })}
          </nav>

          <div className="hidden md:block">{authControl}</div>

          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="md:hidden"
            aria-label="Toggle navigation"
            onClick={() => setIsMobileOpen((open) => !open)}
          >
            {isMobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>

        <div
          className={cn(
            "overflow-hidden transition-[max-height,opacity] duration-200 md:hidden",
            isMobileOpen ? "max-h-80 opacity-100" : "max-h-0 opacity-0"
          )}
        >
          <Separator />
          <div className="flex flex-col gap-3 py-4">
            {navItems.map((item) => {
              if (item.external) {
                return (
                  <a
                    key={item.label}
                    href={item.href}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-sm text-zinc-700 dark:text-zinc-300"
                    onClick={() => setIsMobileOpen(false)}
                  >
                    {item.label}
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                )
              }

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "text-sm",
                    isActive(pathname, item.href) ? "font-semibold text-zinc-900 dark:text-zinc-100" : "text-zinc-700 dark:text-zinc-300"
                  )}
                  onClick={() => setIsMobileOpen(false)}
                >
                  {item.label}
                </Link>
              )
            })}
            {isLoading ? (
              <div className="flex items-center gap-2 pt-1">
                <Skeleton className="h-8 w-8 rounded-full" />
                <Skeleton className="h-4 w-20" />
              </div>
            ) : isAuthenticated && user ? (
              <div className="flex items-center justify-between gap-3 pt-1">
              <div className="flex items-center gap-2">
                {user.avatar_url ? (
                  <Image
                    src={user.avatar_url}
                    width={32}
                    height={32}
                    className="h-8 w-8 rounded-full object-cover"
                    alt={user.username}
                  />
                ) : (
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-200 text-xs font-semibold uppercase text-zinc-700">
                      {user.username.slice(0, 1)}
                    </div>
                  )}
                  <span className="text-sm font-medium">{user.username}</span>
                </div>
                <Button
                  type="button"
                  size="sm"
                  variant="ghost"
                  className="w-fit px-0"
                  onClick={() => {
                    signOut()
                    setIsMobileOpen(false)
                  }}
                >
                  Sign Out
                </Button>
              </div>
            ) : (
              <Button asChild size="sm" variant="ghost" className="w-fit px-0">
                <Link href="/login" onClick={() => setIsMobileOpen(false)}>
                  Sign In
                </Link>
              </Button>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
