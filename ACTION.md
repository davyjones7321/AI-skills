# ai-skills — Master Action Plan

> Everything that needs to be built, developed, and implemented.  
> Check off items as you complete them. Items marked ✅ are already done.

---

## Phase 1 — Foundation (✅ Complete)

- [x] v0.1 specification document (`docs/SPEC.md`)
- [x] Five example skills (`examples/`)
- [x] Skill validator (`sdk/validator.py`)
- [x] LangChain exporter (`sdk/exporters/langchain.py`)
- [x] AutoGen exporter (`sdk/exporters/autogen.py`)
- [x] CrewAI exporter (`sdk/exporters/crewai.py`)
- [x] Unified CLI — `init`, `validate`, `export`, `info` (`sdk/cli.py`)
- [x] Registry index prototype (`registry/index.json`)
- [x] Python package configuration (`pyproject.toml`)

---

## Phase 2 — Pre-Launch Prep

### 2.1 — Additional Example Skills

Build 10–15 more skills to show range and validate all execution types.

**`prompt` type skills:**

- [x] `extract-email-data/skill.yaml` — Pull name, subject, action items from email text
- [x] `generate-commit-message/skill.yaml` — Generate conventional commit messages from code diffs
- [x] `code-review/skill.yaml` — Review a code snippet for bugs and improvements
- [x] `detect-language/skill.yaml` — Detect the language of input text
- [x] `generate-sql/skill.yaml` — Generate SQL queries from natural language descriptions
- [x] `summarize-to-tweet/skill.yaml` — Condense text to a 280-character tweet

**`tool_call` type skills:**

- [x] `spell-check/skill.yaml` — Check spelling via an external API
- [x] `weather-lookup/skill.yaml` — Get weather data for a given location

**`code` type skills (currently zero examples):**

- [x] `word-frequency/skill.yaml` — Count word frequencies in text
- [x] `markdown-to-html/skill.yaml` — Convert basic markdown to HTML
- [x] `json-to-csv/skill.yaml` — Convert JSON data to CSV format
- [x] `calculate-reading-time/skill.yaml` — Estimate reading time for text
- [ ] `resize-image/skill.yaml` — Resize an image to given dimensions
- [ ] `pdf-page-count/skill.yaml` — Count pages in a PDF file

**`chain` type skills (currently zero examples):**

- [x] `translate-and-summarize/skill.yaml` — Detect language → translate → summarize
- [x] `review-and-fix-code/skill.yaml` — Code review → auto-fix suggestions chain

**After creating each skill:**

- [x] Run `aiskills validate` on every new skill
- [x] Update `registry/index.json` with all new skill entries

---

### 2.2 — Spec Improvements

- [x] Add `spec_version` as an optional field to `skill.yaml` schema
  ```yaml
  skill:
    spec_version: "0.1"
  ```
- [x] Add `max_length` as an optional field on string inputs for token limit awareness
  ```yaml
  inputs:
    - name: document
      type: string
      max_length: 50000
  ```
- [x] Add "Spec Versioning Rules" section to `docs/SPEC.md` (patch / minor / major compatibility rules)

---

### 2.3 — Security Layer

#### `sdk/security.py` — New File

- [x] Secret detection scanner — regex patterns for common API key formats (OpenAI, GitHub, generic)
- [x] Dangerous import scanner for `code` type skills — flag `os`, `sys`, `subprocess`, `socket`, etc.
- [x] Suspicious URL scanner for `tool_call` type skills

#### Validator Integration

- [x] Add `--audit` flag to `aiskills validate` that runs security checks
- [x] Warn if `skill.yaml` contains anything that looks like a hardcoded secret
- [x] Warn if `code` type skills import blocked modules

#### Documentation

- [x] Create `docs/SECURITY.md` — document the security model:
  - How `code` skills are sandboxed
  - How secrets should be handled (`{env.VAR_NAME}` pattern)
  - Registry review process for published skills

---

### 2.4 — Documentation & Launch Materials

#### New Files to Create

- [x] `CONTRIBUTING.md` — How to contribute:
  - Adding a new example skill (copy folder, edit YAML, validate)
  - Adding a new exporter (follow existing pattern)
  - Reporting bugs / opening issues
  - Code style and PR guidelines
- [x] `docs/COMPARISON.md` — Competitive positioning table:
  - vs OpenAI function-calling
  - vs Anthropic MCP
  - vs Hugging Face Hub
  - vs LangChain Hub
  - vs CrewAI Tools
- [x] `docs/LAUNCH_POST.md` — Blog-style launch post:
  - Personal hook / why you built it
  - 30-second pitch
  - Terminal demo GIF
  - Link to repo
- [x] `CODE_OF_CONDUCT.md` — Standard open-source code of conduct

#### Update Existing Files

- [x] `README.md` — Add a brief "How This Compares" section (5–10 lines)
- [x] `README.md` — Add badges (Python version, license, build status)
- [x] `README.md` — Add a quick-start section with copy-paste commands
- [x] `OVERVIEW.md` — Update timeline estimates to be more realistic

#### Demo Assets

- [ ] Record terminal demo GIF using [asciinema](https://asciinema.org/) or [VHS](https://github.com/charmbracelet/vhs)
  - Show: `init` → edit YAML → `validate` → `export --target langchain` → `export --target autogen`
- [x] Create a project logo / banner image for the README

---

## Phase 3 — Go Live

### 3.1 — `aiskills publish` CLI Command

- [x] Add `publish` subcommand to `sdk/cli.py`
- [x] Flow:
  1. Read `skill.yaml`
  2. Run `validate` — abort if invalid
  3. Run security audit — warn on issues
  4. Run all test cases locally
  5. Authenticate with registry (GitHub OAuth token or personal token)
  6. Upload skill YAML to registry API
  7. Print the URL where the skill is now live
- [x] Store auth token in `~/.aiskills/config.json`
- [x] Add `--dry-run` flag to simulate without uploading

---

### 3.2 — `aiskills install` CLI Command

- [x] Add `install` subcommand to `sdk/cli.py`
- [x] Support formats:
  ```bash
  aiskills install jane/summarize-document
  aiskills install jane/summarize-document@1.2.0
  ```
- [x] Download `skill.yaml` into a local `skills/` directory
- [x] Add `--export` flag to auto-export after install:
  ```bash
  aiskills install jane/summarize-document --export langchain
  ```
- [x] Create `skills/` directory if it doesn't exist
- [ ] Handle version conflicts (skill already installed at different version) — defer to Phase 6.3

---

### 3.3 — Registry Backend API

#### Tech Stack

- [x] **Framework:** FastAPI (Python)
- [x] **Database:** SQLite (start simple, migrate to PostgreSQL later if needed)
- [x] **Auth:** GitHub OAuth authentication
- [ ] **Hosting:** Railway.app or Render.com

#### Database Schema

- [x] Create `skills` table:
  ```sql
  CREATE TABLE skills (
      id            TEXT,
      author        TEXT,
      version       TEXT,
      name          TEXT,
      description   TEXT,
      yaml_content  TEXT,
      tags          JSON,
      exec_type     TEXT,
      benchmarks    JSON,
      downloads     INTEGER DEFAULT 0,
      reviewed      BOOLEAN DEFAULT FALSE,
      published_at  TIMESTAMP,
      PRIMARY KEY (author, id, version)
  );
  ```

#### API Endpoints

- [x] `POST /skills` — Publish a new skill (authenticated)
  - Validate YAML against spec before storing
  - Reject if version already exists (immutable versions)
  - Run security audit checks
- [x] `GET /skills` — List all skills (paginated)
  - Support `?page=1&limit=20`
  - Return total count for pagination
- [x] `GET /skills/{author}/{id}` — Get latest version of a skill
- [x] `GET /skills/{author}/{id}/{version}` — Get specific version
- [x] `GET /skills/search?q={query}` — Search by name or tag
- [x] `GET /skills/search?tag={tag}` — Filter by tag
- [x] `GET /skills/search?type={exec_type}` — Filter by execution type
- [x] `DELETE /skills/{author}/{id}/{version}` — Yank a version (authenticated, author only)

#### Rate Limiting

- [ ] 60 requests/minute for read endpoints — defer to deployment (add slowapi)
- [ ] 10 requests/minute for publish endpoint — defer to deployment (add slowapi)

#### Other

- [x] CORS configuration for frontend access
- [x] Health check endpoint: `GET /health`
- [x] Seed the database with all example skills on first run
- [x] Write `registry/api/README.md` with setup instructions

---

### 3.4 — Registry Frontend Website

#### Tech Choice (MVP)

- [ ] **Option A (Simpler):** Static site with client-side search using Fuse.js — hosted on GitHub Pages (free)
- [x] **Option B (Richer):** Next.js + Tailwind CSS — hosted on Vercel (free tier)

#### Pages to Build

- [x] **Homepage** (`/`)
  - Search bar
  - Featured skills
  - Stats: total skills, total authors, total downloads
  - Quick-start commands
- [x] **Browse skills** (`/skills`)
  - Filter by tag, execution type
  - Sort by downloads, newest, name
  - Paginated grid/list of skill cards
- [x] **Skill detail page** (`/skills/{author}/{id}`)
  - Full schema display (inputs, outputs)
  - Benchmark scores (latency, cost, accuracy)
  - Install command (copy-to-clipboard)
  - Framework compatibility badges
  - Version history dropdown
  - Raw `skill.yaml` viewer
- [x] **Publish guide** (`/publish`)
  - Step-by-step guide for publishing a skill
  - Link to CLI docs

#### Design

- [x] Responsive layout (mobile + desktop)
- [x] Dark mode
- [x] Skill card component with: name, author, tags, execution type badge, download count
- [x] Copy-to-clipboard for install commands
- [ ] Syntax highlighting for YAML display

#### App Shell

- [x] Persistent sticky header with mobile navigation and active-route highlighting
- [x] Persistent footer with docs/community links and spec badge
- [x] Root layout metadata and favicon update

---

### 3.5 — GitHub Repository Setup

- [x] Initialize git repository
- [x] Create `.gitignore` (Python, Node, IDE files)
- [x] Set up GitHub Actions CI:
  - Run `aiskills validate` on all example skills
  - Run security audit on all example skills
- [x] Add issue templates (bug report, feature request, new skill proposal)
- [x] Add PR template
- [ ] Set up branch protection on `main`
- [ ] Make repository public

---

### 3.6 — Launch Execution

- [ ] Post to Reddit: r/MachineLearning
- [ ] Post to Reddit: r/LangChain
- [ ] Post to Reddit: r/LocalLLaMA
- [ ] Post to HackerNews (Show HN)
- [ ] Post to LangChain Discord
- [ ] Post to AutoGen Discord
- [ ] Post on Twitter/X with demo GIF
- [ ] Respond to all GitHub issues within 24 hours (first month)

---

## Phase 4 — CLI Completion

### 4.1 — `aiskills run` Command (Local Execution)

- [x] Add `run` subcommand to `sdk/cli.py`
- [x] Support all execution types:
  - **`prompt`:** Format prompt template + call LLM API (or dry-run)
  - **`tool_call`:** Make HTTP request to endpoint (or dry-run)
  - **`code`:** Execute Python code in sandbox
  - **`chain`:** Display chain execution plan (placeholder)
- [x] Accept input as JSON:
  ```bash
  aiskills run skill.yaml --input '{"text": "hello"}'
  ```
- [x] Accept input from file:
  ```bash
  aiskills run skill.yaml --input-file input.json
  ```
- [ ] Display: raw output, parsed output, latency
- [ ] Support `--model` flag to override model hint
- [ ] Load API keys from `.env` file or environment variables

#### LLM Provider Support

- [ ] OpenAI (GPT-4, GPT-3.5)
- [ ] Anthropic (Claude)
- [ ] Local models via Ollama
- [ ] Provider auto-detection from `model_hint` field

#### Output Parsing

- [ ] `none` — return raw string
- [ ] `json` — parse as JSON with fallback strategies:
  1. Direct `json.loads()`
  2. Extract from markdown code block
  3. Find first `{...}` or `[...]` block
- [ ] `structured` — validate against output schema

---

### 4.2 — `aiskills test` Command

- [ ] Add `test` subcommand to `sdk/cli.py`
- [ ] Read `benchmarks.test_cases` from `skill.yaml`
- [ ] For each test case:
  1. Run the skill with the test case input
  2. Compare output to `expected` values
  3. Record latency
  4. Report pass/fail
- [ ] Terminal output format:
  ```
  Running 3 test cases...
  ✅ basic-test (820ms)
  ✅ multilingual (1140ms)
  ❌ edge-case: expected sentiment=neutral, got sentiment=negative
  
  Results: 2/3 passed
  ```
- [ ] Support `--verbose` flag for detailed output comparison
- [ ] Exit with code 0 if all pass, 1 if any fail
- [ ] Support assertion types:
  - Exact match
  - Contains
  - `confidence_min` / `confidence_max` range checks
  - Type checking

---

### 4.3 — `aiskills migrate` Command

- [ ] Add `migrate` subcommand to `sdk/cli.py`
- [ ] Read `spec_version` from skill file
- [ ] Apply known field transformations for version upgrades
- [ ] Write updated file (or `--output` to a new file)
- [ ] Report what changed

---

## Phase 5 — Additional Exporters

Each exporter reads a `skill.yaml` and generates native framework code.

- [ ] **Semantic Kernel** exporter (`sdk/exporters/semantic_kernel.py`)
  - Generate `@kernel_function` decorated Python function
  - Handle input/output descriptions
  - Usage example with SK agent
- [ ] **OpenAI function-calling** exporter (`sdk/exporters/openai.py`)
  - Generate JSON schema in OpenAI's tool format
  - Generate the Python function implementation
  - Usage example with `openai.chat.completions.create(tools=[...])`
- [ ] **Anthropic tool use** exporter (`sdk/exporters/anthropic.py`)
  - Generate tool definition in Anthropic's format
  - Generate handler function
  - Usage example with Claude API
- [ ] **Haystack** exporter (`sdk/exporters/haystack.py`)
  - Generate `@component` decorated class
  - Handle pipeline integration
- [ ] **LlamaIndex** exporter (`sdk/exporters/llamaindex.py`)
  - Generate `FunctionTool` with proper schema
  - Usage example with LlamaIndex agent

---

## Phase 6 — Quality & Trust

### 6.1 — Benchmark CI Runner

- [ ] When a skill is published, automatically run its test cases server-side
- [ ] Start simple: synchronous execution on publish
- [ ] Record results: latency, pass/fail, cost (if applicable)
- [ ] Store benchmark results in the database
- [ ] Display verified results on the registry frontend
- [ ] Later: add Redis job queue for async execution
- [ ] Later: add worker process for parallel benchmark runs

---

### 6.2 — Skill Decay Monitor

- [ ] Background scheduled job (cron or scheduled task)
- [ ] Periodically re-run test cases for all published skills
- [ ] Compare results to baseline (original publish-time benchmarks)
- [ ] Flag skills where:
  - Pass rate dropped below original
  - Latency increased by more than 50%
  - Output format changed
- [ ] Notify skill author via email or GitHub issue
- [ ] Display decay status on registry: 🟢 healthy / 🟡 degraded / 🔴 failing
- [ ] Configurable frequency: weekly for popular skills, monthly for others

---

### 6.3 — Skill Dependency Resolution

- [ ] Parse `dependencies` block in `skill.yaml`:
  ```yaml
  dependencies:
    - id: translate-text
      version: ">=1.0.0"
    - id: summarize-document
      version: ">=1.0.0"
  ```
- [ ] On `aiskills install`, auto-install all dependencies recursively
- [ ] Detect circular dependencies and error out
- [ ] Version conflict resolution (semver range matching)
- [ ] Lock file: `skills.lock` to pin exact versions

---

### 6.4 — Chain Execution Engine

- [ ] Runtime engine that executes `chain` type skills
- [ ] Resolve and load all dependent skills
- [ ] Execute steps in sequence, passing outputs as inputs to next step
- [ ] Support `condition` field for conditional step execution:
  ```yaml
  condition: "{lang_result.language} != english"
  ```
- [ ] Support `output_as` for naming intermediate results
- [ ] Error handling: if any step fails, report which step and why
- [ ] Support parallel steps (future enhancement)

---

### 6.5 — Code Execution Sandbox

- [ ] Restricted Python execution environment for `code` type skills
- [ ] Block dangerous modules: `os`, `sys`, `subprocess`, `shutil`, `socket`, `http`, `urllib`
- [ ] Allow safe builtins: `len`, `range`, `str`, `int`, `float`, `list`, `dict`, `set`, `sorted`, `enumerate`, `zip`, `min`, `max`, `sum`, `re`
- [ ] Allow safe stdlib imports: `re`, `json`, `math`, `datetime`, `collections`, `itertools`, `functools`
- [ ] Memory limit (optional)
- [ ] Timeout limit (default 30 seconds)

---

## Phase 7 — Scale & Polish

### 7.1 — Registry Enhancements

- [ ] Verified author badges (linked GitHub account with certain criteria)
- [ ] Skill collections / curated packs (e.g., "NLP Essentials", "Data Extraction")
- [ ] Download count tracking and display
- [ ] Skill analytics dashboard for authors (views, downloads, install trends)
- [ ] "Star" or "favorite" skills (requires user accounts)

---

### 7.2 — Web-Based Skill Tester

- [ ] Browser-based interface to test a skill without the CLI
- [ ] Input form auto-generated from skill schema
- [ ] Run skill and display output in the browser
- [ ] Show latency and parsed output
- [ ] "Try it" button on every skill detail page

---

### 7.3 — Enterprise Features (Optional)

- [ ] Private registry (skills visible only within an org)
- [ ] Team management (invite members, role-based access)
- [ ] Self-hosted registry Docker image
- [ ] Private skill namespaces

---

### 7.4 — Ecosystem Integrations

- [ ] VS Code extension — validate and preview skills in-editor
- [ ] GitHub Action — validate skills in CI/CD
- [ ] API for third-party framework adapter plugins
- [ ] Webhook support (notify external services on skill publish)

---

### 7.5 — Database Migration (When Needed)

- [ ] Migrate from SQLite to PostgreSQL
- [ ] Write migration scripts
- [ ] Update API connection logic
- [ ] Load test to determine when migration is necessary

---

## Quick Reference — File Map

| File to Create / Modify | Phase | Purpose |
|--------------------------|-------|---------|
| `examples/*/skill.yaml` (10–15 new) | 2 | Fill out example library |
| `sdk/security.py` | 2 | Secret detection + code auditing |
| `docs/SECURITY.md` | 2 | Security model documentation |
| `docs/COMPARISON.md` | 2 | Competitive positioning |
| `docs/LAUNCH_POST.md` | 2 | Blog-style launch post |
| `CONTRIBUTING.md` | 2 | Contribution guide |
| `CODE_OF_CONDUCT.md` | 2 | Community standards |
| `sdk/cli.py` (update) | 3–4 | Add `publish`, `install`, `run`, `test`, `migrate` |
| `registry/api/` (new dir) | 3 | FastAPI backend |
| `registry/frontend/` (new dir) | 3 | Website |
| `.github/workflows/ci.yml` | 3 | GitHub Actions CI |
| `sdk/exporters/semantic_kernel.py` | 5 | New exporter |
| `sdk/exporters/openai.py` | 5 | New exporter |
| `sdk/exporters/anthropic.py` | 5 | New exporter |
| `sdk/exporters/haystack.py` | 5 | New exporter |
| `sdk/exporters/llamaindex.py` | 5 | New exporter |
| `sdk/runner.py` (new) | 4 | Skill execution engine |
| `sdk/sandbox.py` (new) | 6 | Code execution sandbox |
| `registry/api/benchmarks.py` (new) | 6 | Benchmark CI runner |
| `registry/api/decay.py` (new) | 6 | Skill decay monitor |

---

*Track progress by checking off items as you complete them.*  
*Update this file whenever new tasks are identified.*

---

## Session Update — 2026-03-26

- Completed the GitHub OAuth audit follow-up for the registry.
- Backend auth now verifies JWT signatures instead of matching token strings in the database.
- Frontend auth pages and provider wiring were added so browser login can round-trip and persist.
- CLI login now completes through the browser without manual token paste.
- Added the missing `registry/api/.env.example` for OAuth and JWT configuration.
