"""
ai-skills SDK — Runner
Executes skills locally. Supports all 4 execution types:
  - prompt:    Format template + call LLM (or dry-run)
  - tool_call: Make HTTP request to endpoint
  - code:      Execute embedded Python in sandbox
  - chain:     Execute skill chain (placeholder)

Usage (via CLI):
    aiskills run skill.yaml --input '{"text": "hello"}'
    aiskills run skill.yaml --input-file input.json
    aiskills run skill.yaml --dry-run
    aiskills run skill.yaml --execute --model gpt-4
"""

import os
import re
import json
import time
import yaml
from pathlib import Path


# ── MAIN ENTRY ────────────────────────────────────────────────────────────────

def run_skill(skill_path: str, input_data: dict, dry_run: bool = True, model: str = None) -> dict:
    """
    Run a skill locally.
    
    Args:
        skill_path: Path to skill.yaml
        input_data: Dict of input values
        dry_run: If True, don't actually call APIs/LLMs — just show what would happen
        model: Override the model hint (for prompt type)
    
    Returns:
        Dict with 'output', 'latency_ms', and 'execution_type' keys
    """
    path = Path(skill_path)
    if not path.exists():
        raise FileNotFoundError(f"Skill file not found: {skill_path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "skill" not in data:
        raise ValueError("Invalid skill file: missing top-level 'skill' key")

    skill = data["skill"]
    execution = skill.get("execution", {})
    exec_type = execution.get("type")

    # Validate required inputs
    _validate_inputs(skill, input_data)

    # Apply defaults for missing optional inputs
    input_data = _apply_defaults(skill, input_data)

    start = time.time()

    if exec_type == "prompt":
        result = _run_prompt(skill, input_data, dry_run, model)
    elif exec_type == "tool_call":
        result = _run_tool_call(skill, input_data, dry_run)
    elif exec_type == "code":
        result = _run_code(skill, input_data)
    elif exec_type == "chain":
        result = _run_chain(skill, input_data, dry_run)
    else:
        raise ValueError(f"Unknown execution type: {exec_type}")

    elapsed_ms = round((time.time() - start) * 1000)

    return {
        "output": result,
        "latency_ms": elapsed_ms,
        "execution_type": exec_type,
    }


# ── INPUT VALIDATION ──────────────────────────────────────────────────────────

def _validate_inputs(skill: dict, input_data: dict):
    """Check that all required inputs are present."""
    inputs = skill.get("inputs", [])
    for inp in inputs:
        if inp.get("required", False) and inp["name"] not in input_data:
            raise ValueError(f"Missing required input: '{inp['name']}'")


def _apply_defaults(skill: dict, input_data: dict) -> dict:
    """Apply default values for optional inputs not provided."""
    result = dict(input_data)
    inputs = skill.get("inputs", [])
    for inp in inputs:
        if inp["name"] not in result and "default" in inp:
            result[inp["name"]] = inp["default"]
    return result


# ── PROMPT EXECUTION ──────────────────────────────────────────────────────────

def _run_prompt(skill: dict, inputs: dict, dry_run: bool, model_override: str = None) -> dict:
    """Run a prompt-type skill."""
    execution = skill["execution"]
    system_prompt = execution.get("system_prompt", "").strip()
    template = execution.get("prompt_template", "")
    output_parser = execution.get("output_parser", "none")
    model = model_override or execution.get("model_hint", "gpt-3.5-turbo")
    if model == "any":
        model = "gpt-3.5-turbo"

    # Format the prompt template with inputs
    try:
        formatted = template.format(**inputs)
    except KeyError as e:
        raise ValueError(f"Prompt template references undefined input: {e}")

    if dry_run:
        return {
            "_mode": "dry-run",
            "_note": "Pass --execute to call the LLM API",
            "model": model,
            "system_prompt": system_prompt if system_prompt else "(none)",
            "formatted_prompt": formatted,
            "output_parser": output_parser,
        }

    # Live execution — call OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY not set. Set it in your environment or .env file.\n"
            "  Windows:  set OPENAI_API_KEY=sk-...\n"
            "  Linux:    export OPENAI_API_KEY=sk-..."
        )

    try:
        import urllib.request
        import ssl

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": formatted})

        body = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": 0.3,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )

        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))

        raw_output = resp_data["choices"][0]["message"]["content"]
        usage = resp_data.get("usage", {})

        parsed = _parse_output(raw_output, output_parser)
        parsed["_usage"] = {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "model": model,
        }
        return parsed

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API error ({e.code}): {error_body[:500]}")


# ── TOOL_CALL EXECUTION ──────────────────────────────────────────────────────

def _run_tool_call(skill: dict, inputs: dict, dry_run: bool) -> dict:
    """Run a tool_call-type skill."""
    execution = skill["execution"]
    endpoint = execution.get("endpoint", {})

    url = endpoint.get("url", "")
    method = endpoint.get("method", "GET").upper()
    headers = endpoint.get("headers", {})
    params = endpoint.get("params", {})

    # Resolve {input} and {env.VAR} references in all string values
    url = _resolve_refs(url, inputs)
    headers = {k: _resolve_refs(v, inputs) for k, v in headers.items()}
    params = {k: _resolve_refs(v, inputs) for k, v in params.items()}

    if dry_run:
        return {
            "_mode": "dry-run",
            "_note": "Pass --execute to make the actual HTTP request",
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
        }

    # Live execution — make HTTP request
    try:
        import urllib.request
        import urllib.parse
        import ssl

        if params and method == "GET":
            url = url + "?" + urllib.parse.urlencode(params)

        req = urllib.request.Request(url, method=method)
        for k, v in headers.items():
            req.add_header(k, v)

        if method in ("POST", "PUT", "PATCH") and params:
            req.data = json.dumps(params).encode("utf-8")
            req.add_header("Content-Type", "application/json")

        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))

        # Apply response_map if defined
        response_map = execution.get("response_map", {})
        if response_map:
            return _apply_response_map(resp_data, response_map)

        return resp_data

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP error ({e.code}): {error_body[:500]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Connection error: {e.reason}")


# ── CODE EXECUTION ────────────────────────────────────────────────────────────

# Safe modules that code skills are allowed to import
ALLOWED_MODULES = {
    "re", "json", "math", "datetime", "collections", "itertools",
    "functools", "string", "textwrap", "decimal", "fractions",
    "statistics", "random", "hashlib", "base64", "csv", "io",
}

# Dangerous modules blocked from code execution
BLOCKED_MODULES = {
    "os", "sys", "subprocess", "shutil", "socket", "http", "urllib",
    "requests", "pathlib", "pty", "shlex", "pickle", "marshal",
    "shelve", "ftplib", "telnetlib", "xmlrpc", "ctypes", "signal",
}


def _run_code(skill: dict, inputs: dict) -> dict:
    """Run a code-type skill in a restricted environment."""
    import ast

    execution = skill["execution"]
    code_str = execution.get("code", "")

    if not code_str.strip():
        raise ValueError("Code skill has empty code block")

    # Step 1: Static analysis — scan for dangerous imports
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        raise ValueError(f"Syntax error in skill code: {e}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in BLOCKED_MODULES:
                    raise SecurityError(f"Blocked import: '{alias.name}' — this module is not allowed in code skills")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                if root in BLOCKED_MODULES:
                    raise SecurityError(f"Blocked import: '{node.module}' — this module is not allowed in code skills")

    # Step 2: Build restricted builtins
    safe_builtins = {
        "len": len, "range": range, "str": str, "int": int, "float": float,
        "list": list, "dict": dict, "set": set, "tuple": tuple, "bool": bool,
        "sorted": sorted, "enumerate": enumerate, "zip": zip, "map": map,
        "filter": filter, "reversed": reversed,
        "min": min, "max": max, "sum": sum, "abs": abs, "round": round,
        "isinstance": isinstance, "type": type, "hasattr": hasattr,
        "True": True, "False": False, "None": None,
        "print": lambda *a, **k: None,  # no-op print
        "ValueError": ValueError, "TypeError": TypeError, "KeyError": KeyError,
        "__import__": _safe_import,
    }

    restricted_globals = {"__builtins__": safe_builtins}

    # Step 3: Execute the code
    try:
        exec(compile(code_str, "<skill>", "exec"), restricted_globals)
    except Exception as e:
        raise RuntimeError(f"Error executing skill code: {e}")

    run_fn = restricted_globals.get("run")
    if not run_fn:
        raise ValueError("Code skill must define a 'run(inputs)' function")

    # Step 4: Call the run function
    try:
        result = run_fn(inputs)
    except Exception as e:
        raise RuntimeError(f"Error in skill run() function: {e}")

    if not isinstance(result, dict):
        raise ValueError(f"run() must return a dict, got {type(result).__name__}")

    return result


def _safe_import(name, *args, **kwargs):
    """Restricted import that only allows safe modules."""
    root = name.split(".")[0]
    if root in BLOCKED_MODULES:
        raise ImportError(f"Import of '{name}' is blocked in code skills")
    if root not in ALLOWED_MODULES:
        raise ImportError(f"Import of '{name}' is not allowed. Allowed: {', '.join(sorted(ALLOWED_MODULES))}")
    return __builtins__["__import__"](name, *args, **kwargs) if isinstance(__builtins__, dict) else __import__(name, *args, **kwargs)


class SecurityError(Exception):
    """Raised when a security check fails."""
    pass


# ── CHAIN EXECUTION ───────────────────────────────────────────────────────────

def _run_chain(skill: dict, inputs: dict, dry_run: bool) -> dict:
    """Run a chain-type skill (currently shows chain info only)."""
    execution = skill["execution"]
    steps = execution.get("steps", [])
    dependencies = skill.get("dependencies", [])

    step_info = []
    for i, step in enumerate(steps, 1):
        input_map = step.get("input_map", {})
        resolved_inputs = {}
        for k, v in input_map.items():
            if isinstance(v, str):
                resolved_inputs[k] = _resolve_template_refs(v, inputs)
            else:
                resolved_inputs[k] = v

        step_info.append({
            "step": i,
            "skill": step.get("skill", "unknown"),
            "output_as": step.get("output_as", f"step_{i}"),
            "inputs": resolved_inputs,
            "condition": step.get("condition", None),
        })

    return {
        "_mode": "chain-info",
        "_note": "Chain execution engine is not yet implemented. This shows the planned execution flow.",
        "total_steps": len(steps),
        "dependencies": [d.get("id", "?") for d in dependencies],
        "steps": step_info,
    }


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _resolve_refs(text: str, inputs: dict) -> str:
    """Replace {input_name} and {env.VAR_NAME} in a string."""
    if not isinstance(text, str):
        return text

    # Replace {env.VAR_NAME} with environment variable values
    def env_replacer(match):
        var_name = match.group(1)
        value = os.environ.get(var_name, "")
        if not value:
            return f"<{var_name} not set>"
        return value

    text = re.sub(r"\{env\.(\w+)\}", env_replacer, text)

    # Replace {input_name} with input values
    for key, value in inputs.items():
        text = text.replace(f"{{{key}}}", str(value))

    return text


def _resolve_template_refs(text: str, inputs: dict) -> str:
    """Resolve template references like {text} against inputs. Leave unresolved refs as-is."""
    if not isinstance(text, str):
        return str(text)
    for key, value in inputs.items():
        text = text.replace(f"{{{key}}}", str(value))
    return text


def _parse_output(raw_output: str, parser_type: str) -> dict:
    """Parse LLM output based on the parser type."""
    if parser_type == "none" or parser_type is None:
        return {"raw_output": raw_output}

    if parser_type == "json":
        # Attempt 1: Direct parse
        try:
            parsed = json.loads(raw_output)
            return parsed if isinstance(parsed, dict) else {"result": parsed}
        except json.JSONDecodeError:
            pass

        # Attempt 2: Extract from markdown code block
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_output)
        if match:
            try:
                parsed = json.loads(match.group(1).strip())
                return parsed if isinstance(parsed, dict) else {"result": parsed}
            except json.JSONDecodeError:
                pass

        # Attempt 3: Find first { ... } or [ ... ] block
        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", raw_output)
        if match:
            try:
                parsed = json.loads(match.group(1))
                return parsed if isinstance(parsed, dict) else {"result": parsed}
            except json.JSONDecodeError:
                pass

        # All fallbacks failed
        return {"raw_output": raw_output, "_parse_error": "Could not parse as JSON"}

    if parser_type == "structured":
        # Structured output — return as raw text for now
        return {"raw_output": raw_output}

    return {"raw_output": raw_output}


def _apply_response_map(data: dict, response_map: dict) -> dict:
    """Apply JSONPath-like response mapping to extract fields from API response."""
    result = {}
    for output_name, path in response_map.items():
        result[output_name] = _extract_jsonpath(data, path)
    return result


def _extract_jsonpath(data, path: str):
    """Simple JSONPath extraction (supports $.key.subkey and $.key[0].subkey)."""
    if not path.startswith("$."):
        return None

    parts = path[2:]  # Remove "$."
    current = data

    for part in re.split(r"\.(?![^\[]*\])", parts):
        if current is None:
            return None

        # Handle array index: key[0]
        array_match = re.match(r"(\w+)\[(\d+)\]", part)
        if array_match:
            key, index = array_match.group(1), int(array_match.group(2))
            if isinstance(current, dict) and key in current:
                current = current[key]
                if isinstance(current, list) and index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None
        else:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

    return current
