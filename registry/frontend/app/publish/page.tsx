import Link from "next/link"
import { CheckCircle2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { CodeBlock } from "@/components/ui/code-block"
import { Separator } from "@/components/ui/separator"

const minimalSkillYaml = `skill:
  id: my-skill-name
  version: 1.0.0
  name: My Skill
  description: A short summary of what this skill does.
  inputs:
    - name: input_text
      type: string
      required: true
  outputs:
    - name: result
      type: string
  execution:
    type: prompt
    prompt_template: "Process: {input_text}"`

const executionTypeSnippets = {
  prompt: `execution:
  type: prompt
  prompt_template: "Summarize: {input_text}"`,
  tool_call: `execution:
  type: tool_call
  endpoint: "https://api.example.com/run"`,
  code: `execution:
  type: code
  language: python
  source: |
    output["result"] = input["text"].upper()`,
  chain: `execution:
  type: chain
  steps:
    - id: detect-language
    - id: summarize-document`,
}

function typeBadgeClass(type: "prompt" | "tool_call" | "code" | "chain") {
  if (type === "prompt") return "bg-blue-100 text-blue-800 border-blue-200"
  if (type === "tool_call") return "bg-purple-100 text-purple-800 border-purple-200"
  if (type === "code") return "bg-emerald-100 text-emerald-800 border-emerald-200"
  return "bg-orange-100 text-orange-800 border-orange-200"
}

export default function PublishPage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="container max-w-5xl px-4 py-12 md:px-6 md:py-14">
        <div className="mb-8 text-sm text-zinc-500">
          <Link href="/" className="hover:text-zinc-900 dark:hover:text-zinc-100">
            Home
          </Link>
          <span className="mx-2">→</span>
          <span>Publish</span>
        </div>

        <section className="space-y-3">
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl">Publish a Skill</h1>
          <p className="text-zinc-600 dark:text-zinc-300 md:text-lg">
            Share your skill with the community. Publish once, install anywhere.
          </p>
        </section>

        <Separator className="my-10" />

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold tracking-tight">Prerequisites</h2>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Python 3.8+ installed</CardTitle>
                <CardDescription>Use Python 3.8 or newer so the CLI and SDK run correctly.</CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">ai-skills-sdk installed via pip</CardTitle>
                <CardDescription>Install the CLI globally or in your project environment using pip.</CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">A GitHub account</CardTitle>
                <CardDescription>Publishing uses GitHub authentication to identify the skill author.</CardDescription>
              </CardHeader>
            </Card>
          </div>
        </section>

        <Separator className="my-10" />

        <section className="space-y-6">
          <h2 className="text-2xl font-semibold tracking-tight">Step by step</h2>

          <div className="space-y-8">
            <div className="relative pl-14">
              <div className="absolute left-0 top-0 flex h-9 w-9 items-center justify-center rounded-full border bg-background text-sm font-semibold">1</div>
              <h3 className="text-lg font-semibold">Install the CLI</h3>
              <p className="mb-3 mt-1 text-sm text-zinc-600 dark:text-zinc-300">Install the ai-skills SDK and command-line tools.</p>
              <CodeBlock language="bash" code={`pip install ai-skills-sdk`} />
            </div>

            <div className="relative pl-14">
              <div className="absolute left-0 top-0 flex h-9 w-9 items-center justify-center rounded-full border bg-background text-sm font-semibold">2</div>
              <h3 className="text-lg font-semibold">Create your skill</h3>
              <p className="mb-3 mt-1 text-sm text-zinc-600 dark:text-zinc-300">Scaffold a new skill and define the metadata, IO schema, and execution block.</p>
              <div className="space-y-3">
                <CodeBlock language="bash" code={`aiskills init my-skill-name`} />
                <CodeBlock language="yaml" code={minimalSkillYaml} />
              </div>
            </div>

            <div className="relative pl-14">
              <div className="absolute left-0 top-0 flex h-9 w-9 items-center justify-center rounded-full border bg-background text-sm font-semibold">3</div>
              <h3 className="text-lg font-semibold">Validate and audit</h3>
              <p className="mb-3 mt-1 text-sm text-zinc-600 dark:text-zinc-300">`validate` checks schema correctness; `--audit` scans for insecure patterns and leaked secrets.</p>
              <CodeBlock language="bash" code={`aiskills validate skill.yaml\naiskills validate --audit skill.yaml`} />
            </div>

            <div className="relative pl-14">
              <div className="absolute left-0 top-0 flex h-9 w-9 items-center justify-center rounded-full border bg-background text-sm font-semibold">4</div>
              <h3 className="text-lg font-semibold">Test it locally</h3>
              <p className="mb-3 mt-1 text-sm text-zinc-600 dark:text-zinc-300">Run the skill with representative input before publishing.</p>
              <CodeBlock language="bash" code={`aiskills run skill.yaml --input '{"input_text": "hello world"}'`} />
            </div>

            <div className="relative pl-14">
              <div className="absolute left-0 top-0 flex h-9 w-9 items-center justify-center rounded-full border bg-background text-sm font-semibold">5</div>
              <h3 className="text-lg font-semibold">Authenticate</h3>
              <p className="mb-3 mt-1 text-sm text-zinc-600 dark:text-zinc-300">Authenticates via GitHub OAuth and stores credentials locally.</p>
              <CodeBlock language="bash" code={`aiskills login`} />
            </div>

            <div className="relative pl-14">
              <div className="absolute left-0 top-0 flex h-9 w-9 items-center justify-center rounded-full border bg-background text-sm font-semibold">6</div>
              <h3 className="text-lg font-semibold">Publish</h3>
              <p className="mb-3 mt-1 text-sm text-zinc-600 dark:text-zinc-300">Publish your validated skill. Use `--dry-run` to preview without creating a release.</p>
              <CodeBlock language="bash" code={`aiskills publish skill.yaml`} />
            </div>
          </div>
        </section>

        <Separator className="my-10" />

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold tracking-tight">Skill types</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <Badge variant="outline" className={typeBadgeClass("prompt")}>prompt</Badge>
                <CardDescription>Use for LLM-driven text tasks with prompt templates.</CardDescription>
              </CardHeader>
              <CardContent>
                <CodeBlock language="yaml" code={executionTypeSnippets.prompt} />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <Badge variant="outline" className={typeBadgeClass("tool_call")}>tool_call</Badge>
                <CardDescription>Use for calling external APIs or service endpoints.</CardDescription>
              </CardHeader>
              <CardContent>
                <CodeBlock language="yaml" code={executionTypeSnippets.tool_call} />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <Badge variant="outline" className={typeBadgeClass("code")}>code</Badge>
                <CardDescription>Use for deterministic transformations and local compute logic.</CardDescription>
              </CardHeader>
              <CardContent>
                <CodeBlock language="yaml" code={executionTypeSnippets.code} />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <Badge variant="outline" className={typeBadgeClass("chain")}>chain</Badge>
                <CardDescription>Use for sequencing multiple skills into one workflow.</CardDescription>
              </CardHeader>
              <CardContent>
                <CodeBlock language="yaml" code={executionTypeSnippets.chain} />
              </CardContent>
            </Card>
          </div>
        </section>

        <Separator className="my-10" />

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold tracking-tight">Rules and guidelines</h2>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Validate first</CardTitle>
                <CardDescription>Skills must pass `aiskills validate` before publishing.</CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">No hardcoded secrets</CardTitle>
                <CardDescription>Use environment variable references instead of embedding credentials.</CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Benchmarkable behavior</CardTitle>
                <CardDescription>Skills should be deterministic enough to produce stable benchmark results.</CardDescription>
              </CardHeader>
            </Card>
          </div>
        </section>

        <Separator className="my-10" />

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold tracking-tight">Resources</h2>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Read the Spec</CardTitle>
                <CardDescription>Review the full skill schema and protocol details.</CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild variant="outline" className="w-full">
                  <a href="https://github.com/davyjones7321/AI-skills/blob/main/docs/SPEC.md" target="_blank" rel="noreferrer">
                    Open Specification
                  </a>
                </Button>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">See Example Skills</CardTitle>
                <CardDescription>Browse published skills and study real-world patterns.</CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild variant="outline" className="w-full">
                  <Link href="/skills">Browse Skills</Link>
                </Button>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Contributing Guide</CardTitle>
                <CardDescription>Learn contribution standards and the expected workflow.</CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild variant="outline" className="w-full">
                  <a href="https://github.com/davyjones7321/AI-skills/blob/main/CONTRIBUTING.md" target="_blank" rel="noreferrer">
                    Open Guide
                  </a>
                </Button>
              </CardContent>
            </Card>
          </div>
        </section>

        <div className="mt-12 rounded-lg border bg-zinc-50 p-4 text-sm text-zinc-700 dark:bg-zinc-900/20 dark:text-zinc-300">
          <div className="flex items-center gap-2 font-medium">
            <CheckCircle2 className="h-4 w-4" />
            Ready when you are
          </div>
          <p className="mt-2">
            Start with a minimal skill, validate early, and publish often. Skills are versioned and immutable, so each release becomes a reusable building block for the ecosystem.
          </p>
        </div>
      </div>
    </main>
  )
}
