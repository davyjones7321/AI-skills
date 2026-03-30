import type { SkillCategory } from "@/lib/skill-categories"

export type ExecutionType = "prompt" | "tool_call" | "code" | "chain"

export type SkillIOField = {
  name: string
  type: string
  required?: boolean
}

export type BuildSkillFormState = {
  id: string
  version: string
  name: string
  description: string
  category: SkillCategory | ""
  execType: ExecutionType
  tags: string
  inputs: SkillIOField[]
  outputs: SkillIOField[]
  promptTemplate: string
  code: string
}

export type BuildSkillFormErrors = {
  id?: string
  version?: string
  name?: string
  description?: string
  category?: string
  tags?: string
  promptTemplate?: string
  code?: string
  inputs?: string[]
  outputs?: string[]
}

type UploadPreview = {
  id: string
  version: string
  name: string
  execType: string
}

const KEBAB_CASE_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/
const SEMVER_RE = /^\d+\.\d+\.\d+$/

export function createEmptyInput(): SkillIOField {
  return { name: "", type: "string", required: true }
}

export function createEmptyOutput(): SkillIOField {
  return { name: "", type: "string" }
}

export function createInitialBuildSkillFormState(): BuildSkillFormState {
  return {
    id: "",
    version: "1.0.0",
    name: "",
    description: "",
    category: "",
    execType: "prompt",
    tags: "",
    inputs: [createEmptyInput()],
    outputs: [createEmptyOutput()],
    promptTemplate: "",
    code: "",
  }
}

function quoteYamlString(value: string): string {
  return JSON.stringify(value)
}

function formatScalar(value: string | boolean): string {
  return typeof value === "boolean" ? (value ? "true" : "false") : quoteYamlString(value)
}

function toYamlLines(value: unknown, indentLevel = 0): string[] {
  const indent = "  ".repeat(indentLevel)

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return [`${indent}[]`]
    }

    return value.flatMap((item) => {
      if (item && typeof item === "object" && !Array.isArray(item)) {
        const entries = Object.entries(item as Record<string, unknown>)
        if (entries.length === 0) {
          return [`${indent}- {}`]
        }
        const [firstKey, firstValue] = entries[0]
        const firstScalar =
          typeof firstValue === "string" || typeof firstValue === "boolean"
            ? formatScalar(firstValue)
            : null
        const lines: string[] = []
        if (firstScalar !== null) {
          lines.push(`${indent}- ${firstKey}: ${firstScalar}`)
        } else {
          lines.push(`${indent}- ${firstKey}:`)
          lines.push(...toYamlLines(firstValue, indentLevel + 2))
        }
        for (const [key, nestedValue] of entries.slice(1)) {
          if (typeof nestedValue === "string") {
            if (nestedValue.includes("\n")) {
              lines.push(`${indent}  ${key}: |`)
              for (const line of nestedValue.split("\n")) {
                lines.push(`${indent}    ${line}`)
              }
            } else {
              lines.push(`${indent}  ${key}: ${quoteYamlString(nestedValue)}`)
            }
          } else if (typeof nestedValue === "boolean") {
            lines.push(`${indent}  ${key}: ${nestedValue ? "true" : "false"}`)
          } else {
            lines.push(`${indent}  ${key}:`)
            lines.push(...toYamlLines(nestedValue, indentLevel + 2))
          }
        }
        return lines
      }

      if (typeof item === "string") {
        return [`${indent}- ${quoteYamlString(item)}`]
      }

      return [`${indent}- ${String(item)}`]
    })
  }

  if (value && typeof value === "object") {
    const lines: string[] = []
    for (const [key, nestedValue] of Object.entries(value as Record<string, unknown>)) {
      if (nestedValue === undefined) {
        continue
      }
      if (typeof nestedValue === "string") {
        if (nestedValue.includes("\n")) {
          lines.push(`${indent}${key}: |`)
          for (const line of nestedValue.split("\n")) {
            lines.push(`${indent}  ${line}`)
          }
        } else {
          lines.push(`${indent}${key}: ${quoteYamlString(nestedValue)}`)
        }
      } else if (typeof nestedValue === "boolean") {
        lines.push(`${indent}${key}: ${nestedValue ? "true" : "false"}`)
      } else {
        lines.push(`${indent}${key}:`)
        lines.push(...toYamlLines(nestedValue, indentLevel + 1))
      }
    }
    return lines
  }

  if (typeof value === "string") {
    return [`${indent}${quoteYamlString(value)}`]
  }
  if (typeof value === "boolean") {
    return [`${indent}${value ? "true" : "false"}`]
  }
  return [`${indent}${String(value)}`]
}

export function isKebabCase(value: string): boolean {
  return KEBAB_CASE_RE.test(value)
}

export function isSemver(value: string): boolean {
  return SEMVER_RE.test(value)
}

export function splitTags(value: string): string[] {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean)
}

export function validateBuildSkillForm(form: BuildSkillFormState): BuildSkillFormErrors {
  const errors: BuildSkillFormErrors = {}

  if (!isKebabCase(form.id.trim())) {
    errors.id = "Use kebab-case, like my-skill-name."
  }
  if (!isSemver(form.version.trim())) {
    errors.version = "Use semantic version format, like 1.0.0."
  }
  if (!form.name.trim()) {
    errors.name = "Name is required."
  }
  if (!form.description.trim()) {
    errors.description = "Description is required."
  }
  if (!form.category) {
    errors.category = "Choose a category."
  }

  const inputErrors = form.inputs.map((input, index) => {
    if (!input.name.trim()) return `Input ${index + 1} needs a name.`
    if (!input.type.trim()) return `Input ${index + 1} needs a type.`
    return ""
  })
  if (form.inputs.length === 0 || inputErrors.some(Boolean)) {
    errors.inputs = inputErrors.some(Boolean) ? inputErrors.filter(Boolean) : ["Add at least one input."]
  }

  const outputErrors = form.outputs.map((output, index) => {
    if (!output.name.trim()) return `Output ${index + 1} needs a name.`
    if (!output.type.trim()) return `Output ${index + 1} needs a type.`
    return ""
  })
  if (form.outputs.length === 0 || outputErrors.some(Boolean)) {
    errors.outputs = outputErrors.some(Boolean) ? outputErrors.filter(Boolean) : ["Add at least one output."]
  }

  if (form.execType === "prompt" && !form.promptTemplate.trim()) {
    errors.promptTemplate = "Prompt skills need a prompt template."
  }
  if (form.execType === "code" && !form.code.trim()) {
    errors.code = "Code skills need source code."
  }

  return errors
}

export function buildSkillYaml(form: BuildSkillFormState, author: string): string {
  const tags = splitTags(form.tags)
  const execution: Record<string, unknown> =
    form.execType === "prompt"
      ? {
          type: "prompt",
          prompt_template: form.promptTemplate.trim(),
        }
      : form.execType === "code"
        ? {
            type: "code",
            language: "python",
            source: form.code.trim(),
          }
        : form.execType === "tool_call"
          ? {
              type: "tool_call",
              endpoint: "https://api.example.com/run",
            }
          : {
              type: "chain",
              steps: [
                {
                  skill: "example-step",
                },
              ],
            }

  const skillDocument = {
    skill: {
      id: form.id.trim(),
      version: form.version.trim(),
      name: form.name.trim(),
      description: form.description.trim(),
      author,
      category: form.category,
      tags,
      inputs: form.inputs.map((input) => ({
        name: input.name.trim(),
        type: input.type.trim(),
        required: Boolean(input.required),
      })),
      outputs: form.outputs.map((output) => ({
        name: output.name.trim(),
        type: output.type.trim(),
      })),
      execution,
    },
  }

  return `${toYamlLines(skillDocument).join("\n")}\n`
}

export function getUploadPreview(rawYaml: string): UploadPreview {
  const id = rawYaml.match(/^\s+id:\s*([^\n]+)$/m)?.[1]?.trim() ?? "Unknown"
  const version = rawYaml.match(/^\s{2}version:\s*([^\n]+)$/m)?.[1]?.trim() ?? "Unknown"
  const name = rawYaml.match(/^\s{2}name:\s*([^\n]+)$/m)?.[1]?.trim() ?? "Unknown"
  const execType = rawYaml.match(/^\s{4}type:\s*([^\n]+)$/m)?.[1]?.trim() ?? "Unknown"
  return {
    id: id.replace(/^["']|["']$/g, ""),
    version: version.replace(/^["']|["']$/g, ""),
    name: name.replace(/^["']|["']$/g, ""),
    execType: execType.replace(/^["']|["']$/g, ""),
  }
}
