"""
P-Systems & Membrane Computing: From Biology to Algorithms

This is the SOURCE OF TRUTH for all formulas and examples in the paper.
All formulas are defined symbolically in SymPy and exported to Typst.

Gheorghe Păun's P-systems formalize membrane computing using:
1. Hierarchical membrane structure (μ)
2. Multisets of objects (chemical molecules)
3. Evolution rules (chemical reactions)
4. Maximal parallelism (all applicable rules fire simultaneously)

This model captures the essence of computation-by-membrane-reaction,
from simple multiplication (3 × 2 = 6) to complex optimization algorithms.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import sympy as sp

# === Formula metadata class ===


@dataclass
class Formula:
    """A formula with metadata for traceability."""

    name: str
    expr: sp.Expr
    description: str
    source_line: int

    def to_latex(self) -> str:
        """Convert SymPy expression to LaTeX string."""
        return sp.latex(self.expr)

    def to_dict(self) -> dict:
        """Export as dictionary for JSON serialization."""
        return {
            "latex": self.to_latex(),
            "sympy": str(self.expr),
            "description": self.description,
            "source_line": self.source_line,
        }


# === Symbol definitions for P-System formalism ===

# Core P-system symbols
n = sp.Symbol("n", integer=True, positive=True)  # Number of objects (molecule count)
m = sp.Symbol("m", integer=True, positive=True)  # Number of distinct object types
k = sp.Symbol("k", integer=True, positive=True)  # Step/iteration counter
r = sp.Symbol("r", integer=True, positive=True)  # Rule index

# Membrane structure: depth d (levels of nesting)
d = sp.Symbol("d", integer=True, positive=True)

# Computational complexity
t = sp.Symbol("t", integer=True, positive=True)  # Time (number of steps)

# The Multiplication Example: 3 × 2 = 6
# Input: three 'a' objects
initial_a = sp.Integer(3)

# Rule 1: a → b b (each 'a' becomes two 'b's)
# After step 1: 3 × 2 = 6 'b' objects
rule1_output = initial_a * 2

# Rule 2: b → c (each 'b' becomes one 'c' and exits membrane)
# After step 2: 6 'c' objects in output membrane
final_c = rule1_output

# === Core P-System Formulas ===

FORMULAS = {
    # === 1. Membrane Structure ===
    "membrane_hierarchy": Formula(
        name="membrane_hierarchy",
        expr=sp.Integer(2) ** d,  # 2^d possible nested structures with d levels
        description="Maximum hierarchical depth in a P-system with d membrane levels",
        source_line=59,
    ),
    # === 2. Multiset Operations ===
    "multiset_cardinality": Formula(
        name="multiset_cardinality",
        expr=sp.binomial(n + m - 1, m),  # Stars and bars: distributing n objects among m types
        description="Number of distinct multisets with n objects distributed among m types",
        source_line=66,
    ),
    # === 3. Evolution Rules & Parallelism ===
    "max_rules_per_step": Formula(
        name="max_rules_per_step",
        expr=n,  # In maximal parallelism, at most n rules fire (one per object)
        description="Maximum number of rules that can fire simultaneously in maximal parallelism (upper bound: n)",
        source_line=73,
    ),
    # === 4. The Multiplication Example (3 × 2) ===
    "mult_example_input": Formula(
        name="mult_example_input",
        expr=initial_a,
        description="Multiplication example: input count (three 'a' objects = 3)",
        source_line=80,
    ),
    "mult_example_step1": Formula(
        name="mult_example_step1",
        expr=rule1_output,
        description="Multiplication example: Step 1 output (Rule 1: a → bb, produces 3 × 2 = 6 b's)",
        source_line=85,
    ),
    "mult_example_final": Formula(
        name="mult_example_final",
        expr=final_c,
        description="Multiplication example: final output (Rule 2: b → c_out, produces 6 c's in output membrane)",
        source_line=90,
    ),
    # === 5. Computational Complexity ===
    "time_complexity_exponential": Formula(
        name="time_complexity_exponential",
        expr=2**t,  # Potential exponential speedup with parallelism
        description="Theoretical computational power: O(2^t) with exponential parallelism over t steps",
        source_line=97,
    ),
    "objects_created_per_step": Formula(
        name="objects_created_per_step",
        expr=n * 2,  # Each of n objects can create up to 2 new objects per step
        description="Maximum objects created in one step (conservative bound: 2n)",
        source_line=103,
    ),
}


def export_json(output_path="qips_equations.json"):
    """Export formulas as JSON for build pipeline."""
    data = {name: formula.to_dict() for name, formula in FORMULAS.items()}
    Path(output_path).write_text(json.dumps(data, indent=2))
    return data


if __name__ == "__main__":
    export_json()
    print("✅ Exported qips_equations.json")
    if FORMULAS:
        print("\nFormulas:")
        for name, formula in FORMULAS.items():
            print(f"  {name}: {formula.to_latex()}")
    else:
        print("\n⚠️  No formulas defined yet. Complete literature review and update FORMULAS dict.")
