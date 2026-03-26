# ai-skills — Improvement Solutions & Action Plan

> Based on the analysis of OVERVIEW.md  
> Goal: Build and ship a complete, polished open-source project

---

## Table of Contents

1. [Competitive Positioning](#1-competitive-positioning)
2. [Adoption & Launch Strategy](#2-adoption--launch-strategy)
3. [Security & Safety](#3-security--safety)
4. [Missing Example Skills (Chain & Code)](#4-missing-example-skills-chain--code)
5. [Spec Versioning & Migration Strategy](#5-spec-versioning--migration-strategy)
6. [Realistic Timeline Adjustments](#6-realistic-timeline-adjustments)
7. [Error Handling & Edge Cases](#7-error-handling--edge-cases)

---

## 1. Competitive Positioning

### The Problem

The OVERVIEW says "nobody has built this" — but readers (especially developers) will immediately think of existing tools. You need to acknowledge them and explain why ai-skills is different.

### What to Add

Create a section in OVERVIEW.md or a standalone `docs/COMPARISON.md` with this table:

| Existing Tool | What It Does | How ai-skills Is Different |
|---------------|-------------|---------------------------|
| **OpenAI function-calling** | Defines tools as JSON schemas for GPT models | Locked to OpenAI's API. Not portable to other frameworks. ai-skills exports to *any* framework, not just OpenAI. |
| **Anthropic MCP (Model Context Protocol)** | Standardizes how AI models connect to external data/tools | MCP is about *connecting* models to data sources. ai-skills is about *defining and sharing* reusable skill logic. They solve different layers — MCP = transport, ai-skills = skill definition. Could be complementary. |
| **Hugging Face Hub** | Hosts models, datasets, and Spaces | Focused on models and datasets, not reusable agent skill definitions. No concept of exporting a skill to framework-native code. |
| **LangChain Hub** | Shares prompts and chains within LangChain | LangChain-only. Skills shared here don't work in AutoGen or CrewAI. ai-skills is framework-agnostic. |
| **CrewAI Tools** | Built-in and community tools for CrewAI agents | CrewAI-only. Same lock-in problem. |

### Key Talking Point

> "ai-skills is not a framework — it's a **translation layer** that sits between frameworks. It doesn't compete with LangChain, MCP, or Hugging Face. It makes them all interoperable."

### Action Items

- [ ] Add a "How This Compares" section to `README.md` (brief, 5–10 lines)
- [ ] Create `docs/COMPARISON.md` with the detailed table above
- [ ] Keep the tone respectful — position as complementary, not adversarial

---

## 2. Adoption & Launch Strategy

### The Problem

Right now the plan is "post on HackerNews and Reddit." That's a start, but without a concrete plan, the launch will fizzle.

### Step-by-Step Launch Plan

#### Pre-Launch (Before Going Public)

1. **Seed the registry with 15–20 quality skills**, not just 5  
   Ideas for additional skills to build yourself:

   | Skill | Execution Type | Usefulness |
   |-------|---------------|------------|
   | `extract-email-data` | prompt | Pull name, subject, action items from email |
   | `generate-commit-message` | prompt | Generate conventional commit messages from diffs |
   | `code-review` | prompt | Review a code snippet for bugs and improvements |
   | `json-to-csv` | code | Convert JSON data to CSV format |
   | `pdf-page-count` | code | Count pages in a PDF file |
   | `resize-image` | code | Resize an image to given dimensions |
   | `detect-language` | prompt | Detect the language of input text |
   | `generate-sql` | prompt | Generate SQL queries from natural language |
   | `spell-check` | tool_call | Check spelling via an API |
   | `weather-lookup` | tool_call | Get weather data for a location |
   | `summarize-to-tweet` | chain | Summarize → then compress to 280 chars |
   | `translate-and-summarize` | chain | Detect language → translate → summarize |
   | `word-frequency` | code | Count word frequencies in text |
   | `markdown-to-html` | code | Convert markdown to HTML |
   | `calculate-reading-time` | code | Estimate reading time for text |

   This also solves the **missing `chain` and `code` examples** problem (see section 4).

2. **Write a blog-style launch post** (`docs/LAUNCH_POST.md`)  
   Structure:
   - Hook: "I built X skills for my AI agents. When I switched from LangChain to AutoGen, I had to rewrite all of them."
   - The 30-second pitch
   - One animated GIF showing the export workflow in a terminal
   - Link to the repo

3. **Create a 2-minute demo video** (or animated GIF)  
   Show the complete flow:
   ```
   aiskills init my-skill → edit skill.yaml → validate → export --target langchain → export --target autogen
   ```

4. **Write a good `CONTRIBUTING.md`**  
   Make it dead simple for someone to:
   - Add a new example skill (just copy a folder, edit YAML)
   - Add a new exporter (follow the existing pattern)
   - Report issues

#### Launch Day

Post to these specific communities in this order:

| Platform | Subreddit / Channel | Why |
|----------|-------------------|-----|
| **Reddit** | r/MachineLearning | Largest ML community, appreciates open-source tools |
| **Reddit** | r/LangChain | Directly relevant — these users feel the pain |
| **Reddit** | r/LocalLLaMA | Active community, loves open-source tooling |
| **HackerNews** | Show HN | Best for technical launches, high-quality feedback |
| **Discord** | LangChain Discord | Active dev community |
| **Discord** | AutoGen Discord | Target users who need interop |
| **Twitter/X** | Post + tag AI thought leaders | Amplification |

#### Post-Launch

- Respond to every GitHub issue within 24 hours (for the first month)
- Accept any PR that adds a new example skill (easy wins for contributors)
- Post weekly updates on what was built (keeps momentum)

### Action Items

- [x] Build 10–15 additional example skills before launch (14 created)
- [x] Write `docs/LAUNCH_POST.md`
- [ ] Record a terminal demo GIF using [asciinema](https://asciinema.org/) or [VHS](https://github.com/charmbracelet/vhs)
- [x] Write `CONTRIBUTING.md` with clear contribution guides

---

## 3. Security & Safety

### The Problem

The `code` execution type runs arbitrary Python. The `tool_call` type hits external APIs. Without any safety measures, a malicious skill in the registry could do damage.

### Solutions

#### 3.1 — Sandbox the `code` Execution Type

When `aiskills run` executes a `code` type skill, use **restricted execution**:

```python
# sdk/runner.py — safe execution approach

import ast
import RestrictedPython  # pip install RestrictedPython

BLOCKED_MODULES = [
    'os', 'sys', 'subprocess', 'shutil', 'socket',
    'http', 'urllib', 'requests', 'pathlib',
    '__import__', 'eval', 'exec', 'compile'
]

def run_code_skill(code_string: str, inputs: dict) -> dict:
    """
    Run a code-type skill in a restricted environment.
    No filesystem access, no network access, no imports of dangerous modules.
    """
    # Step 1: Static analysis — scan for dangerous imports
    tree = ast.parse(code_string)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split('.')[0] in BLOCKED_MODULES:
                    raise SecurityError(f"Blocked import: {alias.name}")
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split('.')[0] in BLOCKED_MODULES:
                raise SecurityError(f"Blocked import: {node.module}")

    # Step 2: Execute in restricted globals
    restricted_globals = {
        '__builtins__': {
            'len': len, 'range': range, 'str': str, 'int': int,
            'float': float, 'list': list, 'dict': dict, 'set': set,
            'sorted': sorted, 'enumerate': enumerate, 'zip': zip,
            'min': min, 'max': max, 'sum': sum, 'abs': abs,
            'round': round, 'isinstance': isinstance, 'type': type,
            'True': True, 'False': False, 'None': None,
            'print': lambda *a, **k: None,  # no-op print
        }
    }

    exec(compile(code_string, '<skill>', 'exec'), restricted_globals)
    run_fn = restricted_globals.get('run')
    if not run_fn:
        raise ValueError("Code skill must define a 'run(inputs)' function")

    return run_fn(inputs)
```

#### 3.2 — Credential Management

For `tool_call` skills that need API keys, use a `.env`-based approach:

```yaml
# In skill.yaml — reference env vars, never hardcode secrets
execution:
  type: tool_call
  endpoint:
    url: https://api.example.com/search
    headers:
      Authorization: "Bearer {env.SEARCH_API_KEY}"
```

The SDK should:
1. Load from `.env` file or system environment variables
2. **Never** allow secrets to be stored in `skill.yaml` itself
3. Warn if a skill.yaml contains anything that looks like a hardcoded key

```python
# sdk/security.py — secret detection

import re

SECRET_PATTERNS = [
    r'sk-[a-zA-Z0-9]{20,}',          # OpenAI keys
    r'key-[a-zA-Z0-9]{20,}',         # Generic API keys
    r'ghp_[a-zA-Z0-9]{36}',          # GitHub tokens
    r'Bearer\s+[a-zA-Z0-9._-]{20,}', # Raw bearer tokens
]

def check_for_hardcoded_secrets(yaml_content: str) -> list[str]:
    warnings = []
    for pattern in SECRET_PATTERNS:
        matches = re.findall(pattern, yaml_content)
        for match in matches:
            warnings.append(
                f"Possible hardcoded secret detected: {match[:8]}... "
                f"Use {{env.VAR_NAME}} instead."
            )
    return warnings
```

#### 3.3 — Registry Safety for Published Skills

Since you're self-funding and running the registry yourself, keep it simple:

1. **All published skills are public and source-visible** — anyone can read the `skill.yaml` before installing
2. **Add a `aiskills audit <skill.yaml>` command** that scans for:
   - Dangerous imports in `code` type skills
   - Hardcoded secrets
   - Suspicious URLs in `tool_call` endpoints
3. **Add a flag on the registry**: `"reviewed": true/false` — you manually review skills before marking them as reviewed
4. **Show a warning when installing unreviewed skills**:
   ```
   ⚠️ This skill has not been reviewed. Inspect the skill.yaml before using.
   ```

### Action Items

- [x] Add sandboxing logic to the `aiskills run` implementation
- [x] Create `sdk/security.py` with secret detection
- [x] Add a `--audit` flag to the validator that checks for security issues
- [ ] Add a `reviewed` field to the registry schema
- [x] Document the security model in `docs/SECURITY.md`

---

## 4. Missing Example Skills (Chain & Code)

### The Problem

All 5 examples are `prompt` or `tool_call`. The `chain` and `code` execution types have zero working examples, which makes them feel unvalidated.

### Solution: Build These Examples

#### Code Example — `word-frequency`

```yaml
# examples/word-frequency/skill.yaml
skill:
  id: word-frequency
  version: 1.0.0
  name: Word Frequency Counter
  description: |
    Counts the frequency of each word in a text document.
    Returns a sorted list of words with their counts.
  author: ai-skills-team
  license: MIT
  tags: [text, analysis, utility]

  inputs:
    - name: text
      type: string
      description: The text to analyze
      required: true
    - name: top_n
      type: integer
      description: Number of top words to return
      required: false
      default: 10

  outputs:
    - name: frequencies
      type: array
      description: List of {word, count} objects sorted by count descending
    - name: total_words
      type: integer
      description: Total number of words in the text

  execution:
    type: code
    language: python
    code: |
      def run(inputs):
          import re
          text = inputs["text"].lower()
          words = re.findall(r'\b[a-z]+\b', text)
          freq = {}
          for word in words:
              freq[word] = freq.get(word, 0) + 1
          sorted_freq = sorted(freq.items(), key=lambda x: -x[1])
          top_n = inputs.get("top_n", 10)
          return {
              "frequencies": [
                  {"word": w, "count": c} for w, c in sorted_freq[:top_n]
              ],
              "total_words": len(words)
          }

  benchmarks:
    test_cases:
      - id: basic-count
        input:
          text: "the cat sat on the mat the cat"
          top_n: 3
        expected:
          total_words: 8
```

#### Code Example — `markdown-to-html`

```yaml
# examples/markdown-to-html/skill.yaml
skill:
  id: markdown-to-html
  version: 1.0.0
  name: Markdown to HTML Converter
  description: Converts basic markdown text to HTML.
  author: ai-skills-team
  license: MIT
  tags: [markdown, html, converter, utility]

  inputs:
    - name: markdown
      type: string
      description: The markdown text to convert
      required: true

  outputs:
    - name: html
      type: string
      description: The converted HTML string

  execution:
    type: code
    language: python
    code: |
      def run(inputs):
          import re
          md = inputs["markdown"]
          # Headers
          md = re.sub(r'^### (.+)$', r'<h3>\1</h3>', md, flags=re.MULTILINE)
          md = re.sub(r'^## (.+)$', r'<h2>\1</h2>', md, flags=re.MULTILINE)
          md = re.sub(r'^# (.+)$', r'<h1>\1</h1>', md, flags=re.MULTILINE)
          # Bold and italic
          md = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', md)
          md = re.sub(r'\*(.+?)\*', r'<em>\1</em>', md)
          # Line breaks
          md = re.sub(r'\n\n', '</p><p>', md)
          return {"html": f"<p>{md}</p>"}

  benchmarks:
    test_cases:
      - id: headers
        input:
          markdown: "# Hello World"
        expected:
          html: "<p><h1>Hello World</h1></p>"
```

#### Chain Example — `translate-and-summarize`

```yaml
# examples/translate-and-summarize/skill.yaml
skill:
  id: translate-and-summarize
  version: 1.0.0
  name: Translate and Summarize
  description: |
    Detects the language of input text, translates it to English
    if needed, then summarizes it into key points.
  author: ai-skills-team
  license: MIT
  tags: [translation, summarization, chain, multilingual]

  inputs:
    - name: text
      type: string
      description: The text to translate and summarize
      required: true
    - name: max_points
      type: integer
      description: Maximum number of key points to extract
      required: false
      default: 5

  outputs:
    - name: original_language
      type: string
      description: Detected language of the input
    - name: summary
      type: string
      description: Summarized text in English
    - name: key_points
      type: array
      description: List of key points extracted from the text

  execution:
    type: chain
    steps:
      - skill: translate-text
        input_map:
          text: "{text}"
          target_language: "english"
        output_as: translation_result

      - skill: summarize-document
        input_map:
          document: "{translation_result.translated_text}"
          max_points: "{max_points}"
        output_as: summary_result

  dependencies:
    - id: translate-text
      version: ">=1.0.0"
    - id: summarize-document
      version: ">=1.0.0"

  benchmarks:
    test_cases:
      - id: english-input
        input:
          text: "Artificial intelligence is transforming industries worldwide. Companies are adopting AI to improve efficiency, reduce costs, and create new products."
          max_points: 3
        expected:
          original_language: english
```

### Action Items

- [x] Create `examples/word-frequency/skill.yaml`
- [x] Create `examples/markdown-to-html/skill.yaml`
- [x] Create `examples/translate-and-summarize/skill.yaml`
- [x] Validate all new examples pass `aiskills validate`
- [x] Update `registry/index.json` to include the new skills

---

## 5. Spec Versioning & Migration Strategy

### The Problem

The spec is at v0.1. What happens when v1.0 comes out? Will everyone's skills break?

### Solution: Version Header + Migration Tool

#### 5.1 — Add a `spec_version` field to `skill.yaml`

```yaml
skill:
  spec_version: "0.1"    # ← which version of the spec this skill follows
  id: my-skill
  version: 1.0.0
  # ...
```

This lets the validator know which rules to apply.

#### 5.2 — Define Compatibility Rules

Add to `docs/SPEC.md`:

```markdown
## Spec Versioning Rules

- **Patch updates** (0.1.0 → 0.1.1): Bug fixes in the spec. No breaking changes.
  All existing skills remain valid.

- **Minor updates** (0.1 → 0.2): New optional fields may be added.
  All existing skills remain valid. New features require the new spec version.

- **Major updates** (0.x → 1.0): Breaking changes possible.
  A migration guide and migration CLI command will be provided.
```

#### 5.3 — Build a `aiskills migrate` command (for future major versions)

```bash
aiskills migrate skill.yaml --to 1.0
# → Reads skill.yaml (spec v0.1)
# → Applies known transformations
# → Writes updated skill.yaml (spec v1.0)
# → Reports what changed
```

This doesn't need to be built now — just document the plan so early adopters know their skills won't be abandoned.

### Action Items

- [x] Add `spec_version` as an optional field in the current spec
- [x] Add a "Spec Versioning Rules" section to `docs/SPEC.md`
- [ ] Add `aiskills migrate` to the roadmap (Phase 4 or 5)

---

## 6. Realistic Timeline Adjustments

### The Problem

Some estimates in the OVERVIEW are tight for a solo developer.

### Adjusted Estimates

| Task | Original Estimate | Adjusted Estimate | Notes |
|------|------------------|-------------------|-------|
| Registry Backend API | 1–2 weeks | 2–3 weeks | Auth alone can take a week. Use SQLite first instead of PostgreSQL to simplify. |
| Registry Frontend | 2–3 weeks | 3–4 weeks | Build a minimal version first: homepage + skill detail page only. Add search later. |
| Benchmark CI Runner | 1–2 weeks | 2–3 weeks | Redis adds complexity. Start with a simple in-process runner, add Redis later. |
| `aiskills publish` | 2–3 days | 3–5 days | Depends on auth being done first. |
| `aiskills run` | 3–5 days | 1–2 weeks | Handling different LLM providers is more work than expected. |

### Simplification Suggestions

1. **Use SQLite instead of PostgreSQL** for the first version of the registry. You can migrate to PostgreSQL later when (if) scale demands it. This eliminates database setup and hosting complexity.

2. **Skip Redis** for the benchmark runner initially. Just run benchmarks synchronously when a skill is published. Add async job processing later.

3. **Use GitHub Pages** for the frontend initially instead of Next.js + Vercel. A static site with client-side search (using something like [Pagefind](https://pagefind.app/) or [Fuse.js](https://www.fusejs.io/)) is much faster to build and costs $0.

4. **Use GitHub OAuth via simple personal access tokens** first. Full OAuth flow can come later.

### Action Items

- [x] Update the OVERVIEW.md timeline estimates
- [x] Start with SQLite, not PostgreSQL
- [x] Start with a static frontend, not Next.js
- [x] Skip Redis — run benchmarks synchronously first

---

## 7. Error Handling & Edge Cases

### The Problem

No discussion of what happens when things go wrong.

### Solutions to Implement

#### 7.1 — LLM Output Parsing Failures

When `output_parser: json` is set but the LLM returns invalid JSON:

```python
# sdk/runner.py — robust output parsing

import json
import re

def parse_llm_output(raw_output: str, parser_type: str) -> dict:
    if parser_type == "none":
        return {"raw_output": raw_output}

    if parser_type == "json":
        # Attempt 1: Direct parse
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            pass

        # Attempt 2: Extract JSON from markdown code block
        match = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw_output)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Attempt 3: Find first { ... } or [ ... ] block
        match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', raw_output)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # All attempts failed
        raise OutputParseError(
            f"LLM returned invalid JSON. Raw output:\n{raw_output[:500]}"
        )
```

#### 7.2 — Rate Limiting on Registry API

```python
# registry/api.py — simple rate limiting with slowapi

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/skills")
@limiter.limit("60/minute")       # 60 requests per minute for reads
async def list_skills():
    ...

@app.post("/skills")
@limiter.limit("10/minute")       # 10 publishes per minute
async def publish_skill():
    ...
```

#### 7.3 — Token Limit Handling for `prompt` Skills

Add an optional `max_input_length` field to the spec:

```yaml
inputs:
  - name: document
    type: string
    description: The document to summarize
    required: true
    max_length: 50000    # Characters — SDK warns if input exceeds this
```

The SDK should:
1. Check input length before sending to LLM
2. Warn (not error) if close to the limit
3. Error if drastically over the limit
4. Document recommended `max_length` values for common models

#### 7.4 — Network Failure Handling for `tool_call` Skills

```python
# sdk/runner.py — retry logic for API calls

import time

def call_endpoint(url, method, headers, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"⏳ Timeout. Retrying in {wait}s... ({attempt + 1}/{max_retries})")
                time.sleep(wait)
            else:
                raise SkillExecutionError(f"Endpoint timed out after {max_retries} attempts: {url}")
        except requests.exceptions.ConnectionError:
            raise SkillExecutionError(f"Cannot connect to endpoint: {url}")
        except requests.exceptions.HTTPError as e:
            raise SkillExecutionError(f"Endpoint returned error {e.response.status_code}: {e.response.text[:200]}")
```

### Action Items

- [ ] Implement JSON output parser with fallback strategies
- [ ] Add rate limiting when building the registry API
- [ ] Add `max_length` as an optional input field in the spec
- [ ] Add retry logic with exponential backoff for `tool_call` execution
- [ ] Document error handling behavior in `docs/SPEC.md`

---

## Summary — Full Action Items Checklist

### Do Before Launch

- [x] Add competitive comparison section to `README.md`
- [x] Create `docs/COMPARISON.md`
- [x] Build 10–15 additional example skills (including `chain` and `code` types)
- [x] Create `docs/SECURITY.md` with security model
- [x] Add `spec_version` field to the spec
- [x] Write `CONTRIBUTING.md`
- [ ] Record terminal demo GIF
- [x] Write `docs/LAUNCH_POST.md`
- [x] Create `sdk/security.py` (secret detection + code auditing)
- [x] Add `--audit` flag to the validator

### Do During Build Phase

- [x] Implement sandboxed `code` execution in `aiskills run`
- [ ] Implement JSON output parser with fallbacks
- [ ] Add retry logic for `tool_call` execution
- [x] Use SQLite instead of PostgreSQL for MVP registry
- [ ] Build static frontend instead of Next.js for MVP
- [ ] Add rate limiting to registry API

### Do Post-Launch

- [ ] Add `aiskills migrate` command when spec changes
- [ ] Upgrade to PostgreSQL when needed
- [ ] Add Redis for async benchmark jobs when needed
- [ ] Build full Next.js frontend when traffic justifies it

---

*This document is a companion to OVERVIEW.md. Update it as items are completed.*

---

## Session Update — 2026-03-26

One of the highest-priority improvement tracks is now closed: registry authentication moved from the old token-matching approach to a proper GitHub OAuth plus JWT flow. The backend now verifies JWTs correctly, the frontend has the missing auth surfaces, and the CLI login loop no longer depends on manual token paste. Follow-on improvements should target auth-adjacent polish rather than basic auth correctness.
