"use client"

import Link from "next/link"
import { Suspense, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useAuth } from "@/lib/auth"

const TOKEN_STORAGE_KEY = "ai_skills_token"
const LEGACY_TOKEN_STORAGE_KEY = "aiskills_token"

function AuthCallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { refreshUser } = useAuth()
  const token = searchParams.get("token")
  const next = searchParams.get("next")

  useEffect(() => {
    if (!token) {
      return
    }

    let cancelled = false

    async function handleCallback() {
      window.localStorage.setItem(TOKEN_STORAGE_KEY, token!)
      window.localStorage.removeItem(LEGACY_TOKEN_STORAGE_KEY)
      await refreshUser()
      if (!cancelled) {
        const safeNext = next && next.startsWith("/") && !next.startsWith("//") ? next : "/"
        router.replace(safeNext)
      }
    }

    void handleCallback()

    return () => {
      cancelled = true
    }
  }, [next, refreshUser, router, token])

  if (!token) {
    return (
      <main className="flex min-h-[calc(100vh-8rem)] items-center justify-center px-4 py-12">
        <div className="space-y-4 text-center">
          <h1 className="text-2xl font-semibold">Authentication failed. Please try again.</h1>
          <Link href="/login" className="text-sm underline underline-offset-4">
            Back to login
          </Link>
        </div>
      </main>
    )
  }

  return (
    <main className="flex min-h-[calc(100vh-8rem)] items-center justify-center px-4 py-12">
      <p className="text-lg font-medium">Signing you in…</p>
    </main>
  )
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-[calc(100vh-8rem)] items-center justify-center px-4 py-12">
          <p className="text-lg font-medium">Loading sign-in…</p>
        </main>
      }
    >
      <AuthCallbackContent />
    </Suspense>
  )
}
