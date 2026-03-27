export const PAGE_SIZE = 12
export const EXEC_TYPES = ["all", "prompt", "tool_call", "code", "chain"] as const
export const SORT_OPTIONS = ["newest", "most_downloaded", "lowest_latency"] as const

export type ExecTypeFilter = (typeof EXEC_TYPES)[number]
export type SortFilter = (typeof SORT_OPTIONS)[number]

export function parsePositiveInt(value: string | null, fallback: number): number {
  if (!value) return fallback
  const parsed = Number(value)
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback
}

export function startEndText(totalCount: number, page: number, limit: number): string {
  if (totalCount === 0) return "Showing 0 of 0 skills"
  const start = (page - 1) * limit + 1
  const end = Math.min(page * limit, totalCount)
  return `Showing ${start}-${end} of ${totalCount} skills`
}

export function getFilterDescription({
  q,
  type,
  tag,
  sort,
}: {
  q: string
  type: ExecTypeFilter
  tag: string
  sort: SortFilter
}): string {
  const parts: string[] = []
  if (q) parts.push(`search "${q}"`)
  if (type !== "all") parts.push(`type ${type}`)
  if (tag !== "all") parts.push(`tag ${tag}`)
  parts.push(`sorted by ${sort.replace(/_/g, " ")}`)
  return parts.join(", ")
}

export function getVisiblePageNumbers(page: number, totalPages: number): number[] {
  if (totalPages <= 1) return []
  const start = Math.max(1, page - 2)
  const end = Math.min(totalPages, page + 2)
  const nums: number[] = []
  for (let i = start; i <= end; i += 1) nums.push(i)
  return nums
}
