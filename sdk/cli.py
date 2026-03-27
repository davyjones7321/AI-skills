#!/usr/bin/env python3
"""
ai-skills CLI
The command-line interface for the ai-skills universal skill format.

Commands:
    aiskills init <name>              Create a new skill scaffold
    aiskills validate <skill.yaml>    Validate a skill file
    aiskills run <skill.yaml>         Run a skill locally (dry-run)
    aiskills export <skill.yaml>      Export to a target framework
    aiskills info <skill.yaml>        Print skill summary
    aiskills publish <skill.yaml>     Publish a skill to the registry
    aiskills install <author/id>      Install a skill from the registry

Usage examples:
    aiskills init my-summarizer
    aiskills validate my-summarizer/skill.yaml
    aiskills export my-summarizer/skill.yaml --target langchain
    aiskills export my-summarizer/skill.yaml --target autogen --output tool.py
    aiskills export my-summarizer/skill.yaml --target crewai
    aiskills info my-summarizer/skill.yaml
    aiskills publish my-summarizer/skill.yaml
    aiskills install ai-skills-team/summarize-document
    aiskills install ai-skills-team/summarize-document@1.0.0
"""

import sys
import argparse
import os
import yaml
import json
from pathlib import Path
from urllib import request, error
from urllib.parse import urljoin


# ── INIT ──────────────────────────────────────────────────────────────────────

SKILL_TEMPLATE = """\
skill:
  id: __SKILL_ID__
  version: 1.0.0
  name: __SKILL_NAME__
  description: |
    Describe what this skill does in 1-3 sentences.
    Be specific about input and output.
  author: your-name
  license: MIT
  tags: []

  inputs:
    - name: input_text
      type: string
      description: The main input for this skill
      required: true

  outputs:
    - name: result
      type: string
      description: The output of this skill

  execution:
    type: prompt
    model_hint: any
    system_prompt: |
      You are a helpful assistant. Be concise and accurate.
    prompt_template: |
      Process the following input and return a result.

      Input: {input_text}

  benchmarks:
    test_cases:
      - id: basic-test
        description: Basic smoke test
        input:
          input_text: "Hello world"
        expected:
          result_type: string
"""

README_TEMPLATE = """\
# __SKILL_NAME__

> __SKILL_ID__ — an ai-skills compatible skill

## What it does

Describe your skill here.

## Inputs

| Name | Type | Required | Description |
|------|------|----------|-------------|
| input_text | string | ✅ | The main input |

## Outputs

| Name | Type | Description |
|------|------|-------------|
| result | string | The output |

## Usage

```bash
# Validate
aiskills validate skill.yaml

# Export to LangChain
aiskills export skill.yaml --target langchain --output tool.py

# Export to AutoGen
aiskills export skill.yaml --target autogen --output tool.py

# Export to CrewAI
aiskills export skill.yaml --target crewai --output tool.py
```

## License

MIT
"""


DEFAULT_REGISTRY_URL = os.environ.get(
    "AISKILLS_REGISTRY_URL",
    "https://ai-skills-sdk.onrender.com",
)

def _resolve_registry_url(config=None) -> str:
    from sdk.auth_config import DEFAULT_REGISTRY_URL as AUTH_CONFIG_URL
    if config is not None:
        configured_url = getattr(config, "registry_url", None)
        if isinstance(configured_url, str) and configured_url.strip():
            return configured_url.rstrip("/")
    return AUTH_CONFIG_URL.rstrip("/")


def cmd_init(args):
    name = args.name
    skill_id = name.lower().replace(" ", "-").replace("_", "-")
    skill_name = " ".join(word.capitalize() for word in skill_id.split("-"))
    output_dir = Path(skill_id)

    if output_dir.exists():
        print(f"Error: Directory '{skill_id}' already exists.")
        sys.exit(1)

    output_dir.mkdir()
    (output_dir / "skill.yaml").write_text(
        SKILL_TEMPLATE.replace("__SKILL_ID__", skill_id).replace("__SKILL_NAME__", skill_name),
        encoding="utf-8"
    )
    (output_dir / "README.md").write_text(
        README_TEMPLATE.replace("__SKILL_ID__", skill_id).replace("__SKILL_NAME__", skill_name),
        encoding="utf-8"
    )

    print(f"""
OK - Skill scaffolded: {skill_id}/

   skill.yaml    <- Edit this to define your skill
   README.md     <- Document your skill

Next steps:
  cd {skill_id}
  aiskills validate skill.yaml
  aiskills export skill.yaml --target langchain
""")


# ── VALIDATE ──────────────────────────────────────────────────────────────────

def cmd_validate(args):
    # Import using proper relative path resolution
    import importlib.util
    sdk_dir = Path(__file__).parent
    spec = importlib.util.spec_from_file_location("validator", sdk_dir / "validator.py")
    validator_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator_module)
    validate_skill = validator_module.validate_skill

    result = validate_skill(args.skill_path)
    print(f"\nValidating: {args.skill_path}\n{'─' * 40}")
    print(result.report(verbose=args.verbose))
    
    valid = result.valid

    # Run security audit if requested
    if getattr(args, "audit", False):
        sec_spec = importlib.util.spec_from_file_location("security", sdk_dir / "security.py")
        sec_module = importlib.util.module_from_spec(sec_spec)
        sec_spec.loader.exec_module(sec_module)
        scan_skill = sec_module.scan_skill
        
        print(f"\nAuditing: {args.skill_path}\n{'─' * 40}")
        audit_res = scan_skill(args.skill_path)
        if audit_res.is_safe:
            print("OK - No obvious security issues found (but always review code manually).")
        else:
            print("FAIL - Security audit found issues:\n")
            for issue in audit_res.issues:
                print(issue)
            for warning in audit_res.warnings:
                print(warning)
            print("")
            valid = False

    sys.exit(0 if valid else 1)


# ── EXPORT ────────────────────────────────────────────────────────────────────

EXPORTERS = {
    "langchain": ("exporters.langchain", "export_langchain"),
    "autogen": ("exporters.autogen", "export_autogen"),
    "crewai": ("exporters.crewai", "export_crewai"),
}


def cmd_export(args):
    target = args.target.lower()
    if target not in EXPORTERS:
        print(f"Error: Unknown target '{target}'. Available: {', '.join(EXPORTERS.keys())}")
        sys.exit(1)

    sdk_dir = Path(__file__).parent
    sys.path.insert(0, str(sdk_dir))

    module_path, func_name = EXPORTERS[target]
    # Dynamic import
    parts = module_path.split(".")
    module = __import__(module_path, fromlist=[func_name])
    export_fn = getattr(module, func_name)

    output = args.output
    if not output:
        skill_dir = Path(args.skill_path).parent
        output = str(skill_dir / f"{target}_tool.py")

    export_fn(args.skill_path, output)
    print(f"OK - Exported to {output} (target: {target})")


# ── RUN ───────────────────────────────────────────────────────────────────────

def cmd_run(args):
    import importlib.util
    sdk_dir = Path(__file__).parent

    # Import runner
    runner_spec = importlib.util.spec_from_file_location("runner", sdk_dir / "runner.py")
    runner_module = importlib.util.module_from_spec(runner_spec)
    runner_spec.loader.exec_module(runner_module)

    # Parse input
    input_data = {}
    if args.input:
        try:
            input_data = json.loads(args.input)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}")
            sys.exit(1)
    elif args.input_file:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input_file}")
            sys.exit(1)
        with open(input_path, encoding="utf-8") as f:
            input_data = json.load(f)

    dry_run = not args.execute
    model = getattr(args, "model", None)

    print(f"\n{'=' * 50}")
    print(f"  ai-skills -- Running skill")
    print(f"{'=' * 50}")
    print(f"  Skill:  {args.skill_path}")
    print(f"  Mode:   {'>> LIVE' if not dry_run else '-- DRY-RUN'}")
    if model:
        print(f"  Model:  {model}")
    print(f"{'-' * 50}\n")

    try:
        result = runner_module.run_skill(
            skill_path=args.skill_path,
            input_data=input_data,
            dry_run=dry_run,
            model=model,
        )

        print(f"  [OK] Execution complete ({result['latency_ms']}ms)")
        print(f"  Type: {result['execution_type']}\n")
        print(f"{'-' * 50}")
        print(f"  Output:\n")
        print(json.dumps(result["output"], indent=2, ensure_ascii=True))
        print(f"\n{'=' * 50}\n")

    except runner_module.SecurityError as e:
        print(f"  [SECURITY ERROR] {e}")
        sys.exit(1)
    except EnvironmentError as e:
        print(f"  [WARNING] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  [ERROR] {e}")
        sys.exit(1)


# ── PUBLISH ───────────────────────────────────────────────────────────────────

def cmd_publish(args):
    import importlib.util
    sdk_dir = Path(__file__).parent

    skill_path = Path(args.skill_path)
    if not skill_path.exists():
        print(f"Error: File not found: {args.skill_path}")
        sys.exit(1)

    # Step 1: Read and parse
    with open(skill_path, encoding="utf-8") as f:
        raw_content = f.read()

    try:
        data = yaml.safe_load(raw_content)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML: {e}")
        sys.exit(1)

    skill = data.get("skill", {})
    skill_id = skill.get("id", "unknown")
    version = skill.get("version", "0.0.0")
    author = skill.get("author", "unknown")

    # Step 2: Validate
    print(f"\n  Publishing: {author}/{skill_id}@{version}")
    print(f"  {'─' * 40}")

    spec = importlib.util.spec_from_file_location("validator", sdk_dir / "validator.py")
    validator_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator_module)
    validate_skill = validator_module.validate_skill

    result = validate_skill(str(skill_path))
    if not result.valid:
        print(f"\n  FAIL - Skill failed validation:\n")
        print(result.report(verbose=True))
        sys.exit(1)
    print(f"  [1/4] Validation passed")

    # Step 3: Security audit
    sec_spec = importlib.util.spec_from_file_location("security", sdk_dir / "security.py")
    sec_module = importlib.util.module_from_spec(sec_spec)
    sec_spec.loader.exec_module(sec_module)
    scan_skill = sec_module.scan_skill

    audit_res = scan_skill(str(skill_path))
    if not audit_res.is_safe:
        print(f"  [2/4] Security audit found issues:")
        for issue in audit_res.issues:
            print(f"         {issue}")
        for warning in audit_res.warnings:
            print(f"         {warning}")
        print(f"\n  Aborting publish. Fix security issues first.")
        sys.exit(1)
    print(f"  [2/4] Security audit passed")

    # Step 4: Auth
    auth_spec = importlib.util.spec_from_file_location("auth_config", sdk_dir / "auth_config.py")
    auth_module = importlib.util.module_from_spec(auth_spec)
    auth_spec.loader.exec_module(auth_module)
    AuthConfig = auth_module.AuthConfig

    config = AuthConfig()
    token = config.get_token()

    if not token:
        print(f"  [3/4] Not authenticated.")
        print(f"\n  Run: aiskills login --token <your-token> --username <your-name>")
        print(f"  Or set the token in ~/.aiskills/config.json")
        sys.exit(1)
    print(f"  [3/4] Authenticated as: {config.get_username()}")

    # Helper for date serialization
    from datetime import date, datetime
    def _make_json_safe(obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {k: _make_json_safe(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_make_json_safe(item) for item in obj]
        return obj

    # Step 5: Dry-run check
    if args.dry_run:
        print(f"  [4/4] DRY-RUN — would publish to: {_resolve_registry_url(config)}/skills")
        print(f"\n  Payload:")
        payload = {
            "id": skill_id,
            "author": author,
            "version": version,
            "name": skill.get("name", skill_id),
            "description": skill.get("description", "").strip(),
            "tags": skill.get("tags", []),
            "exec_type": skill.get("execution", {}).get("type", "prompt"),
            "benchmarks": _make_json_safe(skill.get("benchmarks", {})),
            "yaml_content": raw_content,
        }
        print(json.dumps({k: v for k, v in payload.items() if k != "yaml_content"}, indent=2))
        print(f"\n  (yaml_content: {len(raw_content)} bytes)")
        print(f"\n  DRY-RUN complete. Remove --dry-run to publish.\n")
        return

    # Step 6: Upload to registry
    execution = skill.get("execution", {})
    benchmarks = skill.get("benchmarks", {})

    payload = json.dumps({
        "id": skill_id,
        "author": author,
        "version": version,
        "name": skill.get("name", skill_id),
        "description": skill.get("description", "").strip(),
        "tags": skill.get("tags", []),
        "exec_type": execution.get("type", "prompt"),
        "benchmarks": _make_json_safe(benchmarks) if benchmarks else {},
        "yaml_content": raw_content,
    }).encode("utf-8")

    registry_url = _resolve_registry_url(config)
    url = f"{registry_url}/skills/"

    req = request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=30) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            skill_url = f"{registry_url}/skills/{resp_data.get('author', author)}/{skill_id}"
            print(f"  [4/4] Published successfully!")
            print(f"\n  Skill URL: {skill_url}")
            print(f"  Version:   {version}")
            print(f"\n  Install with: aiskills install {resp_data.get('author', author)}/{skill_id}\n")
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(body).get("detail", body)
        except json.JSONDecodeError:
            detail = body
        print(f"  [4/4] FAILED: {e.code} — {detail}")
        sys.exit(1)
    except error.URLError as e:
        print(f"  [4/4] FAILED: Cannot connect to registry at {registry_url}")
        print(f"         {e.reason}")
        print(f"\n  Is the registry server running? Start it with:")
        print(f"    uvicorn registry.api.main:app --reload")
        sys.exit(1)


# ── INSTALL ───────────────────────────────────────────────────────────────────

def cmd_install(args):
    import importlib.util
    sdk_dir = Path(__file__).parent

    # Parse skill reference: author/skill-id or author/skill-id@version
    skill_ref = args.skill_ref
    version = None

    if "@" in skill_ref:
        skill_ref, version = skill_ref.rsplit("@", 1)

    parts = skill_ref.split("/", 1)
    if len(parts) != 2:
        print(f"Error: Invalid skill reference '{args.skill_ref}'")
        print(f"  Expected format: author/skill-id or author/skill-id@version")
        print(f"  Example: aiskills install ai-skills-team/summarize-document")
        sys.exit(1)

    author, skill_id = parts

    # Load auth config for registry URL
    auth_spec = importlib.util.spec_from_file_location("auth_config", sdk_dir / "auth_config.py")
    auth_module = importlib.util.module_from_spec(auth_spec)
    auth_spec.loader.exec_module(auth_module)
    AuthConfig = auth_module.AuthConfig

    config = AuthConfig()
    registry_url = _resolve_registry_url(config)

    # Build API URL
    if version:
        api_url = f"{registry_url}/skills/{author}/{skill_id}/{version}"
    else:
        api_url = f"{registry_url}/skills/{author}/{skill_id}"

    print(f"\n  Installing: {author}/{skill_id}" + (f"@{version}" if version else " (latest)"))
    print(f"  {'─' * 40}")

    # Fetch from registry
    try:
        req = request.Request(api_url, method="GET")
        with request.urlopen(req, timeout=30) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as e:
        if e.code == 404:
            print(f"  FAIL: Skill '{author}/{skill_id}" + (f"@{version}" if version else "") + "' not found in registry")
        else:
            body = e.read().decode("utf-8", errors="replace")
            print(f"  FAIL: {e.code} — {body}")
        sys.exit(1)
    except error.URLError as e:
        print(f"  FAIL: Cannot connect to registry at {registry_url}")
        print(f"         {e.reason}")
        print(f"\n  Is the registry server running? Start it with:")
        print(f"    uvicorn registry.api.main:app --reload")
        sys.exit(1)

    yaml_content = resp_data.get("yaml_content", "")
    installed_version = resp_data.get("version", "unknown")
    reviewed = resp_data.get("reviewed", False)

    if not yaml_content:
        print(f"  FAIL: Skill has no YAML content")
        sys.exit(1)

    # Show warning for unreviewed skills
    if not reviewed:
        print(f"  [!] WARNING: This skill has NOT been reviewed. Inspect the skill.yaml before using.")

    # Save to skills/ directory
    install_dir = Path("skills") / skill_id
    install_dir.mkdir(parents=True, exist_ok=True)
    skill_file = install_dir / "skill.yaml"

    skill_file.write_text(yaml_content, encoding="utf-8")
    print(f"  [1/1] Saved to {skill_file}")
    print(f"  Version: {installed_version}")

    # Auto-export if requested
    if args.export:
        target = args.export.lower()
        if target not in EXPORTERS:
            print(f"\n  Warning: Unknown export target '{target}'. Skipping export.")
            print(f"  Available: {', '.join(EXPORTERS.keys())}")
        else:
            sys.path.insert(0, str(sdk_dir))
            module_path, func_name = EXPORTERS[target]
            module = __import__(module_path, fromlist=[func_name])
            export_fn = getattr(module, func_name)

            output_file = str(install_dir / f"{target}_tool.py")
            export_fn(str(skill_file), output_file)
            print(f"  Exported to {output_file} (target: {target})")

    print(f"\n  Done! Skill installed to: {install_dir}/\n")


# ── LOGIN ─────────────────────────────────────────────────────────────────────

def cmd_login(args):
    import importlib.util
    sdk_dir = Path(__file__).parent

    auth_spec = importlib.util.spec_from_file_location("auth_config", sdk_dir / "auth_config.py")
    auth_module = importlib.util.module_from_spec(auth_spec)
    auth_spec.loader.exec_module(auth_module)
    AuthConfig = auth_module.AuthConfig

    config = AuthConfig()

    if args.token and args.username:
        config.save_token(args.token, args.username)
        print(f"\n  OK - Logged in as: {args.username}")
        print(f"  Token saved to: ~/.aiskills/config.json\n")
    elif args.registry_url:
        config.registry_url = args.registry_url
        print(f"\n  OK - Registry URL set to: {args.registry_url}\n")
    elif args.status:
        if config.is_authenticated():
            print(f"\n  Logged in as: {config.get_username()}")
            print(f"  Registry:    {config.registry_url}\n")
        else:
            print(f"\n  Not logged in.")
            print(f"  Registry:    {config.registry_url}")
            print(f"\n  Run: aiskills login --token <your-token> --username <your-name>\n")
    elif args.logout:
        config.clear_token()
        print(f"\n  OK - Logged out. Token cleared.\n")
    else:
        try:
            _, username = config.complete_oauth_login()
            print(f"\n  OK - Logged in as: {username}")
            print(f"  Token saved to: ~/.aiskills/config.json\n")
        except Exception as e:
            print(f"Failed to complete login: {e}")
            sys.exit(1)


# ── INFO ──────────────────────────────────────────────────────────────────────

def cmd_info(args):
    with open(args.skill_path) as f:
        data = yaml.safe_load(f)

    skill = data["skill"]
    inputs = skill.get("inputs", [])
    outputs = skill.get("outputs", [])
    benchmarks = skill.get("benchmarks", {})
    test_cases = benchmarks.get("test_cases", [])

    print(f"""
==============================
  ai-skills -- Skill Info
==============================

  ID:          {skill.get('id', '—')}
  Name:        {skill.get('name', '—')}
  Version:     {skill.get('version', '—')}
  Author:      {skill.get('author', '—')}
  License:     {skill.get('license', '—')}
  Tags:        {', '.join(skill.get('tags', [])) or '—'}

  Description:
    {skill.get('description', '—').strip()}

  Execution Type: {skill.get('execution', {}).get('type', '—')}

  Inputs ({len(inputs)}):""")

    for inp in inputs:
        req = "required" if inp.get("required") else f"optional, default={inp.get('default', 'null')}"
        print(f"    - {inp['name']} ({inp.get('type', '?')}) -- {req}")

    print(f"\n  Outputs ({len(outputs)}):")
    for out in outputs:
        print(f"    - {out['name']} ({out.get('type', '?')})")

    print(f"\n  Compatible with: {', '.join(skill.get('compatible_with', ['—']))}")

    if benchmarks:
        print(f"\n  Benchmarks:")
        if "avg_latency_ms" in benchmarks:
            print(f"    - Avg latency:  {benchmarks['avg_latency_ms']}ms")
        if "avg_cost_per_call_usd" in benchmarks:
            print(f"    - Avg cost:     ${benchmarks['avg_cost_per_call_usd']:.4f} per call")
        print(f"    - Test cases:   {len(test_cases)}")

    print()


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="aiskills",
        description="ai-skills CLI — Universal AI skill format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aiskills init my-summarizer
  aiskills validate my-summarizer/skill.yaml
  aiskills export my-summarizer/skill.yaml --target langchain
  aiskills info my-summarizer/skill.yaml
  aiskills publish my-summarizer/skill.yaml
  aiskills install ai-skills-team/summarize-document
  aiskills login --token <token> --username <name>
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Scaffold a new skill")
    p_init.add_argument("name", help="Skill name (e.g. my-summarizer)")

    # validate
    p_val = subparsers.add_parser("validate", help="Validate a skill.yaml file")
    p_val.add_argument("skill_path", help="Path to skill.yaml")
    p_val.add_argument("--verbose", "-v", action="store_true", help="Show all warnings")
    p_val.add_argument("--audit", "-a", action="store_true", help="Run security audit on the file")

    # export
    p_exp = subparsers.add_parser("export", help="Export skill to a target framework")
    p_exp.add_argument("skill_path", help="Path to skill.yaml")
    p_exp.add_argument("--target", "-t", required=True,
                       choices=list(EXPORTERS.keys()),
                       help="Target framework")
    p_exp.add_argument("--output", "-o", help="Output file path (default: <target>_tool.py)")

    # run
    p_run = subparsers.add_parser("run", help="Run a skill locally")
    p_run.add_argument("skill_path", help="Path to skill.yaml")
    p_run.add_argument("--input", "-i", help="Input as JSON string")
    p_run.add_argument("--input-file", "-f", help="Path to JSON input file")
    p_run.add_argument("--execute", "-e", action="store_true",
                       help="Actually call LLM/API (default is dry-run)")
    p_run.add_argument("--model", "-m", help="Override model (for prompt type)")

    # publish
    p_pub = subparsers.add_parser("publish", help="Publish a skill to the registry")
    p_pub.add_argument("skill_path", help="Path to skill.yaml")
    p_pub.add_argument("--dry-run", action="store_true",
                       help="Show what would be published without uploading")

    # install
    p_inst = subparsers.add_parser("install", help="Install a skill from the registry")
    p_inst.add_argument("skill_ref", help="Skill reference (e.g. author/skill-id or author/skill-id@1.0.0)")
    p_inst.add_argument("--export", help="Auto-export after install (e.g. langchain, autogen, crewai)")

    # login
    p_login = subparsers.add_parser("login", help="Manage registry authentication")
    p_login.add_argument("--token", help="Auth token to save")
    p_login.add_argument("--username", help="Your username")
    p_login.add_argument("--status", action="store_true", help="Show login status")
    p_login.add_argument("--logout", action="store_true", help="Clear saved token")
    p_login.add_argument("--registry-url", help="Set custom registry URL")

    # info
    p_info = subparsers.add_parser("info", help="Print skill summary")
    p_info.add_argument("skill_path", help="Path to skill.yaml")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "validate": cmd_validate,
        "export": cmd_export,
        "run": cmd_run,
        "publish": cmd_publish,
        "install": cmd_install,
        "login": cmd_login,
        "info": cmd_info,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
