<p align="center">
  <img src="assets/banner.png" alt="ai-skills banner" width="600" />
</p>

# 🧠 ai-skills

> The universal open standard for AI agent skills — write once, run anywhere.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Spec Version](https://img.shields.io/badge/spec-v0.1-blue)](./docs/SPEC.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)

---

## The Problem

AI agent frameworks are exploding — LangChain, AutoGen, CrewAI, Semantic Kernel, and dozens more. But skills (tools, functions, actions) built for one framework **don't work in another**. Every developer rewrites the same skills over and over, just in different formats.

This is the same problem the web solved with HTML. We need a common language for AI skills.

## The Solution

**ai-skills** is an open specification + SDK that lets you:

1. **Write** a skill once in a simple `skill.yaml` file
2. **Publish** it to the public registry
3. **Export** it to any framework automatically

```
skill.yaml  →  LangChain tool
            →  AutoGen skill  
            →  CrewAI tool
            →  Semantic Kernel function
            →  Raw API call
```

### How This Compares
Wondering how this compares to **LangChain Tools**, **OpenAPI**, **MCP**, or **SKILL.md**? 
Read our detailed breakdown: **[How ai-skills Compares](./docs/COMPARISON.md)**.

---

## Quick Start

### Install the CLI

```bash
pip install ai-skills-sdk
```

### Create your first skill

```bash
aiskills init my-skill
cd my-skill
```

This creates a `skill.yaml`:

```yaml
skill:
  id: my-skill
  version: 1.0.0
  name: My Skill
  description: What this skill does
  inputs:
    - name: input_text
      type: string
      required: true
  outputs:
    - name: result
      type: string
  execution:
    type: prompt
    prompt_template: "Do something with: {input_text}"
```

### Validate and audit

```bash
# Check against the v0.1 schema specification
aiskills validate skill.yaml

# Run static security analysis (catch secrets & dangerous imports)
aiskills validate --audit skill.yaml
```

### Export to your framework

```bash
aiskills export --target langchain    # → langchain_tool.py
aiskills export --target autogen      # → autogen_skill.py
aiskills export --target crewai       # → crewai_tool.py
```

### Run a skill locally

```bash
# Dry-run: shows formatted prompt without calling any API
aiskills run skill.yaml --input '{"text": "hello"}'

# Run a code-type skill (no API key needed)
aiskills run examples/word-frequency/skill.yaml --input-file input.json

# Live execution: actually calls the LLM (requires OPENAI_API_KEY)
aiskills run skill.yaml --input-file input.json --execute
```

### Publish to the registry

```bash
# Authenticate with your token
aiskills login --token "my-token" --username "my-username"

# Publish your skill to the registry
aiskills publish skill.yaml
```

### Install a skill

```bash
# Download a published skill to your local workspace
aiskills install ai-skills-team/summarize-document

# Download and immediately auto-export it to LangChain!
aiskills install ai-skills-team/summarize-document --export langchain
```

---

## Project Structure

```
ai-skills/
├── README.md               ← You are here
├── CONTRIBUTING.md         ← Contribution guidelines
├── CODE_OF_CONDUCT.md      ← Community standards
├── .github/
│   ├── workflows/ci.yml    ← CI: validate all skills on push/PR
│   ├── ISSUE_TEMPLATE/     ← Bug, feature, new skill templates
│   └── pull_request_template.md
├── docs/
│   ├── SPEC.md             ← The official v0.1 specification
│   ├── SECURITY.md         ← Security model and audit tools
│   └── COMPARISON.md       ← How we compare to MCP/LangChain/etc
├── examples/               ← 19 complete, working example skills (prompt, code, tool_call, chain)
│   ├── summarize-document/
│   ├── generate-sql/ 
│   ├── markdown-to-html/
│   └── ... (16 more)
├── sdk/
│   ├── cli.py              ← Main CLI entry point
│   ├── validator.py        ← Schema validation
│   ├── security.py         ← Security auditing
│   ├── runner.py           ← Skill execution engine (run command)
│   ├── auth_config.py      ← Authentication management
│   └── exporters/          ← Framework adapters
└── registry/
    ├── api/                ← FastAPI Registry Backend Server
    └── index.json          ← Prototype registry index
```

---

## Skill Types

| Type | Description | Example |
|------|-------------|---------|
| `prompt` | LLM prompt template | Summarize, classify, translate |
| `tool_call` | External API/function call | Web search, database query |
| `chain` | Multiple steps in sequence | Research → summarize → format |
| `code` | Execute a code snippet | Data processing, calculations |

---

## Why ai-skills?

| | ai-skills | LangChain | AutoGen | Semantic Kernel |
|--|-----------|-----------|---------|-----------------|
| Framework-agnostic | ✅ | ❌ | ❌ | ❌ |
| Open standard | ✅ | ❌ | ❌ | ❌ |
| Public registry | ✅ | ❌ | ❌ | ❌ |
| Built-in benchmarks | ✅ | ❌ | ❌ | ❌ |
| Skill portability | ✅ | ❌ | ❌ | ❌ |

---

## Contributing

We're in early days — contributions, feedback, and ideas are very welcome.

- 📖 Read the [Specification](./docs/SPEC.md)
- 🛠️ Check out [example skills](./examples/)
- 💬 Open an issue to discuss ideas
- 🔁 Submit a PR

---

## License

MIT — free to use, modify, and distribute.
