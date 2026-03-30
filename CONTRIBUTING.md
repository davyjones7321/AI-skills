# Contributing to ai-skills

First off, thank you for considering contributing to `ai-skills`! We want to make the AI agent ecosystem open, interoperable, and standardized. To make this happen, we need your help.

## How Can I Contribute?

### 1. Adding a New Example Skill
The easiest way to contribute is to create a new, high-quality skill for the `examples/` directory.

1. Create a new branch: `git checkout -b add-my-skill`
2. Run `aiskills init my-skill-name` inside the `examples/` folder.
3. Edit the `skill.yaml` to define your skill.
4. **Crucial:** Run `aiskills validate examples/my-skill-name/skill.yaml` to ensure it passes the spec.
5. **Recommended:** Run `aiskills run examples/my-skill-name/skill.yaml --input-file input.json` to test it locally.
6. Create a Pull Request with your new skill.

### 2. Improving the CLI / SDK
If you want to add features to the `aiskills` CLI or improve the SDK:

1. All Python code lives in the `sdk/` directory.
2. Key files: `cli.py` (commands), `validator.py` (schema checks), `runner.py` (skill execution), `security.py` (audit).
3. We try to use standard library modules wherever possible to keep the SDK ultra-lightweight.
4. Ensure any new CLI flags are documented in `cli.py` and `README.md`.

### 3. Writing New Framework Adapters
Currently, we support exporting to LangChain, AutoGen, and CrewAI. If you use Semantic Kernel, LlamaIndex, or another framework, we'd love an adapter!

1. Create a new file in `sdk/exporters/your_framework.py`.
2. Implement an `export_yourframework(skill_path: str, output_path: str)` function.
3. Hook it up in the `EXPORTERS` dictionary inside `sdk/cli.py`.

## Pull Request Process

1. Fork the repo and create your branch from `main`.
2. Ensure you have tested your code. If adding a skill, it **must** pass `aiskills validate`.
3. Update the `README.md` and `OVERVIEW.md` if your changes alter the CLI usage or add new examples.
4. Submit your PR!

## Code of Conduct
Please note we have a [Code of Conduct](CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.

---

## Session Update — 2026-03-26

The repository auth flow changed in this session. Contributors working on the registry should now assume GitHub OAuth plus JWT-based auth, not database token matching or manual CLI token paste. If you touch registry auth behavior, update the backend, frontend, CLI, and root documentation together so the login flow stays consistent.

## Session Update — 2026-03-28 (Standalone CLI)

The SDK is now published to PyPI as `ai-skills-sdk`. Contributors no longer need to clone the repo to use the CLI — `pip install ai-skills-sdk` works directly. The publish page on the frontend has been updated to reflect this. If you are developing on the SDK itself, use `pip install -e .` from the repo root.

## Session Update — 2026-03-30

Publishing flow update: the registry now supports web-based publishing via the `/publish` interactive studio in addition to the CLI. Contributors working on backend serialization should note the new `registry/api/utils.py` shared utility, which provides a `make_json_safe` helper if you need to add date-safe JSON fields to the database.
