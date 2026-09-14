# Malta Architecture: Import Layering + Restructure Plan

## Vision
Enforce clear boundaries between CLI, services, core simulation, and I/O so that as benchmarks scale and regulatory requirements tighten, the codebase remains composable and testable without importing internals.

---

## Part A: Malta Restructure (Concrete File Moves)

### Current Layout
```
malta/
├── cli/
│   ├── main.py
│   ├── dev.py
│   └── introspect.py
├── config/
├── core/              ← NOT YET: simulation logic scattered at root
├── dot.py (253L)      ← graphical output
├── environment.py (144L)
├── factory.py (120L)  ← high-level ops
├── membrane.py
├── membrane_item.py
├── mmultiset.py
├── multiset_treenode.py (488L)
├── rule.py
├── ruleset.py
├── simulation.py (669L)
├── util.py
└── wip.py
```

### Proposed Layout
```
malta/
├── __init__.py         ← PUBLIC API ONLY (see section A3)
├── cli/                ← user-facing commands
│   ├── __init__.py
│   ├── main.py
│   ├── dev.py
│   └── introspect.py
├── services/           ← high-level orchestration
│   ├── __init__.py
│   └── factory.py      ← SimulationFactory.get_sim1/2/3/4
├── core/               ← simulation engine (private)
│   ├── __init__.py
│   ├── environment.py
│   ├── membrane.py
│   ├── membrane_item.py
│   ├── rule.py
│   ├── ruleset.py
│   ├── simulation.py
│   └── util.py
├── io/                 ← graphical I/O (private)
│   ├── __init__.py
│   ├── dot.py
│   └── dot_colour.py
├── types/              ← shared data structures
│   ├── __init__.py
│   ├── mmultiset.py
│   └── multiset_treenode.py
├── config/             ← simulation configs
└── examples/           ← example programs
```

### A1: File Moves (git mv for history)
```bash
# Core simulation engine
git mv malta/environment.py malta/core/
git mv malta/membrane.py malta/core/
git mv malta/membrane_item.py malta/core/
git mv malta/rule.py malta/core/
git mv malta/ruleset.py malta/core/
git mv malta/simulation.py malta/core/
git mv malta/util.py malta/core/util.py

# Services layer
mkdir -p malta/services
git mv malta/factory.py malta/services/

# I/O and visualization
mkdir -p malta/io
git mv malta/dot.py malta/io/
git mv malta/dot_colour.py malta/io/

# Shared types
mkdir -p malta/types
git mv malta/mmultiset.py malta/types/
git mv malta/multiset_treenode.py malta/types/
```

### A2: Update Imports in Each Module

**malta/core/environment.py**
```python
# Before: from multiset_treenode import convert_tree_to_membranes
from malta.types.multiset_treenode import convert_tree_to_membranes
```

**malta/core/membrane_item.py**
```python
# Before: from dot_colour import get_rand_colour
from malta.io.dot_colour import get_rand_colour
```

**malta/core/rule.py**
```python
# Before: from util import NameGenerator
from malta.core.util import NameGenerator
```

**malta/core/multiset_treenode.py**
```python
# Before: from mmultiset import MMultiset, make_mmultiset
from malta.types.mmultiset import MMultiset, make_mmultiset
```

**malta/core/simulation.py**
```python
# Before: from multiset_treenode import ...
from malta.types.multiset_treenode import ...
# Before: from dot import ...
from malta.io.dot import ...
```

**malta/services/factory.py**
```python
# Before: from simulation import Simulation, SimulationFactory
from malta.core.simulation import Simulation, SimulationFactory
```

**malta/cli/main.py**
```python
# Before: from simulation import Simulation
from malta.services.factory import SimulationFactory
```

### A3: Public API (`malta/__init__.py`)

Expose **only** what external code (benchmarks, user scripts) should touch:

```python
"""Malta P-System simulator — membrane computing framework."""

from malta.services.factory import SimulationFactory
from malta.core.simulation import Simulation, SimulationFactory

__all__ = [
    "SimulationFactory",
    "Simulation",
]

__version__ = "0.1.0"
```

**Effect:** `from malta import SimulationFactory` works; `from malta.core.simulation import rule` doesn't (ImportError: no such module in `__all__`).

---

## Part B: Import Guard Tool

### B1: Concept

A lightweight Python script (`scripts/dev/check_imports.py`) that validates:
1. CLI layer only imports from services/ (not core/)
2. benchmarks/ only imports from benchmarks/ and public malta API
3. No circular imports
4. No test code in production code

Runs as `just check-imports` before commit.

### B2: Implementation

```python
#!/usr/bin/env python3
"""
Import layer validator: enforces clean architecture boundaries.

Allowed imports by layer:
  malta/cli/          → malta.services, malta.cli, typer
  malta/services/     → malta.core, malta.types, malta.services
  malta/core/         → malta.core, malta.types
  malta/io/           → malta.io, malta.types
  benchmarks/         → benchmarks, scipy, pandas, deap, pyswarm, malta (public API only)
  tests/              → malta, benchmarks, pytest, hypothesis
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
    Rule("malta/io", ["malta.io", "malta.types", "pathlib", "matplotlib", "networkx"]),
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
        # Skip .git, __pycache__, tests/
        if any(part in py_file.parts for part in [".git", "__pycache__"]):
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
```

### B3: Integration

Add to `justfile`:

```just
# Check import layer boundaries
check-imports:
    python scripts/dev/check_imports.py

# Lint: ruff + import check
lint: check-imports
    uv run ruff check malta tests benchmarks
```

Run before every commit:

```bash
just check-imports && git add -A && git commit ...
```

---

## Part C: Timeline & Risk Mitigation

### Phase 1: Dry Run (30 min)
1. Run `check_imports.py` on current code (will fail — that's expected)
2. Review violations to confirm rules are sensible
3. Adjust rules if needed (e.g., allow `malta.io` in `malta.core`? probably not — use dependency injection instead)

### Phase 2: Restructure (1 hr)
1. `mkdir -p malta/{core,services,io,types}`
2. Run the `git mv` commands above
3. Update 15–20 import statements (bulk find-replace, then verify)

### Phase 3: Verify (30 min)
1. `uv run pytest tests/ -v` — all tests green
2. `just check-imports` — clean bill of health
3. `just lint`, `just fmt`

### Risk: Circular Imports
If `malta/io/` needs something from `malta/core/`, we **don't** add a reverse import. Instead, use **dependency injection**:

**Bad:**
```python
# malta/core/simulation.py
from malta.io.dot import render
```

**Good:**
```python
# malta/core/simulation.py
class Simulation:
    def __init__(self, renderer=None):
        self.renderer = renderer or lambda x: None
    
    def visualize(self):
        if self.renderer:
            return self.renderer(self)

# malta/cli/main.py
from malta.io.dot import render
from malta.services.factory import SimulationFactory

sim = SimulationFactory.get_sim1(renderer=render)
```

---

## Part D: Scaling Implications

### Why This Pays Dividends

1. **Regulatory Compliance (Insurance):** When you need to prove malta's decision rules are auditable, you can point to `malta/services/` public API and say "this is the only surface," making it easier to certify.

2. **Benchmarking at Scale:** As you add 10+ benchmark suites, they all import the same public surface, so changes to malta internals don't break them.

3. **Publication:** Your paper can reference `SimulationFactory` and `Simulation` as the stable API, not a list of internal modules.

4. **Testing:** Unit tests for `malta/core/` can mock the renderer; integration tests can use real I/O; benchmarks don't see either.

5. **Onboarding:** New contributors see the layer structure immediately — "CLI talks to services; services talk to core; benchmarks use services."

---

## Part E: Checklist

- [ ] Review rules in `check_imports.py` — does the layer model match your vision?
- [ ] Confirm file moves won't break any downstream CI/notebooks (check git history)
- [ ] Decide: should `malta/io/` import from `malta/core/` (current visualization pattern), or use dependency injection?
- [ ] Decide: is `malta/services/factory.py` the only "orchestrator," or should there be more service modules (e.g., `optimizer.py` for benchmark integration)?
- [ ] After restructure, update `ARCHITECTURE.md` with the new layer diagram

---

## Implementation Ready

Once you approve the rules and layer model, the work is:
1. Run script to validate current code
2. Execute `git mv` commands
3. Find-replace imports in ~15 files
4. Verify tests
5. Commit with message: `refactor(malta): organize into layered architecture (core, services, cli, io)`

No functional changes — pure reorganization for scalability and governance.
