# Announcing `ai-skills`: The Universal Open Standard for AI Agent Tools

Today, the AI agent ecosystem is massively fragmented. If you write an incredible custom tool for your LangChain agent, you can't reuse it in AutoGen. If you switch to CrewAI, you have to rewrite all your tools from scratch. 

We don't do this anywhere else in software engineering. We have package managers like `npm` and `pip` for code. We have Docker for containers. But for AI agents, we are stuck rewriting basic tools over and over.

Today we're open-sourcing **`ai-skills`**: a framework-agnostic, universal file format (`skill.yaml`) for AI agent capabilities.

## What is it?

An `ai-skill` is a single YAML file that describes exactly *what* a tool does, *how* it runs, and *what inputs/outputs* it expects. 

It supports 4 execution types:
1. `prompt`: A prompt template sent to an LLM (e.g., text summarization).
2. `tool_call`: A REST API call (e.g., fetching weather).
3. `code`: A portable block of Python code (e.g., converting Markdown to HTML).
4. `chain`: A sequence of other skills (e.g., detect language -> translate -> summarize).

## Write Once, Run Anywhere

Instead of writing tools tied to an SDK, you define your tool in `skill.yaml`. 
Then, using the open-source CLI, you export it:

```bash
# Export to native LangChain BaseTool
aiskills export skill.yaml --target langchain

# Export to AutoGen FunctionTool
aiskills export skill.yaml --target autogen

# Export to CrewAI Tool
aiskills export skill.yaml --target crewai
```

## Built-In Validation & Security

Because executing random code for AI agents is dangerous, `ai-skills` comes with a powerful CLI out of the box.

- `aiskills validate skill.yaml` checks your schema against the official v0.1 spec.
- `aiskills validate --audit skill.yaml` runs a static security analysis, catching leaked hardcoded secrets, dangerous Python imports (`os`, `subprocess`), and insecure HTTP endpoints.

## The Public Registry

We are also launching the prototype of the `ai-skills` public registry. We already have 19 high-quality, fully tested example skills ready to download and use today—including everything from invoice data extractors, to conventional commit generators, to markdown converters.

## Get Involved
We want this to be a community-driven standard. 
- Star the repo on GitHub to show your support.
- Contribute an adapter for your favorite framework (Semantic Kernel, LlamaIndex, etc.).
- Build and publish your own skills!

Check out the repo here: [Link]
Read the v0.1 Specification: [Link]
