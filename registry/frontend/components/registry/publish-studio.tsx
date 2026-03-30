"use client"

import Link from "next/link"
import { ChangeEvent, DragEvent, useEffect, useMemo, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { CheckCircle2, FileUp, Github, Loader2, Plus, UploadCloud } from "lucide-react"
import { CodeBlock } from "@/components/ui/code-block"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { publishSkillFile, ApiError } from "@/lib/api"
import { useAuth } from "@/lib/auth"
import { SKILL_CATEGORIES } from "@/lib/skill-categories"
import {
  buildSkillYaml,
  createEmptyInput,
  createEmptyOutput,
  createInitialBuildSkillFormState,
  getUploadPreview,
  type BuildSkillFormErrors,
  type BuildSkillFormState,
  validateBuildSkillForm,
} from "@/lib/publish-utils"
import type { SkillDetail } from "@/lib/types"
import { cn } from "@/lib/utils"

function InlineError({ message }: { message?: string }) {
  if (!message) return null
  return <p className="text-sm text-red-600">{message}</p>
}

function SignInGate({ next = "/publish" }: { next?: string }) {
  return (
    <Card className="border-dashed">
      <CardHeader className="space-y-3 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border bg-zinc-50">
          <Github className="h-6 w-6" />
        </div>
        <CardTitle>Sign in with GitHub to publish</CardTitle>
        <CardDescription>Your GitHub username will be used as the skill author automatically.</CardDescription>
      </CardHeader>
      <CardContent>
        <Button asChild className="w-full">
          <Link href={`/login?next=${encodeURIComponent(next)}`}>
            <Github className="h-4 w-4" />
            Sign in with GitHub to publish
          </Link>
        </Button>
      </CardContent>
    </Card>
  )
}

function SuccessState({ skill }: { skill: SkillDetail }) {
  const detailHref = `/skills/${skill.author}/${skill.id}`

  return (
    <Card className="border-emerald-200 bg-emerald-50/70">
      <CardHeader className="space-y-3">
        <div className="flex items-center gap-2 text-emerald-700">
          <CheckCircle2 className="h-5 w-5" />
          <span className="text-sm font-medium">Publish complete</span>
        </div>
        <CardTitle>{skill.name} is live</CardTitle>
        <CardDescription>
          Redirecting to <span className="font-mono">{skill.author}/{skill.id}</span> now.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Button asChild>
          <Link href={detailHref}>Open skill detail page</Link>
        </Button>
      </CardContent>
    </Card>
  )
}

export function PublishStudio() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const { user, isLoading, isAuthenticated } = useAuth()
  const [activeTab, setActiveTab] = useState("upload")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadYaml, setUploadYaml] = useState("")
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState<SkillDetail | null>(null)
  const [buildSuccess, setBuildSuccess] = useState<SkillDetail | null>(null)
  const [buildServerError, setBuildServerError] = useState<string | null>(null)
  const [formState, setFormState] = useState<BuildSkillFormState>(createInitialBuildSkillFormState)
  const [formErrors, setFormErrors] = useState<BuildSkillFormErrors>({})
  const [buildPreviewYaml, setBuildPreviewYaml] = useState("")
  const [isDragActive, setIsDragActive] = useState(false)
  const [isPublishingUpload, setIsPublishingUpload] = useState(false)
  const [isPublishingBuild, setIsPublishingBuild] = useState(false)

  useEffect(() => {
    const publishedSkill = uploadSuccess ?? buildSuccess
    if (!publishedSkill) {
      return
    }

    const timer = window.setTimeout(() => {
      router.push(`/skills/${publishedSkill.author}/${publishedSkill.id}`)
    }, 1500)

    return () => window.clearTimeout(timer)
  }, [buildSuccess, router, uploadSuccess])

  const uploadPreview = useMemo(() => {
    if (!uploadYaml) return null
    return getUploadPreview(uploadYaml)
  }, [uploadYaml])

  const resetPublishState = () => {
    setUploadError(null)
    setBuildServerError(null)
    setUploadSuccess(null)
    setBuildSuccess(null)
  }

  const loadSelectedFile = async (file: File | null) => {
    resetPublishState()
    if (!file) {
      setSelectedFile(null)
      setUploadYaml("")
      return
    }

    try {
      const text = await file.text()
      setSelectedFile(file)
      setUploadYaml(text)
      setUploadError(null)
    } catch {
      setSelectedFile(null)
      setUploadYaml("")
      setUploadError("Failed to read the selected file.")
    }
  }

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    await loadSelectedFile(event.target.files?.[0] ?? null)
  }

  const handleUploadDrop = async (event: DragEvent<HTMLButtonElement>) => {
    event.preventDefault()
    setIsDragActive(false)
    await loadSelectedFile(event.dataTransfer.files?.[0] ?? null)
  }

  const handleUploadPublish = async () => {
    if (!selectedFile) {
      setUploadError("Choose a skill.yaml file before publishing.")
      return
    }

    setIsPublishingUpload(true)
    setUploadError(null)
    try {
      const published = await publishSkillFile(selectedFile)
      setUploadSuccess(published)
    } catch (error) {
      setUploadError(error instanceof ApiError ? error.message : "Publishing failed.")
    } finally {
      setIsPublishingUpload(false)
    }
  }

  const updateInput = (index: number, field: "name" | "type" | "required", value: string | boolean) => {
    setFormState((current) => ({
      ...current,
      inputs: current.inputs.map((input, inputIndex) =>
        inputIndex === index ? { ...input, [field]: value } : input
      ),
    }))
  }

  const updateOutput = (index: number, field: "name" | "type", value: string) => {
    setFormState((current) => ({
      ...current,
      outputs: current.outputs.map((output, outputIndex) =>
        outputIndex === index ? { ...output, [field]: value } : output
      ),
    }))
  }

  const buildYamlIfValid = () => {
    const nextErrors = validateBuildSkillForm(formState)
    setFormErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) {
      setBuildPreviewYaml("")
      return null
    }

    const yaml = buildSkillYaml(formState, user?.username ?? "github-user")
    setBuildPreviewYaml(yaml)
    return yaml
  }

  const handlePreview = () => {
    setBuildServerError(null)
    buildYamlIfValid()
  }

  const handleBuildPublish = async () => {
    const yaml = buildYamlIfValid()
    if (!yaml) {
      return
    }

    if (!isAuthenticated) {
      setBuildServerError("Sign in with GitHub to publish.")
      return
    }

    setIsPublishingBuild(true)
    setBuildServerError(null)
    try {
      const file = new File([yaml], "skill.yaml", { type: "text/yaml" })
      const published = await publishSkillFile(file)
      setBuildSuccess(published)
    } catch (error) {
      setBuildServerError(error instanceof ApiError ? error.message : "Publishing failed.")
    } finally {
      setIsPublishingBuild(false)
    }
  }

  const publishResult = uploadSuccess ?? buildSuccess
  if (publishResult) {
    return (
      <main className="min-h-screen bg-background text-foreground">
        <div className="container max-w-4xl px-4 py-12 md:px-6 md:py-16">
          <SuccessState skill={publishResult} />
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="container max-w-6xl px-4 py-12 md:px-6 md:py-14">
        <div className="mb-8 text-sm text-zinc-500">
          <Link href="/" className="hover:text-zinc-900 dark:hover:text-zinc-100">
            Home
          </Link>
          <span className="mx-2">/</span>
          <span>Publish</span>
        </div>

        <section className="space-y-4">
          <Badge variant="outline">Web publishing</Badge>
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl">Publish a skill from your browser</h1>
          <p className="max-w-3xl text-zinc-600 dark:text-zinc-300 md:text-lg">
            Upload an existing <span className="font-mono">skill.yaml</span> or build one from a guided form. We’ll
            publish it using your GitHub identity.
          </p>
        </section>

        <Separator className="my-8" />

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="upload">Upload YAML</TabsTrigger>
            <TabsTrigger value="build">Build Form</TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="space-y-6">
            {isLoading ? (
              <Card>
                <CardContent className="flex items-center gap-3 p-6 text-sm text-zinc-600">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Checking your sign-in status…
                </CardContent>
              </Card>
            ) : !isAuthenticated ? (
              <SignInGate />
            ) : (
              <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
                <Card>
                  <CardHeader>
                    <CardTitle>Upload your skill.yaml</CardTitle>
                    <CardDescription>Drag and drop a file here, or browse from your device.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <button
                      type="button"
                      onDragOver={(event) => {
                        event.preventDefault()
                        setIsDragActive(true)
                      }}
                      onDragLeave={() => setIsDragActive(false)}
                      onDrop={(event) => void handleUploadDrop(event)}
                      onClick={() => fileInputRef.current?.click()}
                      className={cn(
                        "flex min-h-56 w-full flex-col items-center justify-center rounded-xl border border-dashed px-6 py-8 text-center transition-colors",
                        isDragActive ? "border-zinc-900 bg-zinc-50" : "border-zinc-300 hover:border-zinc-500"
                      )}
                    >
                      <UploadCloud className="mb-3 h-8 w-8 text-zinc-500" />
                      <p className="font-medium">Drop a skill.yaml file here</p>
                      <p className="mt-2 text-sm text-zinc-500">or click to browse from your computer</p>
                    </button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".yaml,.yml,text/yaml,text/x-yaml"
                      className="hidden"
                      onChange={(event) => void handleFileChange(event)}
                    />
                    {selectedFile ? (
                      <div className="rounded-lg border bg-zinc-50/60 px-4 py-3 text-sm">
                        <div className="flex items-center gap-2 font-medium">
                          <FileUp className="h-4 w-4" />
                          {selectedFile.name}
                        </div>
                        <div className="mt-1 text-zinc-500">{Math.max(1, Math.round(selectedFile.size / 1024))} KB</div>
                      </div>
                    ) : null}
                    <InlineError message={uploadError ?? undefined} />
                    <Button onClick={() => void handleUploadPublish()} disabled={!selectedFile || isPublishingUpload}>
                      {isPublishingUpload ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                      Publish
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Preview</CardTitle>
                    <CardDescription>We’ll publish this using @{user?.username} as the author.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {uploadPreview ? (
                      <div className="grid gap-3 rounded-lg border bg-zinc-50/60 p-4 text-sm sm:grid-cols-2">
                        <div>
                          <div className="text-zinc-500">Name</div>
                          <div className="font-medium">{uploadPreview.name}</div>
                        </div>
                        <div>
                          <div className="text-zinc-500">ID</div>
                          <div className="font-mono">{uploadPreview.id}</div>
                        </div>
                        <div>
                          <div className="text-zinc-500">Version</div>
                          <div>{uploadPreview.version}</div>
                        </div>
                        <div>
                          <div className="text-zinc-500">Execution Type</div>
                          <div>{uploadPreview.execType}</div>
                        </div>
                      </div>
                    ) : (
                      <p className="text-sm text-zinc-500">Select a YAML file to preview its contents.</p>
                    )}
                    {uploadYaml ? <CodeBlock language="yaml" code={uploadYaml} /> : null}
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          <TabsContent value="build" className="space-y-6">
            <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
              <Card>
                <CardHeader>
                  <CardTitle>Build a skill step by step</CardTitle>
                  <CardDescription>Fill in the essentials and we’ll generate the YAML for you.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {!isLoading && !isAuthenticated ? (
                    <div className="rounded-lg border border-dashed p-4 text-sm text-zinc-600">
                      Sign in before publishing. You can still draft the form below, and we’ll use your GitHub username as the author once you log in.
                    </div>
                  ) : null}

                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Skill ID</label>
                      <Input
                        value={formState.id}
                        onChange={(event) => setFormState((current) => ({ ...current, id: event.target.value }))}
                        placeholder="my-skill-name"
                      />
                      <InlineError message={formErrors.id} />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Version</label>
                      <Input
                        value={formState.version}
                        onChange={(event) => setFormState((current) => ({ ...current, version: event.target.value }))}
                        placeholder="1.0.0"
                      />
                      <InlineError message={formErrors.version} />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Name</label>
                    <Input
                      value={formState.name}
                      onChange={(event) => setFormState((current) => ({ ...current, name: event.target.value }))}
                      placeholder="My Skill"
                    />
                    <InlineError message={formErrors.name} />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Description</label>
                    <textarea
                      value={formState.description}
                      onChange={(event) => setFormState((current) => ({ ...current, description: event.target.value }))}
                      placeholder="What does this skill do?"
                      className="min-h-28 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    />
                    <InlineError message={formErrors.description} />
                  </div>

                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Category</label>
                      <select
                        value={formState.category}
                        onChange={(event) =>
                          setFormState((current) => ({ ...current, category: event.target.value as BuildSkillFormState["category"] }))
                        }
                        className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                      >
                        <option value="">Select a category</option>
                        {SKILL_CATEGORIES.map((category) => (
                          <option key={category} value={category}>
                            {category}
                          </option>
                        ))}
                      </select>
                      <InlineError message={formErrors.category} />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Execution Type</label>
                      <select
                        value={formState.execType}
                        onChange={(event) =>
                          setFormState((current) => ({ ...current, execType: event.target.value as BuildSkillFormState["execType"] }))
                        }
                        className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                      >
                        <option value="prompt">prompt</option>
                        <option value="tool_call">tool_call</option>
                        <option value="code">code</option>
                        <option value="chain">chain</option>
                      </select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Tags</label>
                    <Input
                      value={formState.tags}
                      onChange={(event) => setFormState((current) => ({ ...current, tags: event.target.value }))}
                      placeholder="summarization, nlp, productivity"
                    />
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between gap-3">
                      <h2 className="text-lg font-semibold">Inputs</h2>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          setFormState((current) => ({ ...current, inputs: [...current.inputs, createEmptyInput()] }))
                        }
                      >
                        <Plus className="h-4 w-4" />
                        Add another input
                      </Button>
                    </div>
                    {formState.inputs.map((input, index) => (
                      <div key={`input-${index}`} className="grid gap-3 rounded-lg border p-4 md:grid-cols-[1fr_1fr_auto]">
                        <Input
                          value={input.name}
                          onChange={(event) => updateInput(index, "name", event.target.value)}
                          placeholder="Input name"
                        />
                        <Input
                          value={input.type}
                          onChange={(event) => updateInput(index, "type", event.target.value)}
                          placeholder="string"
                        />
                        <label className="flex items-center gap-2 text-sm font-medium">
                          <input
                            type="checkbox"
                            checked={Boolean(input.required)}
                            onChange={(event) => updateInput(index, "required", event.target.checked)}
                          />
                          Required
                        </label>
                      </div>
                    ))}
                    {formErrors.inputs?.map((error) => (
                      <InlineError key={error} message={error} />
                    ))}
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between gap-3">
                      <h2 className="text-lg font-semibold">Outputs</h2>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          setFormState((current) => ({ ...current, outputs: [...current.outputs, createEmptyOutput()] }))
                        }
                      >
                        <Plus className="h-4 w-4" />
                        Add another output
                      </Button>
                    </div>
                    {formState.outputs.map((output, index) => (
                      <div key={`output-${index}`} className="grid gap-3 rounded-lg border p-4 md:grid-cols-2">
                        <Input
                          value={output.name}
                          onChange={(event) => updateOutput(index, "name", event.target.value)}
                          placeholder="Output name"
                        />
                        <Input
                          value={output.type}
                          onChange={(event) => updateOutput(index, "type", event.target.value)}
                          placeholder="string"
                        />
                      </div>
                    ))}
                    {formErrors.outputs?.map((error) => (
                      <InlineError key={error} message={error} />
                    ))}
                  </div>

                  {formState.execType === "prompt" ? (
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Prompt Template</label>
                      <textarea
                        value={formState.promptTemplate}
                        onChange={(event) => setFormState((current) => ({ ...current, promptTemplate: event.target.value }))}
                        placeholder="Summarize the following input: {document}"
                        className="min-h-36 w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
                      />
                      <InlineError message={formErrors.promptTemplate} />
                    </div>
                  ) : null}

                  {formState.execType === "code" ? (
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Code</label>
                      <textarea
                        value={formState.code}
                        onChange={(event) => setFormState((current) => ({ ...current, code: event.target.value }))}
                        placeholder={'output["result"] = input["text"].upper()'}
                        className="min-h-40 w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
                      />
                      <InlineError message={formErrors.code} />
                    </div>
                  ) : null}

                  <div className="flex flex-wrap gap-3">
                    <Button type="button" variant="outline" onClick={handlePreview}>
                      Preview YAML
                    </Button>
                    <Button
                      type="button"
                      onClick={() => void handleBuildPublish()}
                      disabled={isLoading || isPublishingBuild}
                    >
                      {isPublishingBuild ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                      Publish
                    </Button>
                  </div>
                  <InlineError message={buildServerError ?? undefined} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Generated skill.yaml</CardTitle>
                  <CardDescription>
                    Preview the YAML that will be published{user ? ` as @${user.username}` : ""}.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {buildPreviewYaml ? (
                    <CodeBlock language="yaml" code={buildPreviewYaml} />
                  ) : (
                    <p className="text-sm text-zinc-500">Click Preview YAML to generate your skill definition.</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </main>
  )
}
