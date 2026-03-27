"use client"

import * as React from "react"
import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { useRouter } from "next/navigation"

export function SearchBar() {
    const router = useRouter()

    const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        const formData = new FormData(e.currentTarget)
        const q = formData.get("q")
        if (q) {
            router.push(`/skills?q=${q}`)
        }
    }

    return (
        <form onSubmit={handleSearch} className="relative w-full max-w-2xl mx-auto">
            <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-zinc-500" />
            <Input
                name="q"
                className="h-14 w-full pl-12 text-lg bg-white/80 dark:bg-zinc-950/50 backdrop-blur-sm border-zinc-200 dark:border-zinc-800 focus-visible:ring-offset-2 focus-visible:ring-zinc-950 dark:focus-visible:ring-zinc-300 rounded-2xl shadow-sm"
                placeholder="Search for skills (e.g. summarize, extract pdf)..."
            />
        </form>
    )
}
