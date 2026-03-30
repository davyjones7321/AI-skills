export interface SkillBenchmarks {
  avg_latency_ms?: number
  avg_cost_per_call_usd?: number
  [key: string]: unknown
}

export interface SkillListItem {
  id: string
  author: string
  version: string
  name: string
  description: string
  tags: string[]
  exec_type: string
  category: string | null
  benchmarks: SkillBenchmarks | null
  downloads: number
  published_at: string
  reviewed: boolean
}

export interface SkillListResponse {
  skills: SkillListItem[]
  total_count: number
  page: number
  limit: number
}

export interface SkillDetail extends SkillListItem {
  yaml_content: string
  inputs: Record<string, unknown>[]
  outputs: Record<string, unknown>[]
  execution: Record<string, unknown>
  compatible_with: string[]
}

export interface AuthUser {
  username: string
  github_id: string
  email: string | null
  avatar_url: string | null
}

export interface TagListResponse {
  tags: string[]
}
