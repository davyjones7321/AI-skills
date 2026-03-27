"use client"

import { createContext, useContext, useEffect, useMemo, useState } from "react"
import { getMe } from "@/lib/api"
import type { AuthUser } from "@/lib/types"

interface AuthContextValue {
  user: AuthUser | null
  isLoading: boolean
  isAuthenticated: boolean
  signOut: () => void
  refreshUser: () => Promise<void>
}

const TOKEN_STORAGE_KEY = "ai_skills_token"
const LEGACY_TOKEN_STORAGE_KEY = "aiskills_token"

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

function getStoredToken(): string | null {
  if (typeof window === "undefined") {
    return null
  }

  return window.localStorage.getItem(TOKEN_STORAGE_KEY) ?? window.localStorage.getItem(LEGACY_TOKEN_STORAGE_KEY)
}

function clearStoredToken() {
  if (typeof window === "undefined") {
    return
  }

  window.localStorage.removeItem(TOKEN_STORAGE_KEY)
  window.localStorage.removeItem(LEGACY_TOKEN_STORAGE_KEY)
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let isMounted = true

    async function loadUser() {
      const token = getStoredToken()

      if (!token) {
        if (isMounted) {
          setIsLoading(false)
        }
        return
      }

      try {
        const nextUser = await getMe()
        if (!isMounted) {
          return
        }
        window.localStorage.setItem(TOKEN_STORAGE_KEY, token)
        window.localStorage.removeItem(LEGACY_TOKEN_STORAGE_KEY)
        setUser(nextUser)
      } catch {
        if (!isMounted) {
          return
        }
        clearStoredToken()
        setUser(null)
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void loadUser()

    return () => {
      isMounted = false
    }
  }, [])

  const signOut = () => {
    clearStoredToken()
    setUser(null)
  }

  const refreshUser = async () => {
    const token = getStoredToken()
    if (!token) {
      setUser(null)
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    try {
      const nextUser = await getMe()
      window.localStorage.setItem(TOKEN_STORAGE_KEY, token)
      window.localStorage.removeItem(LEGACY_TOKEN_STORAGE_KEY)
      setUser(nextUser)
    } catch {
      clearStoredToken()
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      isAuthenticated: user !== null,
      signOut,
      refreshUser,
    }),
    [isLoading, user]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
