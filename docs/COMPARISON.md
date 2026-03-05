# How ai-skills Compares

When building `ai-skills`, we are often asked how it compares to existing standards. Here is a breakdown of why `skill.yaml` exists and what niche it fills.

---

## vs. Framework-Specific Tools (LangChain / AutoGen / CrewAI)
Frameworks like LangChain define tools as Python classes (`BaseTool`). AutoGen uses annotated Python functions. 

**The Problem:** If you write a great tool for LangChain, you cannot easily drop it into CrewAI. The AI agent ecosystem is heavily fragmented.
**The Solution:** `ai-skills` sits *above* the frameworks. You write your skill once in `skill.yaml`, and the `aiskills export` command generates the native LangChain/AutoGen/CrewAI code for you.

## vs. OpenAPI / Swagger
OpenAPI/Swagger is the gold standard for defining massive REST APIs. 

**The Problem:** OpenAPI is designed for defining thousands of endpoints for web services. It is overly complex for an AI agent that just needs a simple "summarize text" prompt or a 10-line Python script. OpenAPI also lacks concepts like `prompt_template` execution or `chain` execution.
**The Solution:** `skill.yaml` is designed specifically for atomic AI tools. It supports `prompt` templates, local Python `code` execution, and `chain` execution natively—none of which OpenAPI supports.

## vs. `SKILL.md` (OpenAI / Anthropic Ecosystems)
Some repos use a `SKILL.md` file format (often seen in coding assistants).

**The Problem:** These are almost entirely unstructured markdown files designed to be injected into a system prompt. They tell an LLM "how to write a React component," but they don't define a strict, typed input/output interface, nor do they define how an automated system should invoke an external API.
**The Solution:** `ai-skills` uses strictly typed YAML. It guarantees the inputs, outputs, and execution methods so that programmatic orchestrators (not just chatbots) can reliably use the tools.

## vs. Model Context Protocol (MCP)
Anthropic recently introduced the Model Context Protocol (MCP) for connecting AI models to data sources.

**The Problem:** MCP is a live, running server protocol. You have to run a Node or Python server that speaks the MCP JSON-RPC protocol over stdio or SSE. This is fantastic for connecting to live databases (like a Postgres database), but it is total overkill if you just want to share a good text summarization prompt or a 5-line markdown-to-html converter.
**The Solution:** `ai-skills` requires no running server. It is a static file format for packaging deterministic logic, prompts, and portable tools. You can even wrap an `ai-skill` inside an MCP server!
