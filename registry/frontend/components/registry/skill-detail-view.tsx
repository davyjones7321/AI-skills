"use client"

import Link from "next/link"
import { useMemo, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Check, Copy, ShieldCheck } from "lucide-react"
import type { SkillDetail } from "@/lib/types"
import {
  executionBadgeClass,
  formatPublishedDate,
  parseBenchmarks,
  parseChainSteps,
  parseInputs,
  parseOutputs,
} from "@/lib/skill-detail-utils"

export interface SkillDetailProps {
  skill: SkillDetail
}

function CompatibilityChips({ compatibleWith }: { compatibleWith: string[] }) {
  if (!compatibleWith.length) {
    return null
  }
  return (
    <div className="flex flex-wrap gap-2">
      {compatibleWith.map((framework) => (
        <Badge key={framework} variant="outline" className="text-xs">
          {framework}
        </Badge>
      ))}
    </div>
  )
}

function DataTable({
  columns,
  rows,
  emptyText,
}: {
  columns: string[]
  rows: string[][]
  emptyText: string
}) {
  if (!rows.length) {
    return (
      <div className="rounded-lg border border-dashed p-6 text-sm text-zinc-500">
        {emptyText}
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="min-w-full text-sm">
        <thead className="bg-zinc-50 dark:bg-zinc-900/50">
          <tr>
            {columns.map((column) => (
              <th key={column} className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-300">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={`${row[0]}-${rowIndex}`} className="border-t">
              {row.map((cell, cellIndex) => (
                <td key={`${rowIndex}-${cellIndex}`} className="px-4 py-3 align-top">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function SkillDetailView({ skill }: SkillDetailProps) {
  const [hasCopiedInstall, setHasCopiedInstall] = useState(false)
  const [hasCopiedYaml, setHasCopiedYaml] = useState(false)

  const installCommand = `aiskills install ${skill.author}/${skill.id}`
  const inputRows = useMemo(() => parseInputs(skill.inputs), [skill.inputs])
  const outputRows = useMemo(() => parseOutputs(skill.outputs), [skill.outputs])
  const chainSteps = useMemo(() => parseChainSteps(skill.execution), [skill.execution])
  const benchmarkRows = useMemo(() => parseBenchmarks(skill.benchmarks), [skill.benchmarks])

  const copyInstallCommand = async () => {
    await navigator.clipboard.writeText(installCommand)
    setHasCopiedInstall(true)
    window.setTimeout(() => setHasCopiedInstall(false), 2000)
  }

  const copyYaml = async () => {
    await navigator.clipboard.writeText(skill.yaml_content)
    setHasCopiedYaml(true)
    window.setTimeout(() => setHasCopiedYaml(false), 2000)
  }

  return (
    <div className="container max-w-6xl py-10 space-y-8">
      <div className="text-sm text-zinc-500">
        <Link href="/skills" className="hover:text-zinc-900 dark:hover:text-zinc-100">
          Browse
        </Link>
        <span className="mx-2">/</span>
        <span className="font-mono">
          {skill.author}/{skill.id}
        </span>
      </div>

      <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
        <div className="space-y-5">
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl">{skill.name}</h1>
          <div className="flex flex-wrap items-center gap-2 text-sm text-zinc-500">
            <span className="font-semibold text-zinc-900 dark:text-zinc-100">
              {skill.author}
            </span>
            <span>/</span>
            <span>{skill.id}</span>
            <span>@</span>
            <span>{skill.version}</span>
          </div>
          <p className="text-zinc-600 dark:text-zinc-300">{skill.description}</p>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className={executionBadgeClass(skill.exec_type)}>
              {skill.exec_type}
            </Badge>
            {skill.reviewed ? (
              <Badge variant="outline" className="border-emerald-200 bg-emerald-50 text-emerald-700">
                <ShieldCheck className="mr-1 h-3 w-3" />
                Reviewed
              </Badge>
            ) : (
              <Badge variant="outline" className="border-amber-200 bg-amber-50 text-amber-700">
                Unreviewed
              </Badge>
            )}
            <Badge variant="outline">Published {formatPublishedDate(skill.published_at)}</Badge>
          </div>
          <div className="flex flex-wrap gap-2">
            {skill.tags.map((tag) => (
              <Badge key={tag} variant="secondary">
                #{tag}
              </Badge>
            ))}
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Install</CardTitle>
            <CardDescription>Use this command to install the skill.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between rounded-md border bg-zinc-950 px-3 py-2 font-mono text-xs text-zinc-50">
              <span className="mr-3 overflow-x-auto whitespace-nowrap">{installCommand}</span>
              <Button type="button" size="icon" variant="ghost" className="h-7 w-7 text-zinc-50 hover:bg-zinc-800" onClick={copyInstallCommand}>
                {hasCopiedInstall ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>
            <CompatibilityChips compatibleWith={skill.compatible_with} />
          </CardContent>
        </Card>
      </div>

      <Separator />

      <Tabs defaultValue="overview" className="space-y-5">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="benchmarks">Benchmarks</TabsTrigger>
          <TabsTrigger value="yaml">YAML Source</TabsTrigger>
          <TabsTrigger value="versions">Versions</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Description</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-zinc-700 dark:text-zinc-300">{skill.description}</p>
            </CardContent>
          </Card>

          <div className="space-y-3">
            <h3 className="text-lg font-semibold">Inputs</h3>
            <DataTable
              columns={["Name", "Type", "Required", "Description"]}
              rows={inputRows.map((row) => [
                row.name,
                row.type,
                row.required ? "Yes" : "No",
                row.description || "-",
              ])}
              emptyText="No inputs defined."
            />
          </div>

          <div className="space-y-3">
            <h3 className="text-lg font-semibold">Outputs</h3>
            <DataTable
              columns={["Name", "Type", "Description"]}
              rows={outputRows.map((row) => [row.name, row.type, row.description || "-"])}
              emptyText="No outputs defined."
            />
          </div>

          {chainSteps.length ? (
            <div className="space-y-3">
              <h3 className="text-lg font-semibold">Chain Steps</h3>
              <ol className="space-y-2">
                {chainSteps.map((step, index) => (
                  <li key={`${step.name}-${index}`} className="rounded-lg border p-3">
                    <div className="font-medium">
                      {index + 1}. {step.name}
                    </div>
                    {step.description ? (
                      <div className="mt-1 text-sm text-zinc-600 dark:text-zinc-300">{step.description}</div>
                    ) : null}
                  </li>
                ))}
              </ol>
            </div>
          ) : null}
        </TabsContent>

        <TabsContent value="benchmarks" className="space-y-4">
          {benchmarkRows.length ? (
            <div className="grid gap-4 md:grid-cols-2">
              {benchmarkRows.map((benchmark, index) => {
                const progressValue =
                  typeof benchmark.score === "number"
                    ? Math.max(0, Math.min(100, benchmark.score))
                    : 0
                return (
                  <Card key={`${benchmark.model}-${index}`}>
                    <CardHeader>
                      <CardTitle className="text-lg">{benchmark.model}</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <div className="mb-1 text-xs text-zinc-500">Score</div>
                        <div className="h-2 w-full rounded-full bg-zinc-200 dark:bg-zinc-800">
                          <div
                            className="h-2 rounded-full bg-blue-500"
                            style={{ width: `${progressValue}%` }}
                          />
                        </div>
                        <div className="mt-1 text-xs text-zinc-500">
                          {benchmark.score ?? "N/A"}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <div className="text-xs text-zinc-500">Latency</div>
                          <div>{benchmark.latency_ms ?? "N/A"} ms</div>
                        </div>
                        <div>
                          <div className="text-xs text-zinc-500">Cost / call</div>
                          <div>{benchmark.cost_per_call ?? "N/A"}</div>
                        </div>
                        <div className="col-span-2">
                          <div className="text-xs text-zinc-500">Last evaluated</div>
                          <div>{benchmark.last_evaluated || "N/A"}</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          ) : (
            <div className="rounded-lg border border-dashed p-10 text-center text-sm text-zinc-500">
              No benchmarks recorded yet.
            </div>
          )}
        </TabsContent>

        <TabsContent value="yaml">
          <Card>
            <CardHeader className="flex-row items-center justify-between space-y-0">
              <CardTitle className="text-lg">Raw YAML</CardTitle>
              <Button type="button" variant="outline" size="sm" onClick={copyYaml}>
                {hasCopiedYaml ? <Check className="mr-1 h-4 w-4" /> : <Copy className="mr-1 h-4 w-4" />}
                {hasCopiedYaml ? "Copied" : "Copy"}
              </Button>
            </CardHeader>
            <CardContent>
              <pre className="overflow-x-auto rounded-md border bg-zinc-950 p-4 font-mono text-xs text-zinc-100">
                {skill.yaml_content}
              </pre>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="versions">
          <div className="overflow-x-auto rounded-lg border">
            <table className="min-w-full text-sm">
              <thead className="bg-zinc-50 dark:bg-zinc-900/50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-300">Version</th>
                  <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-300">Published</th>
                  <th className="px-4 py-3 text-left font-medium text-zinc-600 dark:text-zinc-300">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-t">
                  <td className="px-4 py-3">{skill.version}</td>
                  <td className="px-4 py-3">{formatPublishedDate(skill.published_at)}</td>
                  <td className="px-4 py-3">
                    <Badge variant="secondary">Current</Badge>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export function SkillDetailSkeleton() {
  return (
    <div className="container max-w-6xl py-10 space-y-8">
      <Skeleton className="h-4 w-48" />
      <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
        <div className="space-y-4">
          <Skeleton className="h-10 w-3/4" />
          <Skeleton className="h-5 w-1/2" />
          <Skeleton className="h-20 w-full" />
          <div className="flex gap-2">
            <Skeleton className="h-6 w-24" />
            <Skeleton className="h-6 w-24" />
            <Skeleton className="h-6 w-24" />
          </div>
        </div>
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-20" />
            <Skeleton className="h-4 w-44" />
          </CardHeader>
          <CardContent className="space-y-3">
            <Skeleton className="h-10 w-full" />
            <div className="flex gap-2">
              <Skeleton className="h-6 w-24" />
              <Skeleton className="h-6 w-24" />
            </div>
          </CardContent>
        </Card>
      </div>
      <Separator />
      <div className="space-y-4">
        <div className="flex gap-2">
          <Skeleton className="h-9 w-24" />
          <Skeleton className="h-9 w-24" />
          <Skeleton className="h-9 w-24" />
          <Skeleton className="h-9 w-24" />
        </div>
        <Skeleton className="h-72 w-full" />
      </div>
    </div>
  )
}

export function SkillNotFoundState() {
  return (
    <div className="container max-w-4xl py-20">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Skill not found</CardTitle>
          <CardDescription>
            The skill you requested could not be loaded.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button asChild>
            <Link href="/skills">Back to Browse Skills</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
