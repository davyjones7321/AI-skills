"""
ai-skills SDK — Security Scanner
Provides auditing tools to scan skill files for secrets and dangerous code.
"""

import re
import ast
import yaml
from pathlib import Path
from dataclasses import dataclass, field

# Common secret patterns
SECRET_PATTERNS = {
    "OpenAI API Key": r"sk-[a-zA-Z0-9]{32,}",
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "Stripe Standard Key": r"sk_live_[0-9a-zA-Z]{24}",
    "Generic Bearer Token": r"Bearer\s+(?!{)[a-zA-Z0-9\-\._~+/]+=*",
}

# Dangerous Python built-ins/functions
DANGEROUS_FUNCTIONS = {
    "eval", "exec", "compile", "__import__", "open", "getattr", "setattr",
    "delattr", "globals", "locals"
}

# Dangerous Python modules
DANGEROUS_MODULES = {
    "os", "sys", "subprocess", "pty", "shlex", "socket", "urllib", "requests",
    "http", "ftplib", "telnetlib", "xmlrpc", "pickle", "marshal", "shelve"
}

@dataclass
class AuditResult:
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_safe(self) -> bool:
        return len(self.issues) == 0

    def add_issue(self, msg: str):
        self.issues.append(f"  🚨 DANGER: {msg}")

    def add_warning(self, msg: str):
        self.warnings.append(f"  ⚠️  WARNING: {msg}")


def scan_skill(skill_path: str) -> AuditResult:
    """Scans a skill.yaml file for security risks."""
    result = AuditResult()
    path = Path(skill_path)

    if not path.exists():
        return result

    try:
        with open(path) as f:
            content = f.read()
            data = yaml.safe_load(content)
    except Exception:
        # Invalid YAML is handled by the validator, not the security scanner
        return result

    if not isinstance(data, dict) or "skill" not in data:
        return result

    skill = data["skill"]

    # 1. Scan raw file content for hardcoded secrets
    for name, pattern in SECRET_PATTERNS.items():
        if re.search(pattern, content):
            result.add_issue(f"Hardcoded secret detected: {name} (Use {{env.VAR_NAME}} instead)")

    # 2. Check for missing validation on tool_call execution
    if "execution" in skill and isinstance(skill["execution"], dict):
        exec_config = skill["execution"]
        if exec_config.get("type") == "tool_call":
            if "endpoint" in exec_config:
                url = exec_config["endpoint"].get("url", "")
                if url.startswith("http://") and "localhost" not in url and "127.0.0.1" not in url:
                    result.add_issue(f"Insecure endpoint URL (HTTP instead of HTTPS): {url}")

    # 3. Analyze code execution for dangerous patterns
    if "execution" in skill and isinstance(skill["execution"], dict):
        exec_config = skill["execution"]
        if exec_config.get("type") == "code" and "code" in exec_config:
            _analyze_python_code(exec_config["code"], result)

    return result


def _analyze_python_code(code_str: str, result: AuditResult):
    """Parses and analyzes Python code for dangerous AST nodes."""
    try:
        tree = ast.parse(code_str)
    except SyntaxError:
        result.add_issue("Syntax error in embedded code block")
        return

    for node in ast.walk(tree):
        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split('.')[0]
                if root_module in DANGEROUS_MODULES:
                    result.add_issue(f"Dangerous module import: '{alias.name}'")
        
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_module = node.module.split('.')[0]
                if root_module in DANGEROUS_MODULES:
                    result.add_issue(f"Dangerous from-import: '{node.module}'")
        
        # Check function calls
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in DANGEROUS_FUNCTIONS:
                    result.add_issue(f"Dangerous built-in function call: '{func_name}'")
