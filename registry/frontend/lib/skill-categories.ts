export const SKILL_CATEGORIES = [
  "Frontend Development",
  "Backend Development",
  "Database",
  "DevOps",
  "Code Review",
  "Testing",
  "Data Processing",
  "Content & Writing",
  "Security",
  "AI & Agents",
  "Utilities",
  "APIs & Integrations",
] as const

export type SkillCategory = (typeof SKILL_CATEGORIES)[number]
