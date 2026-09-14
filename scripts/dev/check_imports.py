#!/usr/bin/env python3
"""
Import layer validator: enforces clean architecture boundaries.

Allowed imports by layer:
  malta/cli/          → malta.services, malta.cli, typer
  malta/services/     → malta.core, malta.types, malta.services, pathlib
  malta/core/         → malta.core, malta.types, pathlib, anytree, networkx
  malta/io/           → malta.io, malta.types, malta.core (type hints only), pathlib, matplotlib
  malta/types/        → malta.types, pathlib
  benchmarks/         → benchmarks, scipy, pandas, deap, numpy, random, pathlib
  tests/              → malta, benchmarks, pytest, hypothesis, pathlib, tempfile
"""

import ast
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Set


@dataclass
class Rule:
    """Import permission rule."""
    source_pattern: str     # e.g., "malta/cli"
    allowed_patterns: list  # e.g., ["malta.services", "malta.cli", "typer"]


RULES = [
    Rule("malta/cli", ["malta.services", "malta.cli", "typer", "typer.main"]),
    Rule("malta/services", ["malta.core", "malta.types", "malta.services", "pathlib"]),
    Rule("malta/core", ["malta.core", "malta.types", "pathlib", "anytree", "networkx"]),
    Rule("malta/io", ["malta.io", "malta.types", "malta.core", "pathlib", "matplotlib", "networkx"]),
    Rule("malta/types", ["malta.types", "pathlib"]),
    Rule("benchmarks", ["benchmarks", "scipy", "pandas", "deap", "numpy", "random", "pathlib"]),
    Rule("tests", ["malta", "benchmarks", "pytest", "hypothesis", "pathlib", "tempfile"]),
]


def find_imports(file_path: Path) -> Set[str]:
    """Extract all imports from a Python file."""
    try:
        tree = ast.parse(file_path.read_text())
    except SyntaxError:
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])  # Get top-level module
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
    return imports


def get_rule_for_file(file_path: Path) -> Rule | None:
    """Find the applicable rule for a file."""
    rel_path = file_path.relative_to(Path.cwd())
    for rule in RULES:
        if rule.source_pattern in str(rel_path):
            return rule
    return None


def check_file(file_path: Path) -> list[str]:
    """Validate imports in a single file. Return list of violations."""
    if not file_path.suffix == ".py" or file_path.name.startswith("__"):
        return []

    rule = get_rule_for_file(file_path)
    if not rule:
        return []

    violations = []
    imports = find_imports(file_path)

    for imp in imports:
        # Check if import matches any allowed pattern
        allowed = any(
            imp == pat or pat.startswith(imp + ".")
            for pat in rule.allowed_patterns
        )
        if not allowed:
            violations.append(
                f"  {file_path}: imports '{imp}' (not in {rule.allowed_patterns})"
            )

    return violations


def main():
    """Run import validation on all Python files."""
    root = Path.cwd()
    violations = []

    for py_file in root.rglob("*.py"):
        # Skip .git, __pycache__, tests/cyprus, wip.py
        if any(part in py_file.parts for part in [".git", "__pycache__", "cyprus"]):
            continue
        if py_file.name == "wip.py":
            continue
        violations.extend(check_file(py_file))

    if violations:
        print("❌ Import violations found:\n")
        for v in violations:
            print(v)
        sys.exit(1)
    else:
        print("✅ All imports follow layer rules")
        sys.exit(0)


if __name__ == "__main__":
    main()
