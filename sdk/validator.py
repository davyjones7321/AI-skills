"""
ai-skills SDK — Validator
Validates a skill.yaml file against the ai-skills v0.1 specification.

Usage:
    python validator.py path/to/skill.yaml
    python validator.py path/to/skill.yaml --verbose
"""

import sys
import re
import yaml
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

VALID_EXECUTION_TYPES = {"prompt", "tool_call", "chain", "code"}
VALID_DATA_TYPES = {"string", "integer", "number", "boolean", "array", "object", "file", "image", "any"}
VALID_FRAMEWORKS = {"langchain", "autogen", "crewai", "semantic_kernel", "raw_api"}
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
ID_PATTERN = re.compile(r"^[a-z0-9-]+$")


@dataclass
class ValidationResult:
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, msg: str):
        self.errors.append(f"  ✗ ERROR: {msg}")
        self.valid = False

    def warn(self, msg: str):
        self.warnings.append(f"  ⚠ WARNING: {msg}")

    def report(self, verbose: bool = False) -> str:
        lines = []
        if self.valid:
            lines.append("✅ Skill is valid!\n")
        else:
            lines.append("❌ Skill validation failed.\n")

        if self.errors:
            lines.append("Errors:")
            lines.extend(self.errors)
            lines.append("")

        if self.warnings and (verbose or not self.valid):
            lines.append("Warnings:")
            lines.extend(self.warnings)
            lines.append("")

        return "\n".join(lines)


def validate_skill(skill_path: str) -> ValidationResult:
    result = ValidationResult()
    path = Path(skill_path)

    # --- File checks ---
    if not path.exists():
        result.error(f"File not found: {skill_path}")
        return result

    if path.suffix not in {".yaml", ".yml", ".json"}:
        result.error(f"Unsupported file type: {path.suffix}. Must be .yaml or .json")
        return result

    # --- Parse YAML ---
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        result.error(f"Invalid YAML: {e}")
        return result

    if not isinstance(data, dict):
        result.error("Root of skill file must be a YAML mapping")
        return result

    if "skill" not in data:
        result.error("Missing top-level 'skill' key")
        return result

    skill = data["skill"]
    if not isinstance(skill, dict):
        result.error("'skill' must be a mapping/object")
        return result

    # --- Required fields ---
    _check_required_string(skill, "id", result)
    _check_required_string(skill, "version", result)
    _check_required_string(skill, "name", result)
    _check_required_string(skill, "description", result)

    # --- ID format ---
    if "id" in skill:
        if not ID_PATTERN.match(str(skill["id"])):
            result.error(f"'id' must match pattern [a-z0-9-]+ (got: '{skill['id']}')")
        if len(str(skill["id"])) > 64:
            result.error("'id' must be 64 characters or less")

    # --- Version format ---
    if "version" in skill:
        if not SEMVER_PATTERN.match(str(skill["version"])):
            result.error(f"'version' must be semantic version (e.g. 1.0.0), got: '{skill['version']}'")

    if "spec_version" in skill:
        if not isinstance(skill["spec_version"], (str, int, float)):
            result.error("'spec_version' must be a string or number")

    # --- Name length ---
    if "name" in skill and len(str(skill["name"])) > 100:
        result.error("'name' must be 100 characters or less")

    # --- Description length ---
    if "description" in skill and len(str(skill["description"])) > 1000:
        result.warn("'description' is over 1000 characters — consider shortening")

    # --- Inputs ---
    if "inputs" not in skill:
        result.error("Missing required field: 'inputs'")
    else:
        _validate_inputs(skill["inputs"], result)

    # --- Outputs ---
    if "outputs" not in skill:
        result.error("Missing required field: 'outputs'")
    else:
        _validate_outputs(skill["outputs"], result)

    # --- Execution ---
    if "execution" not in skill:
        result.error("Missing required field: 'execution'")
    else:
        _validate_execution(skill["execution"], skill.get("inputs", []), result)

    # --- Optional fields ---
    if "compatible_with" in skill:
        for fw in skill["compatible_with"]:
            if fw not in VALID_FRAMEWORKS:
                result.warn(f"Unknown framework '{fw}' in compatible_with (valid: {', '.join(sorted(VALID_FRAMEWORKS))})")

    if "benchmarks" in skill:
        _validate_benchmarks(skill["benchmarks"], result)

    if "tags" in skill:
        if not isinstance(skill["tags"], list):
            result.error("'tags' must be a list")
        elif len(skill["tags"]) > 20:
            result.warn("Consider limiting tags to 20 or fewer")

    # --- Recommendations ---
    if "author" not in skill:
        result.warn("Consider adding 'author' field")
    if "license" not in skill:
        result.warn("Consider adding 'license' field (e.g. MIT, Apache-2.0)")
    if "benchmarks" not in skill:
        result.warn("Consider adding 'benchmarks' with test cases for quality assurance")

    return result


def _check_required_string(obj: dict, field: str, result: ValidationResult):
    if field not in obj:
        result.error(f"Missing required field: '{field}'")
    elif not isinstance(obj[field], str) or not obj[field].strip():
        result.error(f"'{field}' must be a non-empty string")


def _validate_inputs(inputs: Any, result: ValidationResult):
    if not isinstance(inputs, list):
        result.error("'inputs' must be a list")
        return
    if len(inputs) == 0:
        result.warn("'inputs' is empty — is this intentional?")

    names = set()
    for i, inp in enumerate(inputs):
        prefix = f"inputs[{i}]"
        if not isinstance(inp, dict):
            result.error(f"{prefix} must be a mapping")
            continue

        if "name" not in inp:
            result.error(f"{prefix}: missing 'name'")
        else:
            if inp["name"] in names:
                result.error(f"{prefix}: duplicate input name '{inp['name']}'")
            names.add(inp["name"])

        if "type" not in inp:
            result.error(f"{prefix}: missing 'type'")
        elif inp["type"] not in VALID_DATA_TYPES:
            result.error(f"{prefix}: invalid type '{inp['type']}'. Valid types: {', '.join(sorted(VALID_DATA_TYPES))}")

        if "minimum" in inp and "maximum" in inp:
            if inp["minimum"] > inp["maximum"]:
                result.error(f"{prefix}: 'minimum' ({inp['minimum']}) cannot be greater than 'maximum' ({inp['maximum']})")
        
        if "min_length" in inp and "max_length" in inp:
            if inp["min_length"] > inp["max_length"]:
                result.error(f"{prefix}: 'min_length' ({inp['min_length']}) cannot be greater than 'max_length' ({inp['max_length']})")


def _validate_outputs(outputs: Any, result: ValidationResult):
    if not isinstance(outputs, list):
        result.error("'outputs' must be a list")
        return
    if len(outputs) == 0:
        result.warn("'outputs' is empty — is this intentional?")

    names = set()
    for i, out in enumerate(outputs):
        prefix = f"outputs[{i}]"
        if not isinstance(out, dict):
            result.error(f"{prefix} must be a mapping")
            continue

        if "name" not in out:
            result.error(f"{prefix}: missing 'name'")
        else:
            if out["name"] in names:
                result.error(f"{prefix}: duplicate output name '{out['name']}'")
            names.add(out["name"])

        if "type" not in out:
            result.error(f"{prefix}: missing 'type'")
        elif out["type"] not in VALID_DATA_TYPES:
            result.error(f"{prefix}: invalid type '{out['type']}'")

        if "min_length" in out and "max_length" in out:
            if out["min_length"] > out["max_length"]:
                result.error(f"{prefix}: 'min_length' ({out['min_length']}) cannot be greater than 'max_length' ({out['max_length']})")


def _validate_execution(execution: Any, inputs: list, result: ValidationResult):
    if not isinstance(execution, dict):
        result.error("'execution' must be a mapping")
        return

    if "type" not in execution:
        result.error("'execution.type' is required")
        return

    exec_type = execution["type"]
    if exec_type not in VALID_EXECUTION_TYPES:
        result.error(f"'execution.type' must be one of: {', '.join(sorted(VALID_EXECUTION_TYPES))}")
        return

    if exec_type == "prompt":
        if "prompt_template" not in execution:
            result.error("'execution.prompt_template' is required for type 'prompt'")
        else:
            # Check that placeholders in the template match defined inputs
            template = execution["prompt_template"]
            placeholders = set(re.findall(r"\{(\w+)\}", template))
            input_names = {inp["name"] for inp in inputs if isinstance(inp, dict) and "name" in inp}
            unknown = placeholders - input_names
            if unknown:
                result.warn(f"Prompt template references undefined inputs: {unknown}")

    elif exec_type == "tool_call":
        if "endpoint" not in execution and "function" not in execution:
            result.error("'execution' of type 'tool_call' requires either 'endpoint' or 'function'")

    elif exec_type == "chain":
        if "steps" not in execution or not isinstance(execution["steps"], list):
            result.error("'execution' of type 'chain' requires 'steps' list")

    elif exec_type == "code":
        if "code" not in execution:
            result.error("'execution' of type 'code' requires a 'code' field")
        if "language" not in execution:
            result.warn("'execution.language' not specified for type 'code' — defaulting to python")


def _validate_benchmarks(benchmarks: Any, result: ValidationResult):
    if not isinstance(benchmarks, dict):
        result.error("'benchmarks' must be a mapping")
        return

    if "avg_latency_ms" in benchmarks:
        if not isinstance(benchmarks["avg_latency_ms"], (int, float)) or benchmarks["avg_latency_ms"] < 0:
            result.error("'benchmarks.avg_latency_ms' must be a non-negative number")

    if "avg_cost_per_call_usd" in benchmarks:
        if not isinstance(benchmarks["avg_cost_per_call_usd"], (int, float)) or benchmarks["avg_cost_per_call_usd"] < 0:
            result.error("'benchmarks.avg_cost_per_call_usd' must be a non-negative number")

    if "test_cases" in benchmarks:
        if not isinstance(benchmarks["test_cases"], list):
            result.error("'benchmarks.test_cases' must be a list")
        else:
            ids = set()
            for i, tc in enumerate(benchmarks["test_cases"]):
                prefix = f"test_cases[{i}]"
                if not isinstance(tc, dict):
                    result.error(f"{prefix}: must be a mapping")
                    continue
                if "id" not in tc:
                    result.warn(f"{prefix}: missing 'id' field")
                elif tc["id"] in ids:
                    result.error(f"{prefix}: duplicate test case id '{tc['id']}'")
                else:
                    ids.add(tc["id"])
                if "input" not in tc:
                    result.warn(f"{prefix}: missing 'input' field")
                if "expected" not in tc:
                    result.warn(f"{prefix}: missing 'expected' field (no assertions will be run)")


def main():
    parser = argparse.ArgumentParser(description="Validate an ai-skills skill.yaml file")
    parser.add_argument("skill_path", help="Path to skill.yaml file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all warnings even when valid")
    args = parser.parse_args()

    print(f"\nValidating: {args.skill_path}\n{'─' * 40}")
    result = validate_skill(args.skill_path)
    print(result.report(verbose=args.verbose))

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
