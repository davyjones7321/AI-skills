"use client"

import Link from "next/link"
import { FormEvent, Suspense, useCallback, useEffect, useMemo, useState } from "react"
import { usePathname, useRouter, useSearchParams } from "next/navigation"
import { SkillCard } from "@/components/registry/skill-card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { getTags, listSkills } from "@/lib/api"
import type { SkillListItem } from "@/lib/types"
import {
  EXEC_TYPES,
  PAGE_SIZE,
  SORT_OPTIONS,
  type ExecTypeFilter,
  type SortFilter,
  getFilterDescription,
  getVisiblePageNumbers,
  parsePositiveInt,
  startEndText,
} from "@/lib/skills-page-utils"

function SkillCardSkeleton() {
  return (
    <Card>
      <CardHeader className="space-y-2">
        <Skeleton className="h-6 w-2/3" />
        <Skeleton className="h-4 w-1/2" />
      </CardHeader>
      <CardContent className="space-y-3">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <div className="flex gap-2">
          <Skeleton className="h-5 w-16" />
          <Skeleton className="h-5 w-16" />
        </div>
      </CardContent>
    </Card>
  )
}

function SkillsPageContent() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  const q = searchParams.get("q") ?? ""
  const typeRaw = (searchParams.get("type") ?? "all").toLowerCase()
  const type: ExecTypeFilter = EXEC_TYPES.includes(typeRaw as ExecTypeFilter)
    ? (typeRaw as ExecTypeFilter)
    : "all"
  const tag = searchParams.get("tag") ?? "all"
  const sortRaw = (searchParams.get("sort") ?? "newest").toLowerCase()
  const sort: SortFilter = SORT_OPTIONS.includes(sortRaw as SortFilter)
    ? (sortRaw as SortFilter)
    : "newest"
  const page = parsePositiveInt(searchParams.get("page"), 1)

  const [queryInput, setQueryInput] = useState(q)
  const [skills, setSkills] = useState<SkillListItem[]>([])
  const [totalCount, setTotalCount] = useState(0)
  const [serverPage, setServerPage] = useState(page)
  const [serverLimit, setServerLimit] = useState(PAGE_SIZE)
  const [tags, setTags] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  const totalPages = Math.max(1, Math.ceil(totalCount / serverLimit))
  const shouldShowPagination = totalCount > serverLimit
  const filterDescription = getFilterDescription({ q, type, tag, sort })

  const updateUrl = useCallback((updates: Record<string, string | null>) => {
    const next = new URLSearchParams(searchParams.toString())
    for (const [key, value] of Object.entries(updates)) {
      if (!value || value === "all" || (key === "sort" && value === "newest")) {
        next.delete(key)
      } else {
        next.set(key, value)
      }
    }
    const nextQuery = next.toString()
    router.push(nextQuery ? `${pathname}?${nextQuery}` : pathname)
  }, [pathname, router, searchParams])

  const handleSearchSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    updateUrl({ q: queryInput || null, page: "1" })
  }

  useEffect(() => {
    setQueryInput(q)
  }, [q])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      if (queryInput !== q) {
        updateUrl({ q: queryInput || null, page: "1" })
      }
    }, 300)
    return () => window.clearTimeout(timer)
  }, [q, queryInput, updateUrl])

  useEffect(() => {
    let cancelled = false
    const loadTags = async () => {
      try {
        const result = await getTags()
        if (!cancelled) {
          setTags(result.tags)
        }
      } catch {
        if (!cancelled) {
          setTags([])
        }
      }
    }
    loadTags()
    return () => {
      cancelled = true
    }
  }, [])

  const fetchSkills = useCallback(async () => {
    setIsLoading(true)
    setLoadError(null)
    try {
      const response = await listSkills({
        q: q || undefined,
        type: type === "all" ? undefined : type,
        tag: tag === "all" ? undefined : tag,
        sort,
        page,
        limit: PAGE_SIZE,
      })
      setSkills(response.skills)
      setTotalCount(response.total_count)
      setServerPage(response.page)
      setServerLimit(response.limit)
    } catch {
      setLoadError("Failed to load skills")
      setSkills([])
      setTotalCount(0)
      setServerPage(1)
      setServerLimit(PAGE_SIZE)
    } finally {
      setIsLoading(false)
    }
  }, [page, q, sort, tag, type])

  useEffect(() => {
    void fetchSkills()
  }, [fetchSkills])

  const pageNumbers = useMemo(() => getVisiblePageNumbers(page, totalPages), [page, totalPages])

  return (
    <main className="min-h-screen bg-background text-foreground py-12">
      <div className="container px-4 md:px-6 space-y-8">
        <div className="space-y-4">
          <h1 className="text-3xl font-bold tracking-tight">Browse Skills</h1>

          <form onSubmit={handleSearchSubmit} className="w-full max-w-3xl">
            <Input
              value={queryInput}
              onChange={(event) => setQueryInput(event.target.value)}
              placeholder="Search skills..."
              className="h-11"
              aria-label="Search skills"
            />
          </form>

          <div className="flex flex-wrap gap-3">
            <select
              value={type}
              onChange={(event) => updateUrl({ type: event.target.value, page: "1" })}
              className="h-10 min-w-[170px] rounded-md border border-input bg-background px-3 text-sm"
              aria-label="Execution type filter"
            >
              <option value="all">All Types</option>
              <option value="prompt">prompt</option>
              <option value="tool_call">tool_call</option>
              <option value="code">code</option>
              <option value="chain">chain</option>
            </select>

            <select
              value={tag}
              onChange={(event) => updateUrl({ tag: event.target.value, page: "1" })}
              className="h-10 min-w-[170px] rounded-md border border-input bg-background px-3 text-sm"
              aria-label="Tag filter"
            >
              <option value="all">All Tags</option>
              {tags.map((tagValue) => (
                <option key={tagValue} value={tagValue}>
                  {tagValue}
                </option>
              ))}
            </select>

            <select
              value={sort}
              onChange={(event) => updateUrl({ sort: event.target.value, page: "1" })}
              className="h-10 min-w-[190px] rounded-md border border-input bg-background px-3 text-sm"
              aria-label="Sort order"
            >
              <option value="newest">Newest</option>
              <option value="most_downloaded">Most Downloaded</option>
              <option value="lowest_latency">Lowest Latency</option>
            </select>
          </div>

          <div className="text-sm text-zinc-500">{startEndText(totalCount, serverPage, serverLimit)}</div>
        </div>

        {isLoading ? (
          <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 12 }).map((_, index) => (
              <SkillCardSkeleton key={`skeleton-${index}`} />
            ))}
          </div>
        ) : null}

        {!isLoading && loadError ? (
          <div className="rounded-lg border border-dashed p-10 text-center">
            <p className="text-zinc-600 dark:text-zinc-300">Failed to load skills</p>
            <Button onClick={() => void fetchSkills()} className="mt-4">
              Retry
            </Button>
          </div>
        ) : null}

        {!isLoading && !loadError && skills.length === 0 ? (
          <div className="rounded-lg border border-dashed p-10 text-center space-y-4">
            <p className="text-lg font-medium">No skills found</p>
            <p className="text-sm text-zinc-500">Active filters: {filterDescription}</p>
            <Button asChild variant="outline">
              <Link href="/skills">Clear filters</Link>
            </Button>
          </div>
        ) : null}

        {!isLoading && !loadError && skills.length > 0 ? (
          <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            {skills.map((skill) => (
              <SkillCard key={`${skill.author}/${skill.id}`} {...skill} />
            ))}
          </div>
        ) : null}

        {!isLoading && !loadError && shouldShowPagination ? (
          <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                disabled={page <= 1}
                onClick={() => updateUrl({ page: String(Math.max(1, page - 1)) })}
              >
                Previous
              </Button>
              {pageNumbers.map((pageNumber) => (
                <Button
                  key={pageNumber}
                  variant={pageNumber === page ? "default" : "outline"}
                  onClick={() => updateUrl({ page: String(pageNumber) })}
                >
                  {pageNumber}
                </Button>
              ))}
              <Button
                variant="outline"
                disabled={page >= totalPages}
                onClick={() => updateUrl({ page: String(Math.min(totalPages, page + 1)) })}
              >
                Next
              </Button>
            </div>
            <Badge variant="outline">
              Page {page} of {totalPages}
            </Badge>
          </div>
        ) : null}
      </div>
    </main>
  )
}

export default function SkillsPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-background text-foreground py-12">
          <div className="container px-4 md:px-6 space-y-8">
            <div className="space-y-4">
              <h1 className="text-3xl font-bold tracking-tight">Browse Skills</h1>
            </div>
            <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 12 }).map((_, index) => (
                <SkillCardSkeleton key={`suspense-skeleton-${index}`} />
              ))}
            </div>
          </div>
        </main>
      }
    >
      <SkillsPageContent />
    </Suspense>
  )
}
