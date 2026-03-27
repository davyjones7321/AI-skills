"use client"

import type { FormEvent } from "react"
import { Search } from "lucide-react"
import { useRouter } from "next/navigation"
import { Input } from "@/components/ui/input"

export function HeroSearch() {
  const router = useRouter()

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const query = String(form.get("q") ?? "").trim()
    if (!query) {
      router.push("/skills")
      return
    }
    router.push(`/skills?q=${encodeURIComponent(query)}`)
  }

  return (
    <form onSubmit={onSubmit} className="relative w-full max-w-2xl mx-auto">
      <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-zinc-500" />
      <Input
        name="q"
        className="h-14 w-full pl-12 text-lg bg-white/90 dark:bg-zinc-950/60 border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-sm"
        placeholder="Search for a skill (e.g. summarize, weather, sql)..."
        aria-label="Search skills"
      />
    </form>
  )
}
