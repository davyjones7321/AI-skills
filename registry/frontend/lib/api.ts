import type { AuthUser, SkillDetail, SkillListResponse, TagListResponse } from "@/lib/types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const TOKEN_STORAGE_KEY = "ai_skills_token"
const LEGACY_TOKEN_STORAGE_KEY = "aiskills_token"

type ListSkillsParams = {
  q?: string
  tag?: string
  type?: string
  category?: string
  page?: number
  limit?: number
  sort?: string
}

type SearchSkillsParams = {
  q: string
  tag?: string
  type?: string
  category?: string
  page?: number
  limit?: number
  sort?: string
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

function buildUrl(path: string, params?: Record<string, string | number | undefined>) {
  const url = new URL(path, API_BASE_URL)
  if (!params) {
    return url.toString()
  }
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      url.searchParams.set(key, String(value))
    }
  }
  return url.toString()
}

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, { cache: "no-store", ...init })
  if (!res.ok) {
    let message = `API request failed (${res.status})`
    try {
      const payload = await res.json()
      if (payload && typeof payload.detail === "string") {
        message = payload.detail
      }
    } catch {
      // Fall back to the default message when the response is not JSON.
    }
    throw new ApiError(message, res.status)
  }
  return res.json() as Promise<T>
}

export async function listSkills(params: ListSkillsParams = {}): Promise<SkillListResponse> {
  const { q, tag, type, category, page, limit, sort } = params
  const hasSearchFilters = Boolean(q || tag || type || category)
  const path = hasSearchFilters ? "/skills/search" : "/skills/"
  const url = buildUrl(path, { q, tag, type, category, page, limit, sort })
  return fetchJson<SkillListResponse>(url)
}

export async function searchSkills(params: SearchSkillsParams): Promise<SkillListResponse> {
  const url = buildUrl("/skills/search", params)
  return fetchJson<SkillListResponse>(url)
}

export async function getSkill(author: string, id: string): Promise<SkillDetail> {
  const url = buildUrl(`/skills/${encodeURIComponent(author)}/${encodeURIComponent(id)}`)
  return fetchJson<SkillDetail>(url)
}

export function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") {
    return {}
  }

  const token =
    window.localStorage.getItem(TOKEN_STORAGE_KEY) ??
    window.localStorage.getItem(LEGACY_TOKEN_STORAGE_KEY)

  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function getMe(): Promise<AuthUser> {
  const url = buildUrl("/auth/me")
  const headers = getAuthHeaders()
  return fetchJson<AuthUser>(url, { headers: Object.keys(headers).length > 0 ? headers : undefined })
}

export async function getTags(): Promise<TagListResponse> {
  const url = buildUrl("/skills/tags")
  return fetchJson<TagListResponse>(url)
}

export async function publishSkillFile(file: File): Promise<SkillDetail> {
  const url = buildUrl("/skills/")
  const form = new FormData()
  form.append("file", file)
  const headers = getAuthHeaders()
  return fetchJson<SkillDetail>(url, {
    method: "POST",
    body: form,
    headers,
  })
}
