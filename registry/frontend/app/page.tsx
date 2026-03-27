import Link from "next/link"
import { Boxes, Code2, Link2, Sparkles } from "lucide-react"
import { HeroSearch } from "@/components/registry/hero-search"
import { SkillCard } from "@/components/registry/skill-card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { listSkills } from "@/lib/api"
import type { SkillListItem } from "@/lib/types"

type ExecutionType = "prompt" | "tool_call" | "code" | "chain"

const executionTypeMeta: Record<
  ExecutionType,
  { description: string; href: string; chipClass: string; icon: typeof Sparkles }
> = {
  prompt: {
    description: "Prompt templates for LLM-driven tasks.",
    href: "/skills?type=prompt",
    chipClass: "bg-blue-100 text-blue-800 border-blue-200",
    icon: Sparkles,
  },
  tool_call: {
    description: "External API calls and tool integrations.",
    href: "/skills?type=tool_call",
    chipClass: "bg-purple-100 text-purple-800 border-purple-200",
    icon: Link2,
  },
  code: {
    description: "Deterministic local code execution skills.",
    href: "/skills?type=code",
    chipClass: "bg-emerald-100 text-emerald-800 border-emerald-200",
    icon: Code2,
  },
  chain: {
    description: "Multi-step workflows built from other skills.",
    href: "/skills?type=chain",
    chipClass: "bg-orange-100 text-orange-800 border-orange-200",
    icon: Boxes,
  },
}

const frameworks = ["LangChain", "AutoGen", "CrewAI", "Semantic Kernel", "OpenAI", "Anthropic"]

async function safeListSkills(params: Parameters<typeof listSkills>[0]) {
  try {
    return await listSkills(params)
  } catch {
    return {
      skills: [] as SkillListItem[],
      total_count: 0,
      page: params?.page ?? 1,
      limit: params?.limit ?? 1,
    }
  }
}

export default async function HomePage() {
  const [
    overallResponse,
    newestResponse,
    promptResponse,
    toolCallResponse,
    codeResponse,
    chainResponse,
  ] = await Promise.all([
    safeListSkills({ limit: 1 }),
    safeListSkills({ sort: "newest", limit: 6 }),
    safeListSkills({ type: "prompt", limit: 1 }),
    safeListSkills({ type: "tool_call", limit: 1 }),
    safeListSkills({ type: "code", limit: 1 }),
    safeListSkills({ type: "chain", limit: 1 }),
  ])

  const newestSkills = newestResponse.skills
  const typeCounts: Record<ExecutionType, number> = {
    prompt: promptResponse.total_count,
    tool_call: toolCallResponse.total_count,
    code: codeResponse.total_count,
    chain: chainResponse.total_count,
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <section className="relative overflow-hidden py-20 md:py-28">
        <div className="container px-4 md:px-6 relative z-10 space-y-8 text-center">
          <Badge variant="outline" className="mx-auto">ai-skills registry</Badge>
          <div className="space-y-4 max-w-4xl mx-auto">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
              The universal open standard for AI agent skills
            </h1>
            <p className="text-zinc-600 dark:text-zinc-300 md:text-xl">
              Write a skill once in a simple YAML file. Publish it. Export it to LangChain, AutoGen, CrewAI, and more, automatically.
            </p>
          </div>
          <HeroSearch />
          <div className="flex flex-wrap items-center justify-center gap-3">
            <Button asChild>
              <Link href="/skills">Browse Skills</Link>
            </Button>
            <Button asChild variant="outline">
              <a href="https://github.com/davyjones7321/AI-skills/blob/main/docs/SPEC.md" target="_blank" rel="noreferrer">
                Read the Spec
              </a>
            </Button>
          </div>
        </div>
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,rgba(59,130,246,0.12),transparent_50%),radial-gradient(ellipse_at_bottom,rgba(16,185,129,0.08),transparent_50%)]" />
      </section>

      <section className="border-y bg-zinc-50/70 dark:bg-zinc-900/20">
        <div className="container px-4 md:px-6 py-8">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3 text-center">
            <div>
              <div className="text-3xl font-bold">{overallResponse.total_count}</div>
              <div className="text-sm text-zinc-500">Skills Published</div>
            </div>
            <div>
              <div className="text-3xl font-bold">4</div>
              <div className="text-sm text-zinc-500">Execution Types</div>
            </div>
            <div>
              <div className="text-3xl font-bold">3</div>
              <div className="text-sm text-zinc-500">Framework Exporters</div>
            </div>
          </div>
        </div>
      </section>

      <section className="container px-4 md:px-6 py-14 space-y-6">
        <h2 className="text-2xl font-bold tracking-tight">Browse by execution type</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {(Object.keys(executionTypeMeta) as ExecutionType[]).map((type) => {
            const meta = executionTypeMeta[type]
            const Icon = meta.icon
            return (
              <Link key={type} href={meta.href}>
                <Card className="h-full transition-colors hover:border-zinc-400 dark:hover:border-zinc-600">
                  <CardHeader className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Badge variant="outline" className={meta.chipClass}>{type}</Badge>
                      <Icon className="h-4 w-4 text-zinc-500" />
                    </div>
                    <CardTitle className="text-lg">{typeCounts[type]}</CardTitle>
                    <CardDescription>{meta.description}</CardDescription>
                  </CardHeader>
                </Card>
              </Link>
            )
          })}
        </div>
      </section>

      <section className="container px-4 md:px-6 py-14 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold tracking-tight">Recently Published</h2>
          <Button asChild variant="link">
            <Link href="/skills">View all skills →</Link>
          </Button>
        </div>
        <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {newestSkills.map((skill) => (
            <SkillCard key={`${skill.author}/${skill.id}`} {...skill} />
          ))}
        </div>
      </section>

      <section id="how-it-works" className="container px-4 md:px-6 py-14 space-y-8">
        <h2 className="text-2xl font-bold tracking-tight">How it works</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Card>
            <CardHeader>
              <Badge variant="outline" className="w-fit">1</Badge>
              <CardTitle className="text-lg">Write</CardTitle>
              <CardDescription>
                Define your skill in a skill.yaml file with inputs, outputs, and execution logic.
              </CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <Badge variant="outline" className="w-fit">2</Badge>
              <CardTitle className="text-lg">Validate & Publish</CardTitle>
              <CardDescription>
                Run aiskills validate then aiskills publish to submit to the registry.
              </CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <Badge variant="outline" className="w-fit">3</Badge>
              <CardTitle className="text-lg">Export anywhere</CardTitle>
              <CardDescription>
                Install any skill and export it to your framework with one command.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
        <Card>
          <CardContent className="p-0">
            <pre className="overflow-x-auto rounded-lg bg-zinc-950 p-5 text-xs text-zinc-100">
{`aiskills init my-skill
aiskills validate skill.yaml
aiskills publish skill.yaml
aiskills install author/my-skill --export langchain`}
            </pre>
          </CardContent>
        </Card>
      </section>

      <section className="container px-4 md:px-6 py-14 space-y-6">
        <h2 className="text-2xl font-bold tracking-tight">Works with your stack</h2>
        <div className="flex flex-wrap gap-2">
          {frameworks.map((framework) => (
            <Badge key={framework} variant="secondary">{framework}</Badge>
          ))}
        </div>
        <p className="text-zinc-600 dark:text-zinc-300">
          Export any skill to any framework with a single command.
        </p>
      </section>

      <section className="border-t">
        <div className="container px-4 md:px-6 py-16 text-center space-y-5">
          <h2 className="text-3xl font-bold tracking-tight">Ready to publish your first skill?</h2>
          <div className="flex flex-wrap justify-center gap-3">
            <Button asChild>
              <Link href="/publish">Get Started</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/skills">Browse the Registry</Link>
            </Button>
          </div>
        </div>
      </section>
    </main>
  )
}
