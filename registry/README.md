# ai-skills Registry

The public registry for ai-skills compatible skills.

## Browse Skills

| Skill | Author | Type | Avg Latency | Avg Cost |
|-------|--------|------|-------------|----------|
| [summarize-document](./index.json) | ai-skills-team | prompt | 1100ms | $0.003 |
| [extract-invoice](./index.json) | ai-skills-team | prompt | 900ms | $0.002 |
| [classify-sentiment](./index.json) | ai-skills-team | prompt | 600ms | $0.001 |
| [translate-text](./index.json) | ai-skills-team | prompt | 800ms | $0.002 |
| [web-search](./index.json) | ai-skills-team | tool_call | 400ms | $0.005 |

---

## Install a Skill

```bash
# Install latest version
aiskills install ai-skills-team/summarize-document

# Install specific version
aiskills install ai-skills-team/summarize-document@1.0.0
```

This downloads the `skill.yaml` to your local skills directory.

---

## Publish a Skill

### 1. Create and validate your skill

```bash
aiskills init my-skill
cd my-skill
# edit skill.yaml ...
aiskills validate skill.yaml
```

### 2. Run tests

```bash
aiskills test skill.yaml
```

All test cases in your `benchmarks.test_cases` block must pass.

### 3. Publish

```bash
aiskills publish
```

This will:
- Re-validate your `skill.yaml`
- Run all test cases and record benchmark results
- Submit to the registry for review
- Make your skill available at `registry.ai-skills.dev/{author}/{id}`

### Publishing rules

- Skill IDs must be unique per author (`author/skill-id`)
- Published versions are **immutable** — you cannot overwrite a published version
- Increment the version number for every change
- All test cases must pass before publishing
- Skills violating the [Code of Conduct](../CODE_OF_CONDUCT.md) will be removed

---

## Registry API

The registry exposes a simple REST API:

```
GET /skills                              List all skills (paginated)
GET /skills/{author}/{id}               Get latest version
GET /skills/{author}/{id}/{version}     Get specific version
GET /skills/search?q={query}            Search by name or tag
GET /skills/search?tag={tag}            Filter by tag
POST /skills                            Publish a skill (authenticated)
```

### Example API calls

```bash
# List all skills
curl https://registry.ai-skills.dev/skills

# Get a specific skill
curl https://registry.ai-skills.dev/skills/ai-skills-team/summarize-document

# Search
curl "https://registry.ai-skills.dev/skills/search?q=summarize"
curl "https://registry.ai-skills.dev/skills/search?tag=nlp"
```

---

## Registry Data Format

The registry index follows this schema:

```json
{
  "id": "summarize-document",
  "name": "Document Summarizer",
  "version": "1.0.0",
  "author": "ai-skills-team",
  "description": "...",
  "license": "MIT",
  "tags": ["summarization", "nlp"],
  "execution_type": "prompt",
  "compatible_with": ["langchain", "autogen", "crewai"],
  "benchmarks": {
    "avg_latency_ms": 1100,
    "avg_cost_per_call_usd": 0.003,
    "test_cases_count": 3
  },
  "downloads": 142,
  "published_at": "2026-02-18",
  "skill_url": "https://registry.ai-skills.dev/skills/..."
}
```

---

## Roadmap

- [ ] Web UI for browsing the registry
- [ ] Automated benchmark CI on publish
- [ ] Skill decay monitoring (automatic alerts when quality drops)
- [ ] Dependency graph visualization
- [ ] Collections / curated skill packs
- [ ] Verified author badges
