# ai-skills Security Model

The ai-skills project defines a portable, executable format for AI agents to run. Because skills can include API calls and raw Python code execution, security is a top priority.

This document outlines the security model for `ai-skills` and how both publishers and consumers should approach skill security.

---

## 1. The Threat Model

An ai-skill could potentially:
1. **Exfiltrate data** by sending user data to an attacker-controlled server.
2. **Execute arbitrary code** on the host machine using `execution.type: code`.
3. **Leak secrets** if environment variables or API keys are improperly handled.
4. **Cause malicious side effects** if a `tool_call` executes destructive operations (like SQL drops).

---

## 2. Built-in Security Features

### The Audit Tool
We provide a built-in security scanner to detect obvious vulnerabilities in skill files:

```bash
aiskills validate --audit path/to/skill.yaml
```

This scanner checks for:
- **Hardcoded secrets**: Checks for common token formats (OpenAI, AWS, generic Bearer tokens) to prevent publishers from accidentally leaking their keys.
- **Insecure endpoints**: Flags `tool_call` endpoints that use `http://` instead of `https://` (except for `localhost`).
- **Dangerous Python imports**: Statically analyzes embeded Python code (`execution.type: code`) for imports like `os`, `sys`, `subprocess`, `socket`, `requests`, `urllib`, `pickle`.
- **Dangerous built-ins**: Flags usage of `eval()`, `exec()`, `open()`, `__import__()`, etc.

---

## 3. Best Practices for Developers (Publishers)

If you are writing and publishing an ai-skill:

1. **Never hardcode secrets.** Use `{env.YOUR_API_KEY}` placeholders. The exporting framework will map these to the runtime environment.
2. **Use HTTPS.** Always use secure endpoints for `tool_call` executions.
3. **Minimize code execution.** If you can solve the problem with a `chain` or a `prompt` or a `tool_call`, prefer that over raw `code` execution.
4. **Be explicit about danger.** If your tool mutates data or performs destructive actions (e.g., executing SQL), document it clearly in your description.

---

## 4. Best Practices for Consumers (Runners)

If you are downloading and running an ai-skill from the registry:

1. **Always audit first.** Run `aiskills validate --audit` before using a third-party skill.
2. **Sandboxing (Recommended).** If a skill uses `execution.type: code`, **do not run it in your primary application process**.
   - **LangChain/AutoGen/CrewAI**: We recommend running code skills inside a Docker container, WASM sandbox, or secure execution environment (like E2B or typical AutoGen docker environments).
3. **Review code manually.** The `--audit` flag uses static analysis and is not foolproof. A malicious actor could obfuscate their code. Always read the `.yaml` file.
4. **Scope environment variables.** Only provide the specific `{env.*}` variables that the skill explicitly requires. Do not inject your entire environment into the skill context.

---

## 5. Future Plans (v0.2+)

We are actively working on:
- **Registry verified publishers**: A badge system for verified skill authors.
- **Native WASM sandbox**: A built-in executor that runs `code` type skills in completely isolated WebAssembly environments by default.
- **Hash verification**: Pinning a skill to a SHA-256 hash when downloading to prevent tampered versions.
