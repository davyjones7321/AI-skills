# ai-skills — Project Changelog & Analysis Log

> **📌 RULE:** Every development action on this project **must** be logged here with a timestamp. This includes:
> - Features created or updated
> - Files added, modified, moved, or deleted
> - Bug fixes and error handling additions
> - Configuration changes
> - Dependency changes
> - Refactors and structural changes
>
> **Format:** `[YYYY-MM-DD HH:MM IST]` — Description of change
>
> **No change goes undocumented.**

---

## Log

---

### 2026-03-05

#### `[2026-03-05 15:00 IST]` — `aiskills run` Command + GitHub Launch Prep

**Type:** Feature / Infrastructure / Documentation

**Phase 3.5 + Phase 4.1** — Two major additions:

1. **`aiskills run` command** — Local skill execution engine:
   - Created `sdk/runner.py` (~320 lines) supporting all 4 execution types
   - `code`: Sandboxed Python execution with blocked dangerous modules
   - `prompt`: Dry-run (shows formatted prompt) or live (calls OpenAI API via stdlib)
   - `tool_call`: Dry-run (shows resolved URL/params) or live (makes HTTP request)
   - `chain`: Displays planned execution flow (steps, dependencies, conditions)
   - Added `run` subcommand to `sdk/cli.py` with `--input`, `--input-file`, `--execute`, `--model` flags
   - Fixed Windows cp1252 encoding issues (replaced emoji with ASCII in output)

2. **GitHub repository setup** — All files for a professional open-source launch:
   - `.gitignore` (Python, Node, IDE, OS)
   - `.github/workflows/ci.yml` (validates all 19 skills + security audit on push/PR)
   - `.github/ISSUE_TEMPLATE/` (bug report, feature request, new skill proposal)
   - `.github/pull_request_template.md`
   - `assets/banner.png` (generated project logo)
   - Initialized git repository

3. **Documentation updates** — All MD files updated to reflect new run command:
   - `README.md`: Added run section, updated project structure
   - `OVERVIEW.md`: Updated CLI table (4 → 5 commands), added runner.py section, added run usage examples, updated project structure
   - `CONTRIBUTING.md`: Added run command step, fixed validate path typo, listed SDK files
   - `IMPROVEMENTS.md`: Marked sandboxed code execution as complete
   - `ACTION.md`: Marked Phase 3.5 and Phase 4.1 items as complete

**Files created:** `sdk/runner.py`, `.gitignore`, `.github/workflows/ci.yml`, `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/feature_request.md`, `.github/ISSUE_TEMPLATE/new_skill.md`, `.github/pull_request_template.md`, `assets/banner.png`

**Files modified:** `sdk/cli.py`, `README.md`, `OVERVIEW.md`, `CONTRIBUTING.md`, `IMPROVEMENTS.md`, `ACTION.md`, `analyze.md`

**Verification:** All 4 execution types tested — `code` (7ms, correct output), `prompt` (dry-run OK), `tool_call` (dry-run OK), `chain` (execution plan displayed).

---

### 2026-03-02

#### `[2026-03-02 15:15 IST]` — Timeline & Architecture Updates

**Type:** Documentation

Updated `OVERVIEW.md` to reflect realistic timeline adjustments and simplified MVP architecture choices (SQLite, static frontend, synchronous benchmarks) as recommended in `IMPROVEMENTS.md`. Checked off corresponding items in `ACTION.md`.

**Files modified:** `OVERVIEW.md`, `ACTION.md`, `IMPROVEMENTS.md`

---

### 2026-03-01

#### `[2026-03-01 19:30 IST]` — Spec, Security, and Docs Additions

**Type:** Feature / Documentation / Security

**Phase 2 — Finalizing Pre-Launch Prep**
- Implemented **Spec Enhancements**:
  - Added optional `spec_version` field to track spec updates.
  - Added `max_length` constraint for string inputs.
  - Added "Spec Versioning Rules" section to `docs/SPEC.md`.
- Built the **Security Layer**:
  - Created `sdk/security.py` to statically scan for hardcoded secrets (API keys) and dangerous Python built-ins/modules.
  - Added the `aiskills validate --audit` CLI command to run these checks locally.
  - Wrote `docs/SECURITY.md` detailing the threat model and safety principles.
- Created all final **Launch Documentation**:
  - `CONTRIBUTING.md`
  - `CODE_OF_CONDUCT.md`
  - `docs/COMPARISON.md` (Contrasting with LangChain tools, MCP, OpenAPI)
  - `docs/LAUNCH_POST.md`
- Integrated everything into the main `README.md`.

**Files created:** `sdk/security.py`, `docs/SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `docs/COMPARISON.md`, `docs/LAUNCH_POST.md`
**Files modified:** `docs/SPEC.md`, `sdk/cli.py`, `README.md`

**Verification:** All new CLI commands and documentation links verified. Security scanner tested against example skills.

---

#### `[2026-03-01 18:00 IST]` — 14 New Example Skills Created

**Type:** Feature / Content

Created 14 new `skill.yaml` example files covering all 4 execution types. This fills the critical gap of having zero `code` and `chain` type examples.

| Skill | Execution Type | Description |
|-------|---------------|-------------|
| `extract-email-data` | prompt | Extract sender, subject, action items, dates, urgency from emails |
| `generate-commit-message` | prompt | Generate conventional commit messages from git diffs |
| `code-review` | prompt | Review code for bugs, security, performance, style |
| `detect-language` | prompt | Detect text language with ISO code and confidence |
| `generate-sql` | prompt | Generate SQL from natural language with safety flags |
| `summarize-to-tweet` | prompt | Condense text to 280-character tweets |
| `spell-check` | tool_call | Check spelling via LanguageTool API |
| `weather-lookup` | tool_call | Get weather data from OpenWeatherMap API |
| `word-frequency` | code | Count word frequencies with stop word filtering |
| `markdown-to-html` | code | Full MD→HTML converter (headers, lists, links, code blocks) |
| `json-to-csv` | code | Convert JSON arrays to CSV with nested object flattening |
| `calculate-reading-time` | code | Estimate reading time + word/sentence/paragraph stats |
| `translate-and-summarize` | chain | detect-language → translate-text → summarize-document |
| `review-and-fix-code` | chain | code-review → code-fixer chain |

**Files created:** 14 new `examples/*/skill.yaml` files

**Files modified:** `registry/index.json` (5 → 19 skills), `ACTION.md`, `IMPROVEMENTS.md`, `analyze.md`, `OVERVIEW.md`

**Verification:** All 14 skills pass `aiskills validate`. Fixed `detect-language` encoding issue (replaced Japanese test case with German for Windows cp1252 compatibility).

---

### 2026-02-19

#### `[2026-02-19 01:39 IST]` — Pre-Backend Code Audit & Bug Fixes (8 bugs)

**Type:** Bug Fix / Error Handling

Full code audit of all SDK files before backend development. Found and fixed 8 bugs:

| # | File | Bug | Fix |
|---|------|-----|-----|
| 1 | All exporters + `cli.py` | `UnicodeEncodeError` on Windows — `Path.write_text()` defaulted to `cp1252` | Added `encoding="utf-8"` to all `write_text()` calls |
| 2 | `pyproject.toml` | Wrong `build-backend` value — `setuptools.backends.legacy:build` doesn't exist | Changed to `setuptools.build_meta` |
| 3 | `sdk/cli.py` | Init template used `{input_text}` causing `KeyError` during Python `.format()` | Switched to `__PLACEHOLDER__` + `.replace()` pattern |
| 4 | `sdk/cli.py` | Fragile `from validator import validate_skill` broke when run from other directories | Replaced with `importlib.util.spec_from_file_location()` |
| 5 | All 3 exporters | `tool_call` export ignored headers, params, and auth from YAML | Rewrote `_build_tool_call_body` to parse and generate headers/params/env refs |
| 6 | `sdk/exporters/autogen.py` + `crewai.py` | `_build_code_body` generated broken indentation and invalid `locals()` capture | Rewrote to properly indent each line of the code block |
| 7 | `pyproject.toml` | Listed `click>=8.1` as dependency but CLI uses `argparse` | Removed unused dependency |
| 8 | `sdk/exporters/langchain.py` | `_to_python_type` mapped `"any"` to `"any"` (invalid Python type) | Changed to `"Any"` (from `typing`) |

**Files modified:** `sdk/cli.py`, `sdk/exporters/langchain.py`, `sdk/exporters/autogen.py`, `sdk/exporters/crewai.py`, `pyproject.toml`

**Verification:** All 5 example skills pass validation. All CLI commands (`init`, `validate`, `export`, `info`) tested and working.

---

#### `[2026-02-19 01:10 IST]` — Project Folder Structure Created

**Type:** Structural / Reorganization

All files were reorganized from a flat root directory into the proper project structure defined in `OVERVIEW.md`.

**Directories created:**
- `docs/`
- `sdk/`
- `sdk/exporters/`
- `examples/summarize-document/`
- `examples/extract-invoice/`
- `examples/classify-sentiment/`
- `examples/translate-text/`
- `examples/web-search/`
- `registry/`

**Files moved:**

| From (old location) | To (new location) |
|---|---|
| `SPEC.md` | `docs/SPEC.md` |
| `cli.py` | `sdk/cli.py` |
| `validator.py` | `sdk/validator.py` |
| `langchain.py` | `sdk/exporters/langchain.py` |
| `autogen.py` | `sdk/exporters/autogen.py` |
| `crewai.py` | `sdk/exporters/crewai.py` |
| `skill.yaml` | `examples/summarize-document/skill.yaml` |
| `skill (1).yaml` | `examples/extract-invoice/skill.yaml` |
| `skill (2).yaml` | `examples/classify-sentiment/skill.yaml` |
| `skill (3).yaml` | `examples/translate-text/skill.yaml` |
| `skill (4).yaml` | `examples/web-search/skill.yaml` |
| `index.json` | `registry/index.json` |
| `README.2.md` | `registry/README.md` |

**Files created:**
- `sdk/__init__.py` — Python package init for SDK module
- `sdk/exporters/__init__.py` — Python package init for exporters submodule

---

#### `[2026-02-19 00:57 IST]` — `ACTION.md` Created

**Type:** Documentation

Master action plan created with all tasks organized into 7 phases covering the full project lifecycle — from pre-launch prep through scale & polish.

---

#### `[2026-02-19 00:41 IST]` — `IMPROVEMENTS.md` Created

**Type:** Documentation

Comprehensive solutions document created addressing 7 improvement areas identified from the OVERVIEW.md analysis: competitive positioning, adoption strategy, security, missing examples, spec versioning, timeline adjustments, and error handling.

---

#### `[2026-02-19 01:15 IST]` — `analyze.md` Created

**Type:** Documentation / Process

This changelog file created to track all project changes with timestamps. Rule established that every development action must be logged here.

---

### Pre-existing (Phase 1 — Foundation)

These items were built before this changelog was created. Recorded here for completeness.

| Item | Status | File(s) |
|------|--------|---------|
| v0.1 Specification | ✅ Complete | `docs/SPEC.md` |
| Skill Validator | ✅ Complete | `sdk/validator.py` |
| CLI (init, validate, export, info) | ✅ Complete | `sdk/cli.py` |
| LangChain Exporter | ✅ Complete | `sdk/exporters/langchain.py` |
| AutoGen Exporter | ✅ Complete | `sdk/exporters/autogen.py` |
| CrewAI Exporter | ✅ Complete | `sdk/exporters/crewai.py` |
| Example: summarize-document | ✅ Complete | `examples/summarize-document/skill.yaml` |
| Example: extract-invoice | ✅ Complete | `examples/extract-invoice/skill.yaml` |
| Example: classify-sentiment | ✅ Complete | `examples/classify-sentiment/skill.yaml` |
| Example: translate-text | ✅ Complete | `examples/translate-text/skill.yaml` |
| Example: web-search | ✅ Complete | `examples/web-search/skill.yaml` |
| Registry Index Prototype | ✅ Complete | `registry/index.json` |
| Registry Documentation | ✅ Complete | `registry/README.md` |
| Package Configuration | ✅ Complete | `pyproject.toml` |
| Project README | ✅ Complete | `README.md` |
| Project Overview | ✅ Complete | `OVERVIEW.md` |

---

*New entries should be added at the top of the current date section, with the latest change first.*
