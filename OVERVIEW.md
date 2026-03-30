# ai-skills — Complete Project Overview

> Last updated: March 25, 2026  
> Spec Version: v0.1  
> Status: Alpha MVP — registry web app and API are live in development

---

## Table of Contents

1. [The Problem](#1-the-problem)
2. [The Idea — In Detail](#2-the-idea--in-detail)
3. [How It Works — End to End](#3-how-it-works--end-to-end)
4. [The Three Layers](#4-the-three-layers)
5. [Project Structure](#5-project-structure)
6. [What Has Been Built](#6-what-has-been-built)
7. [What Still Needs to Be Built](#7-what-still-needs-to-be-built)
8. [Setup & Installation](#8-setup--installation)
9. [How to Run the Project](#9-how-to-run-the-project)
10. [The Skill Format — Explained](#10-the-skill-format--explained)
11. [The Four Execution Types](#11-the-four-execution-types)
12. [The SDK — Commands Reference](#12-the-sdk--commands-reference)
13. [The Registry](#13-the-registry)
14. [Technology Stack](#14-technology-stack)
15. [Roadmap](#15-roadmap)
16. [Why This Idea Wins](#16-why-this-idea-wins)

---

## 1. The Problem

The AI agent ecosystem is growing at an extraordinary pace. There are now dozens of major frameworks that developers use to build AI-powered applications — **LangChain**, **AutoGen**, **CrewAI**, **Semantic Kernel**, **Haystack**, **LlamaIndex**, and more appearing every month.

Every one of these frameworks lets you define "skills" — small, reusable units of AI capability. A skill might summarize a document, classify the sentiment of a review, translate text, search the web, or extract data from a PDF. These are the building blocks of AI agents.

**The problem is that every framework has its own completely different format for defining skills.**

A skill written for LangChain looks like this:

```python
# LangChain version
from langchain.tools import BaseTool
class SummarizeTool(BaseTool):
    name = "summarize"
    def _run(self, document: str) -> str:
        ...
```

The same skill written for AutoGen looks completely different:

```python
# AutoGen version
from autogen_core.tools import FunctionTool
def summarize(document: str) -> dict:
    ...
summarize_tool = FunctionTool(summarize, description="...")
```

And for CrewAI it is different again:

```python
# CrewAI version
from crewai.tools import BaseTool
class SummarizeTool(BaseTool):
    name: str = "Summarizer"
    def _run(self, document: str) -> dict:
        ...
```

This means:

- A developer who builds a great summarization skill for LangChain **cannot share it** with a developer who uses AutoGen. They have to rewrite it from scratch.
- Companies that switch frameworks (which happens often as the ecosystem evolves) have to **rewrite their entire skill library**.
- There is no central place to discover, share, and reuse skills across the community.
- There is no standard way to measure or compare skill quality — latency, cost, accuracy.

This is the same problem the early web had before HTML. Every browser rendered pages differently. HTML became the universal language that solved this — you write once, it works everywhere.

**ai-skills is HTML for AI agent skills.**

---

## 2. The Idea — In Detail

### The Core Concept

ai-skills introduces a single, open, framework-agnostic file format for defining AI skills. It is called a `skill.yaml` file. This file describes everything about a skill in plain, human-readable language:

- What the skill is called and what it does
- What inputs it takes and what outputs it produces
- How it executes (via a prompt, an API call, a chain of steps, or code)
- How to test it and measure its quality

Once a skill is defined in this format, the **ai-skills SDK automatically translates it** into native code for any framework the developer wants to use. The developer writes the skill once. The SDK generates the LangChain version, the AutoGen version, the CrewAI version — whatever is needed.

### The Registry

Beyond the format itself, ai-skills includes a **public registry** — a searchable hub where developers can publish and discover skills. Think of it like npm (the package manager for JavaScript) but specifically for AI skills. Every skill in the registry shows:

- Its schema — exactly what inputs and outputs it has
- Benchmark data — verified latency, cost per call, and accuracy metrics
- Framework compatibility — which frameworks it can be exported to
- Version history — every published version is immutable and tracked

### The Network Effect

The power of ai-skills comes from its network effect. Every new framework that adopts the format makes every existing skill in the registry more valuable. Every new skill published to the registry makes the format more attractive to adopt. This is the same dynamic that made npm, PyPI, and Docker Hub grow into essential infrastructure.

### What Makes This Different From Everything Else

There are many AI agent frameworks. There are plugin systems and tool registries. But nobody has built:

1. A **framework-agnostic open standard** (not owned by any single framework vendor)
2. A **universal registry** with verified benchmark metrics (not just user ratings)
3. An **automatic adapter/exporter system** (not just documentation for how to port skills manually)

ai-skills occupies a unique position: it is infrastructure that sits **between** frameworks, not inside any single one. This is the key insight. It does not compete with LangChain or AutoGen — it makes them all more interoperable.

---

## 3. How It Works — End to End

Here is the complete flow, from a developer writing a skill to another developer using it in their project:

```
┌─────────────────────────────────────────────────────────────────────┐
│  DEVELOPER A  (builds the skill)                                    │
│                                                                     │
│  1. Runs:  aiskills init summarize-document                         │
│     → Creates a skill.yaml scaffold                                 │
│                                                                     │
│  2. Edits skill.yaml — defines inputs, outputs, prompt template     │
│                                                                     │
│  3. Runs:  aiskills validate skill.yaml                             │
│     → SDK checks the file against the spec. Errors flagged.         │
│                                                                     │
│  4. Runs:  aiskills publish                                         │
│     → Skill uploaded to registry                                    │
│     → Test cases run automatically                                  │
│     → Benchmark results recorded                                    │
│     → Skill live at registry.ai-skills.dev/jane/summarize-document  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  REGISTRY  (public hub)                                             │
│                                                                     │
│  • Stores all skill.yaml files                                      │
│  • Shows benchmarks: avg latency 1100ms, avg cost $0.003/call       │
│  • Shows compatibility: LangChain ✓  AutoGen ✓  CrewAI ✓           │
│  • Searchable by name, tag, execution type                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  DEVELOPER B  (uses the skill)                                      │
│                                                                     │
│  1. Finds skill on registry website or via CLI search               │
│                                                                     │
│  2. Runs:  aiskills install ai-skills-team/summarize-document       │
│            aiskills login  (Token MVP: GitHub OAuth)                │
│     → Downloads skill.yaml locally                                  │
│                                                                     │
│  3. Runs:  aiskills export skill.yaml --target autogen              │
│     → SDK auto-generates native AutoGen FunctionTool code           │
│     → File saved as autogen_tool.py, ready to import                │
│                                                                     │
│  4. Developer B plugs the generated code into their agent.          │
│     Zero rewriting. Zero reading source code. Just works.           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. The Three Layers

The entire project is built on three distinct layers, each one depending on the one below it:

### Layer 1 — The Specification (The Standard)

A formal, versioned document (`docs/SPEC.md`) that defines exactly what a valid `skill.yaml` file must contain. This is the foundation. It is model-agnostic, framework-agnostic, and language-agnostic. Anyone can read it and implement a validator or adapter in any programming language.

This is the most important layer. If the spec becomes widely adopted, everything else follows naturally.

### Layer 2 — The SDK (The Tooling)

A Python package (`sdk/`) that implements the spec. It includes:

- A **validator** that checks any `skill.yaml` against the spec
- A **CLI** (`aiskills`) with commands for init, validate, export, info, run, and publish
- **Exporters** — one per framework — that read a `skill.yaml` and generate native framework code automatically

The SDK is what developers interact with daily. It must be fast, reliable, and produce high-quality generated code.

### Layer 3 — The Registry (The Community)

A public hub where skills are published, discovered, and installed. It consists of:

- A **backend API** — FastAPI server that stores skills and serves them
- A **frontend website** — Next.js UI for browsing, searching, reading, and publishing skills
- A **registry index** (`registry/index.json`) — static prototype data retained for documentation/bootstrapping

The registry is what creates the network effect and the community around the standard.

---

## 5. Project Structure

```
ai-skills/
│
├── OVERVIEW.md                  ← You are reading this
├── README.md                    ← Quick-start and project intro
├── CONTRIBUTING.md              ← How to contribute
├── CODE_OF_CONDUCT.md           ← Community standards
├── pyproject.toml               ← Python package config (pip install aiskills)
│
├── .github/
│   ├── workflows/ci.yml         ← CI: validate all skills + security audit
│   ├── ISSUE_TEMPLATE/          ← Bug, feature request, new skill templates
│   └── pull_request_template.md  ← PR template with checklist
│
├── docs/
│   ├── SPEC.md                  ← Official v0.1 specification document
│   ├── SECURITY.md              ← Security model documentation
│   ├── COMPARISON.md            ← How ai-skills compares to alternatives
│   └── LAUNCH_POST.md           ← Blog-style launch post
│
├── examples/                    ← 19 complete, working example skills
│   ├── summarize-document/      ← Summarize a document (prompt)
│   ├── extract-invoice/         ← Extract invoice data (prompt)
│   ├── classify-sentiment/      ← Classify sentiment (prompt)
│   ├── translate-text/          ← Translate text (prompt)
│   ├── extract-email-data/      ← Extract email data (prompt)
│   ├── generate-commit-message/ ← Generate commit messages (prompt)
│   ├── code-review/             ← Review code for issues (prompt)
│   ├── detect-language/         ← Detect text language (prompt)
│   ├── generate-sql/            ← Generate SQL from text (prompt)
│   ├── summarize-to-tweet/      ← Condense to tweet (prompt)
│   ├── web-search/              ← Web search API (tool_call)
│   ├── spell-check/             ← Spell check API (tool_call)
│   ├── weather-lookup/          ← Weather data API (tool_call)
│   ├── word-frequency/          ← Word frequency counter (code)
│   ├── markdown-to-html/        ← MD to HTML converter (code)
│   ├── json-to-csv/             ← JSON to CSV converter (code)
│   ├── calculate-reading-time/  ← Reading time estimator (code)
│   ├── translate-and-summarize/ ← Translate → summarize (chain)
│   └── review-and-fix-code/     ← Review → fix code (chain)
│
├── sdk/
│   ├── cli.py                   ← Main CLI entry point (aiskills command)
│   ├── validator.py             ← Validates skill.yaml against the spec
│   ├── security.py              ← Security auditing and secret detection
│   ├── runner.py                ← Skill execution engine (aiskills run)
│   └── exporters/
│       ├── langchain.py         ← Exports skill to LangChain BaseTool
│       ├── autogen.py           ← Exports skill to AutoGen FunctionTool
│       └── crewai.py            ← Exports skill to CrewAI BaseTool
│
└── registry/
    ├── index.json               ← Static registry index (prototype)
    └── README.md                ← Registry documentation and API spec
```

---

## 6. What Has Been Built

Everything listed below is fully built, tested, and working right now.

### ✅ The Specification (`docs/SPEC.md`)

The complete v0.1 specification document. Covers:

- The full `skill.yaml` schema with every field defined and documented
- Four execution types: `prompt`, `tool_call`, `chain`, `code`
- All supported data types: `string`, `integer`, `number`, `boolean`, `array`, `object`, `file`, `image`, `any`
- Semantic versioning rules for skills
- The benchmark and test case format
- The registry protocol (read and write API design)
- Multiple annotated examples

### ✅ 19 Example Skills (`examples/`)

19 complete, real `skill.yaml` files demonstrating the format across all four execution types:

| Skill | Execution Type | What It Does |
|-------|---------------|--------------|
| `summarize-document` | prompt | Summarizes any document into a summary + key points |
| `extract-invoice` | prompt | Extracts vendor, totals, and line items from invoice text |
| `classify-sentiment` | prompt | Returns positive/negative/neutral + confidence score |
| `translate-text` | prompt | Translates text with auto language detection |
| `extract-email-data` | prompt | Extracts sender, subject, action items, dates, urgency from emails |
| `generate-commit-message` | prompt | Generates conventional commit messages from code diffs |
| `code-review` | prompt | Reviews code for bugs, security, performance, and style |
| `detect-language` | prompt | Detects text language with ISO code and confidence score |
| `generate-sql` | prompt | Generates SQL queries from natural language descriptions |
| `summarize-to-tweet` | prompt | Condenses text to a 280-character tweet |
| `web-search` | tool_call | Calls a search API and returns structured results |
| `spell-check` | tool_call | Checks spelling and grammar via LanguageTool API |
| `weather-lookup` | tool_call | Gets current weather data via OpenWeatherMap API |
| `word-frequency` | code | Counts word frequencies in text with stop word filtering |
| `markdown-to-html` | code | Converts Markdown to HTML (headers, lists, links, code blocks) |
| `json-to-csv` | code | Converts JSON arrays to CSV with nested object flattening |
| `calculate-reading-time` | code | Estimates reading time and provides text statistics |
| `translate-and-summarize` | chain | Detects language → translates → summarizes into key points |
| `review-and-fix-code` | chain | Reviews code for issues → auto-generates fixes |

All 19 pass validation and have benchmark test cases defined.

### ✅ The Validator (`sdk/validator.py`)

A Python script that reads any `skill.yaml` and checks it against the spec. It catches:

- Missing required fields (`id`, `version`, `name`, `description`, `inputs`, `outputs`, `execution`)
- Invalid ID format (must be `[a-z0-9-]+`, max 64 chars)
- Invalid semantic version format
- Invalid data types on inputs and outputs
- Duplicate input or output names
- Prompt templates referencing undefined input variables
- Invalid execution types
- Missing required execution fields per type
- Duplicate test case IDs
- Logical errors (minimum greater than maximum)

It also emits warnings (not errors) for best practices like missing `author`, `license`, or `benchmarks`.

### ✅ Three Framework Exporters (`sdk/exporters/`)

Three Python scripts that each read a `skill.yaml` and generate complete, ready-to-use framework code:

**LangChain exporter (`langchain.py`)** — generates:
- A Pydantic `BaseModel` input schema class with all fields, types, defaults, and Field descriptions
- A `BaseTool` subclass with `name`, `description`, `args_schema`, and a `_run` method
- An `_arun` async method
- A full usage example showing how to plug the tool into a LangChain agent

**AutoGen exporter (`autogen.py`)** — generates:
- A plain Python function with a typed signature matching all skill inputs
- A detailed docstring listing all args and return values
- A `FunctionTool` wrapper registration
- A full usage example with `AssistantAgent`

**CrewAI exporter (`crewai.py`)** — generates:
- A Pydantic input schema class
- A `BaseTool` subclass with `name`, `description`, `args_schema`, and `_run`
- A full usage example with `Agent`, `Task`, and `Crew`

All three exporters handle: required vs optional inputs, default values, Optional type hints, system prompts, prompt templates, and `tool_call` endpoint calls.

### ✅ The CLI (`sdk/cli.py`)

A unified command-line interface with the following working commands:

| Command | What It Does |
|---------|--------------|
| `aiskills init <name>` | Scaffolds a new skill directory with `skill.yaml` and `README.md` |
| `aiskills validate <skill.yaml>` | Validates the skill against the spec, shows errors and warnings |
| `aiskills export <skill.yaml> --target <framework>` | Exports skill to LangChain, AutoGen, or CrewAI |
| `aiskills run <skill.yaml> --input <json>` | Run a skill locally (dry-run or live) |
| `aiskills info <skill.yaml>` | Prints a formatted summary of the skill |
| `aiskills login` | Authenticate with the registry via GitHub OAuth |
| `aiskills publish <skill.yaml>` | Validates, security audits, and securely publishes a local skill to the registry |
| `aiskills install <author>/<id>` | Grabs a skill from the registry and downloads it locally |

### ✅ The Skill Runner (`sdk/runner.py`)

A local execution engine that runs skills directly, supporting all four execution types:

- **`code`** skills execute in a sandboxed Python environment with dangerous modules blocked
- **`prompt`** skills format the template and either display it (dry-run) or call the OpenAI API
- **`tool_call`** skills resolve environment variables and make HTTP requests
- **`chain`** skills display the planned execution flow (full chain execution is planned for a future release)

### ✅ Registry Backend API (`registry/api/`)

A FastAPI server that makes the registry real. It implements pagination, tag filtering, execution type tracking, semver version resolution, GitHub OAuth authentication, and SQLite persistence.

Supported endpoints:
- `POST /skills` — Publish a new skill (Requires auth)
- `GET /skills` — List all skills (paginated)
- `GET /skills/{author}/{id}` — Get latest version of a skill
- `GET /skills/search?q=...&tag=...` — Search by query, tag, or execution type
- `DELETE /skills/{author}/{id}/{version}` — Yank a version (author only)

### ✅ The Registry Prototype (`registry/`)

- `index.json` — a structured JSON file listing example skills with metadata and benchmark data.
- `README.md` — full documentation of the registry including publish rules, the REST API design, and the roadmap.

### ✅ Package Configuration (`pyproject.toml`)

Full Python package configuration so the project can be installed via pip:

```bash
pip install ai-skills-sdk
```

Defines optional dependency groups for each supported framework (`langchain`, `autogen`, `crewai`) and development tools.

---

## 7. What Still Needs to Be Built

The core SDK, registry backend, and registry frontend MVP are now implemented.  
The items below are the remaining work to reach a production-ready v1.

### ✅ Registry Frontend Website (MVP)

A Next.js website where developers can browse, search, and publish skills is now implemented.

**Implemented pages:**

- `/` — Homepage: search bar, featured skills, stats (total skills, total authors)
- `/skills` — Browse all skills with filters by tag and execution type
- `/skills/{author}/{id}` — Skill detail page showing: schema, benchmark scores, install command, framework compatibility badges, version view, YAML source
- `/publish` — Guide for how to publish a skill

**Technology:** Next.js + Tailwind CSS (MVP), designed for Vercel deployment.

**Status:** Complete (MVP). Iteration continues for docs/authors/auth flows.

---

### 🔲 Benchmark CI Runner

When a skill is published to the registry, its test cases should be run automatically by the server — not just trusted from the publisher. This gives the benchmark scores credibility.

**How it works:**

1. Developer runs `aiskills publish`
2. Server receives the skill
3. Server queues a benchmark job
4. Worker process picks up the job, runs each test case against a real LLM, records latency and pass/fail
5. Results stored and displayed on the registry

**Technology:** Synchronous execution initially. Redis job queue and Python worker process to be added later. OpenAI API for running prompt-type skills.

**Estimated effort:** 2–3 weeks

---

### 🔲 `aiskills run` Command (Local Testing)

A command that lets developers run their skill locally before publishing, using their own LLM API key.

```bash
aiskills run skill.yaml --input '{"document": "Hello world..."}'
```

This calls the appropriate LLM, shows the raw output, measures latency, and tells the developer whether the output matches the expected test case assertions.

**Estimated effort:** 1–2 weeks

---

### 🔲 `aiskills test` Command

Runs all test cases defined in `benchmarks.test_cases` and reports pass/fail per case.

```bash
aiskills test skill.yaml
# → Running 3 test cases...
# → ✅ basic-test (820ms)
# → ✅ multilingual (1140ms)
# → ❌ edge-case: expected sentiment=neutral, got sentiment=negative
```

**Estimated effort:** 3–5 days

---

### 🔲 Skill Decay Monitor

One of the most original ideas in the project. Skills degrade silently over time — APIs change, models are updated, prompts that worked 6 months ago may not work as well today. Nobody currently monitors this automatically.

**What it does:** A background job that periodically re-runs test cases for published skills and compares results to the baseline. If a skill's pass rate drops or latency increases significantly, it sends an alert to the skill author.

**Why it matters:** This is what makes ai-skills genuinely trustworthy as a registry. npm doesn't tell you when a package breaks — ai-skills will.

**Estimated effort:** 2–3 weeks

---

### 🔲 Additional Framework Exporters

Currently exporters exist for LangChain, AutoGen, and CrewAI. Still to build:

| Framework | Notes |
|-----------|-------|
| Semantic Kernel | Microsoft's framework, popular in enterprise (C# and Python) |
| Haystack | Popular for RAG and document pipelines |
| LlamaIndex | Popular for knowledge base agents |
| OpenAI function-calling | Raw OpenAI tool format, JSON schema output |
| Anthropic tool use | Raw Anthropic tool format |

Each exporter follows the same pattern as the existing three and should take 1–3 days each.

---

### 🔲 Skill Dependency Resolution

The spec supports skills that depend on other skills via the `dependencies` block. The tooling to resolve, download, and wire up these dependencies does not exist yet. This is similar to how npm installs a package's dependencies automatically.

**Estimated effort:** 1–2 weeks

---

### 🔲 Chain Execution Engine

The `chain` execution type is defined in the spec but not yet executable by the SDK runner. A chain skill calls multiple other skills in sequence, passing outputs from one step as inputs to the next. Building the runtime for this requires the dependency resolver above.

**Estimated effort:** 1–2 weeks

---

## 8. Setup & Installation

### Prerequisites

Make sure you have these installed on your machine before starting:

- Python 3.10 or higher
- pip (comes with Python)
- git

Check your versions:

```bash
python --version    # Should be 3.10+
pip --version
git --version
```

### Step 1 — Install the SDK

```bash
# Install from PyPI (recommended)
pip install ai-skills-sdk
```

Or, for development (editable install from source):

```bash
git clone https://github.com/davyjones7321/AI-skills.git
cd AI-skills
pip install -e .                         # Core only
pip install -e ".[langchain]"            # With LangChain
pip install -e ".[autogen]"              # With AutoGen
pip install -e ".[crewai]"              # With CrewAI
pip install -e ".[all]"                  # Everything
```

### Step 2 — Verify Installation

```bash
aiskills info examples/summarize-document/skill.yaml
```

You should see a formatted summary of the skill printed to your terminal.

---

## 9. How to Run the Project

### Validate a skill

```bash
python sdk/cli.py validate examples/summarize-document/skill.yaml
python sdk/cli.py validate examples/classify-sentiment/skill.yaml --verbose
```

### Get skill info

```bash
python sdk/cli.py info examples/extract-invoice/skill.yaml
```

### Export a skill to a framework

```bash
# Export to LangChain
python sdk/cli.py export examples/summarize-document/skill.yaml --target langchain

# Export to AutoGen with a custom output path
python sdk/cli.py export examples/summarize-document/skill.yaml --target autogen --output my_agent/summarizer.py

# Export to CrewAI
python sdk/cli.py export examples/translate-text/skill.yaml --target crewai
```

### Run a skill locally

```bash
# Dry-run a prompt skill (shows the formatted prompt without calling any API)
python sdk/cli.py run examples/summarize-document/skill.yaml --input-file input.json

# Run a code-type skill (executes immediately, no API key needed)
python sdk/cli.py run examples/word-frequency/skill.yaml --input-file input.json

# Dry-run a tool_call skill (shows resolved URL and parameters)
python sdk/cli.py run examples/weather-lookup/skill.yaml --input-file input.json

# Actually call the LLM (requires OPENAI_API_KEY environment variable)
python sdk/cli.py run examples/summarize-document/skill.yaml --input-file input.json --execute

# Override the model
python sdk/cli.py run examples/summarize-document/skill.yaml --input-file input.json --execute --model gpt-4
```

### Create a new skill from scratch

```bash
python sdk/cli.py init my-new-skill
cd my-new-skill
# Edit skill.yaml to define your skill
python sdk/cli.py validate skill.yaml
python sdk/cli.py export skill.yaml --target langchain
```

### Validate all examples at once

```bash
for dir in examples/*/; do
  python sdk/cli.py validate "${dir}skill.yaml"
done
```

### Run the validator directly

```bash
python sdk/validator.py examples/summarize-document/skill.yaml
python sdk/validator.py examples/extract-invoice/skill.yaml --verbose
```

### Run an exporter directly

```bash
python sdk/exporters/langchain.py examples/summarize-document/skill.yaml
python sdk/exporters/autogen.py examples/classify-sentiment/skill.yaml --output out.py
python sdk/exporters/crewai.py examples/translate-text/skill.yaml --output out.py
```

---

## 10. The Skill Format — Explained

A `skill.yaml` file has five main sections:

### Identity

Who the skill is, what it is called, and what it does.

```yaml
skill:
  id: classify-sentiment       # Unique ID — kebab-case, lowercase, no spaces
  version: 1.0.0               # Semantic version — MAJOR.MINOR.PATCH
  name: Sentiment Classifier   # Human-readable name
  description: |               # Plain English description of what it does
    Classifies the sentiment of a piece of text.
  author: jane-doe             # Your username
  license: MIT                 # Open source license
  tags: [nlp, sentiment]       # Searchable keywords
```

### Inputs

What data the skill needs to run.

```yaml
  inputs:
    - name: text               # The variable name used in the prompt template
      type: string             # Data type
      description: The text to analyze
      required: true           # Must be provided

    - name: granularity
      type: string
      description: How detailed the classification should be
      required: false          # Optional
      default: basic           # Used when not provided
      enum: [basic, detailed]  # Only these values allowed
```

### Outputs

What the skill returns.

```yaml
  outputs:
    - name: sentiment
      type: string
      description: The classified sentiment label

    - name: confidence
      type: number
      description: Score from 0.0 to 1.0
```

### Execution

How the skill actually runs.

```yaml
  execution:
    type: prompt               # This skill runs by prompting an LLM
    system_prompt: |
      You are a precise sentiment analysis engine.
    prompt_template: |
      Analyze the sentiment of: {text}
      Granularity: {granularity}
      Return JSON with: sentiment, confidence, explanation.
    output_parser: json        # Parse the LLM output as JSON
```

### Benchmarks

Test cases and performance data.

```yaml
  benchmarks:
    avg_latency_ms: 600
    avg_cost_per_call_usd: 0.001
    test_cases:
      - id: positive-review
        input:
          text: "This product is amazing!"
          granularity: basic
        expected:
          sentiment: positive
          confidence_min: 0.8
```

---

## 11. The Four Execution Types

### `prompt` — LLM prompt template

The most common type. The skill runs by formatting a prompt template with the inputs and sending it to an LLM.

```yaml
execution:
  type: prompt
  model_hint: any              # Preferred model, or "any"
  system_prompt: "You are..."  # Optional system message
  prompt_template: |
    Do something with {input_text}
  output_parser: json          # none | json | structured
```

### `tool_call` — External API call

The skill runs by calling an external API or function — no LLM involved.

```yaml
execution:
  type: tool_call
  endpoint:
    url: https://api.example.com/search
    method: GET
    headers:
      Authorization: "Bearer {env.MY_API_KEY}"
    params:
      q: "{query}"
```

### `chain` — Multiple skills in sequence

The skill runs by calling other skills one after another, passing outputs from each step as inputs to the next.

```yaml
execution:
  type: chain
  steps:
    - skill: detect-language
      input_map:
        text: "{input_text}"
      output_as: lang_result
    - skill: translate-text
      input_map:
        text: "{input_text}"
        target_language: english
      condition: "{lang_result.language} != english"
    - skill: summarize-document
      input_map:
        document: "{translate_text.translated_text}"
```

### `code` — Execute a Python code block

The skill runs by executing a Python function directly.

```yaml
execution:
  type: code
  language: python
  code: |
    def run(inputs):
        text = inputs["text"]
        return {"word_count": len(text.split())}
```

---

## 12. The SDK — Commands Reference

### `aiskills init <name>`

Creates a new skill directory with a scaffold `skill.yaml` and `README.md`.

```bash
aiskills init my-summarizer
# Creates: my-summarizer/skill.yaml
#          my-summarizer/README.md
```

### `aiskills validate <skill.yaml>`

Validates a skill file against the spec. Exits with code 0 if valid, 1 if not.

```bash
aiskills validate skill.yaml          # Errors only
aiskills validate skill.yaml -v       # Errors + warnings
```

### `aiskills export <skill.yaml> --target <framework>`

Exports a skill to framework-specific code.

```bash
aiskills export skill.yaml --target langchain
aiskills export skill.yaml --target autogen
aiskills export skill.yaml --target crewai
aiskills export skill.yaml --target langchain --output my_tool.py
```

### `aiskills info <skill.yaml>`

Prints a formatted summary of the skill to the terminal.

```bash
aiskills info skill.yaml
```

### Coming soon:

```bash
aiskills test skill.yaml                               # Run test cases
aiskills migrate                                       # Migrate spec version
```

### ✅ Already available:

```bash
aiskills login                                         # Authenticate via GitHub OAuth
aiskills publish skill.yaml                            # Publish to registry
aiskills install author/skill-id                       # Install from registry
aiskills install author/skill-id@1.2.0                 # Install specific version
```

---

## 13. The Registry

### What it is

The registry is the public hub where skills are published and discovered. It is designed to work like npm or PyPI but specifically for AI skills. The key difference from any existing plugin store is that every skill in the registry shows **verified benchmark metrics** — not self-reported numbers, but actual results from running the test cases on the server.

### Current state

Right now the registry exists as a static prototype in `registry/index.json`. It lists all 19 example skills with their metadata and benchmark data. The REST API design is fully specified in `registry/README.md`.

### Planned REST API

```
GET  /skills                            List all skills
GET  /skills/{author}/{id}              Get a skill (latest version)
GET  /skills/{author}/{id}/{version}    Get a specific version
GET  /skills/search?q={query}           Search by name or tag
POST /skills                            Publish a skill (requires auth)
```

### Skill naming convention

Skills in the registry are identified as `{author}/{id}@{version}`:

```
ai-skills-team/summarize-document@1.0.0
jane-doe/extract-invoice@2.1.0
```

### Publishing rules

- Skill IDs must be unique per author
- Published versions are immutable — you cannot overwrite a published version
- All test cases must pass before a skill can be published
- The registry runs test cases independently to verify benchmark claims

---

## 14. Technology Stack

### Current (what is built)

| Component | Technology |
|-----------|-----------|
| Skill format | YAML / JSON |
| Validator | Python 3.10+ |
| CLI | Python (argparse) |
| Exporters | Python (LangChain, AutoGen, CrewAI) |
| Skill runner | Python (sandboxed execution) |
| Registry backend | FastAPI + SQLite + SQLAlchemy |
| Registry frontend | Next.js + Tailwind CSS (Vercel) |
| Registry hosting | Render (API) + Vercel (frontend) |
| Auth | GitHub OAuth + JWT |
| Package config | pyproject.toml (setuptools) / PyPI |

### Planned (what to build)

| Component | Technology | Why |
|-----------|-----------|-----|
| Benchmark CI | Redis + Python worker | Reliable job queue for running test cases |
| Skill decay monitor | Scheduled Python jobs | Periodic re-runs of published skill tests |
| Additional exporters | Python | Semantic Kernel, OpenAI, Anthropic, Haystack, LlamaIndex |
| Database migration | PostgreSQL | Scale beyond SQLite for production load |

---

## 15. Roadmap

### Effort & Timeline Estimate (Adjusted MVP)

As a solo developer, building the entire ecosystem takes time. Here is the adjusted realistic timeline focusing on MVP features (SQLite, static frontend, synchronous benchmarks):

| Phase | Component | Original Est. | Adjusted Est. | Status |
|-------|-----------|------------------|---------------|--------|
| **1** | Core Spec & Parsing | 1 week | 1 week | ✅ Done |
| **1** | Export Adapters | 1 week | 1 week | ✅ Done |
| **2** | Example Library (19 skills) | 1 week | 1 week | ✅ Done |
| **2** | Security & Launch Docs | 1 week | 1 week | ✅ Done |
| **3** | CLI `publish` / `install` | 1 week | 1 week | ✅ Done |
| **3** | Registry Backend (SQLite) | 1–2 weeks | 2–3 weeks | ✅ Done |
| **3** | Registry Frontend (Static) | 2–3 weeks | 1–2 weeks | ✅ Done (Next.js MVP) |
| **4** | CLI `run` (Local Exec) | 3–5 days | 1–2 weeks | ✅ Done |
| **4** | CLI `test` (Benchmarks) | 3–5 days | 1 week | 🔴 Pending |
| **6** | Server-side CI Runner | 1–2 weeks | 1-2 weeks | 🔴 Pending |

**Total time to v1.0 Launch:** ~10–12 weeks of focused effort.

### Phase 1 — Foundation (Complete ✅)

- [x] v0.1 specification document
- [x] Five example skills
- [x] Skill validator
- [x] LangChain exporter
- [x] AutoGen exporter
- [x] CrewAI exporter
- [x] Unified CLI (init, validate, export, info)
- [x] Registry index prototype
- [x] Python package configuration

### Phase 2 — Go Live (Next 2–4 weeks)

- [ ] GitHub repository public
- [ ] Post on HackerNews, Reddit, Discord communities
- [x] `aiskills publish` CLI command
- [x] `aiskills install` CLI command
- [x] Registry backend API (FastAPI + SQLite MVP)
- [x] GitHub OAuth authentication (MVP + token fallback)

### Phase 3 — Community (1–2 months)

- [x] Registry frontend website
- [x] `aiskills run` command (local execution)
- [ ] `aiskills test` command (test case runner)
- [ ] Semantic Kernel exporter
- [ ] OpenAI function-calling format exporter
- [ ] Anthropic tool use format exporter

### Phase 4 — Quality & Trust (2–4 months)

- [ ] Benchmark CI runner (auto-run tests on publish)
- [ ] Skill decay monitor (periodic quality alerts)
- [ ] Skill dependency resolution
- [ ] Chain execution engine
- [ ] Verified author badges

### Phase 5 — Scale (4–6 months)

- [ ] Skill collections and curated packs
- [ ] Web UI for skill testing (no CLI needed)
- [ ] API for third-party framework adapter plugins
- [ ] Skill analytics dashboard for authors
- [ ] Enterprise registry (private skills within an org)

---

## 16. Why This Idea Wins

### Timing is right

The AI agent framework explosion is happening right now. LangChain, AutoGen, CrewAI, and Semantic Kernel all reached significant adoption in 2024–2025. The fragmentation problem is fresh and painful. Nobody has solved it yet. This is the window.

### Nobody owns the interoperability layer

The frameworks themselves cannot solve this problem — they are competitors. No single framework vendor will build something that benefits their rivals equally. This has to come from an independent, neutral, open-source project. That is exactly what ai-skills is.

### Open standards compound over time

Once a standard achieves critical mass, it becomes self-reinforcing. Developers build on it because it has the most skills. Frameworks support it because developers demand it. Skills get published to it because it has the most frameworks. This is the same dynamic that made HTTP, HTML, and JSON into essential infrastructure. ai-skills is positioned to be that for AI skills.

### The registry is a moat

The spec alone can be forked and replicated. But the registry — with its growing library of community-published skills, verified benchmark data, and download counts — cannot be easily replicated. The community data is the defensible asset.

### The benchmark layer is a genuine innovation

No existing skill store or plugin marketplace shows verified performance metrics per skill. Developers currently have no reliable way to compare skills beyond reading documentation and trusting the author. Verified benchmarks — especially with decay monitoring — give ai-skills a level of trust that nothing else offers.

---

*This document should be updated every time a major component is built or the spec is revised.*  
*Current spec version: v0.1 | Current SDK version: 0.1.0*

---

## Session Update — 2026-03-26

A major auth milestone was completed in this session: the registry now has an end-to-end GitHub OAuth flow spanning FastAPI, the Next.js frontend, and the CLI. The backend now issues and verifies 30-day HS256 JWTs, validates OAuth state, fetches verified primary email from GitHub, tracks `last_login`, and supports both browser and CLI auth callbacks. The frontend gained the missing login page, callback handler, auth context/provider, and authenticated header UI. The CLI login flow was upgraded from manual token paste to a localhost callback handoff.

## Session Update — 2026-03-27

Registry deployment and client configuration were tightened up in this session. The backend now builds the GitHub OAuth callback URL from `BASE_URL`, which should be set in production to `https://ai-skills-production-f4f0.up.railway.app`, instead of deriving that callback from the frontend-facing URL. The backend CORS allowlist was also expanded to include `https://ai-skills-omega.vercel.app`. On the SDK side, registry-backed CLI flows now honor `AISKILLS_REGISTRY_URL` for `install`, `publish`, and login-related requests, with the Railway-hosted registry as the default fallback.

## Session Update — 2026-03-27 (Production Hardening)

A full production audit was completed and 10 issues were fixed:

- `config.py`: Removed insecure fallback defaults for `SECRET_KEY`, `JWT_SECRET`, `GITHUB_CLIENT_ID`, and `GITHUB_CLIENT_SECRET` — all are now required. `debug` defaults to `False`.
- `main.py`: Removed placeholder CORS origin, simplified origins to `localhost` + `settings.frontend_url`, replaced deprecated `@app.on_event("startup")` with `lifespan` context manager, health endpoint now only exposes env when `debug=True`.
- `models.py` + `auth.py`: OAuth anti-CSRF states migrated from in-memory dict to a persistent `OAuthState` DB table, surviving container restarts and multi-worker scaling.
- `runner.py`: Removed `getattr` from code sandbox safe builtins to prevent escape via attribute chain traversal.
- `cli.py`: `_resolve_registry_url` now delegates to `auth_config.DEFAULT_REGISTRY_URL` to eliminate duplication.
- `.env.example`: Expanded to document all required production variables.
