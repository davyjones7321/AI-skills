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

Usage examples:
    aiskills init my-summarizer
    aiskills validate my-summarizer/skill.yaml
    aiskills export my-summarizer/skill.yaml --target langchain
    aiskills export my-summarizer/skill.yaml --target autogen --output tool.py
    aiskills export my-summarizer/skill.yaml --target crewai
    aiskills info my-summarizer/skill.yaml
"""

import sys
import argparse
import yaml
import json
from pathlib import Path


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


def cmd_init(args):
    name = args.name
    skill_id = name.lower().replace(" ", "-").replace("_", "-")
    skill_name = " ".join(word.capitalize() for word in skill_id.split("-"))
    output_dir = Path(skill_id)

    if output_dir.exists():
        print(f"❌ Directory '{skill_id}' already exists.")
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
✅ Skill scaffolded: {skill_id}/

  📄 skill.yaml    ← Edit this to define your skill
  📄 README.md     ← Document your skill

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
            print("✅ No obvious security issues found (but always review code manually).")
        else:
            print("❌ Security audit found issues:\n")
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
        print(f"❌ Unknown target '{target}'. Available: {', '.join(EXPORTERS.keys())}")
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
    print(f"✅ Exported to {output} (target: {target})")


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
            print(f"❌ Invalid JSON input: {e}")
            sys.exit(1)
    elif args.input_file:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"❌ Input file not found: {args.input_file}")
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
╔══════════════════════════════════════════════╗
║  ai-skills — Skill Info                      ║
╚══════════════════════════════════════════════╝

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
        print(f"    • {inp['name']} ({inp.get('type', '?')}) — {req}")

    print(f"\n  Outputs ({len(outputs)}):")
    for out in outputs:
        print(f"    • {out['name']} ({out.get('type', '?')})")

    print(f"\n  Compatible with: {', '.join(skill.get('compatible_with', ['—']))}")

    if benchmarks:
        print(f"\n  Benchmarks:")
        if "avg_latency_ms" in benchmarks:
            print(f"    • Avg latency:  {benchmarks['avg_latency_ms']}ms")
        if "avg_cost_per_call_usd" in benchmarks:
            print(f"    • Avg cost:     ${benchmarks['avg_cost_per_call_usd']:.4f} per call")
        print(f"    • Test cases:   {len(test_cases)}")

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
  aiskills export my-summarizer/skill.yaml --target autogen --output tool.py
  aiskills info my-summarizer/skill.yaml
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

    # info
    p_info = subparsers.add_parser("info", help="Print skill summary")
    p_info.add_argument("skill_path", help="Path to skill.yaml")

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "validate": cmd_validate,
        "export": cmd_export,
        "run": cmd_run,
        "info": cmd_info,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
