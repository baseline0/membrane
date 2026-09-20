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
from dataclasses import dataclass, field
from pathlib import Path

import sympy as sp

# === Formula metadata class ===


@dataclass
class Formula:
    """A formula with metadata for traceability.

    Supports deterministic rendering with locked SymPy options,
    symbol aliasing (display names), and assumption locking.
    """

    id: str
    name: str
    expr: sp.Expr
    description: str
    source_line: int
    parameters: dict = field(default_factory=dict)
    # NEW: Locked rendering options for reproducibility
    rendering_opts: dict = field(
        default_factory=lambda: {
            "mode": "plain",
            "fold_short_frac": False,
            "mul_symbol": "cdot",
        }
    )
    # NEW: Symbol display mapping (code name → LaTeX display)
    symbols: dict = field(default_factory=dict)  # e.g., {"n": r"\theta"}
    # NEW: Locked assumptions per symbol
    assumptions: dict = field(default_factory=dict)  # e.g., {"n": {"positive": True}}

    def to_latex(self) -> str:
        """Convert to LaTeX with locked rendering options.

        Applies SymPy assumptions and renders with deterministic settings
        for reproducibility across versions.
        """
        expr = self.expr

        # Apply assumptions to symbols
        if self.assumptions:
            expr_dict = {}
            for sym_name, sym_assumptions in self.assumptions.items():
                expr_dict[sym_name] = sp.Symbol(sym_name, **sym_assumptions)
            # Simple substitution (works for most cases)
            for orig, assumed in expr_dict.items():
                if hasattr(expr, "subs"):
                    expr = expr.subs(sp.Symbol(orig), assumed)

        # Render with locked options
        latex_str = sp.latex(expr, **self.rendering_opts)

        # Apply symbol display mapping (e.g., n → \theta)
        for code_name, display_latex in self.symbols.items():
            latex_str = latex_str.replace(code_name, display_latex)

        return latex_str

    def to_dict(self) -> dict:
        """Export as dictionary for JSON serialization."""
        return {
            "id": self.id,
            "latex": self.to_latex(),
            "sympy": str(self.expr),
            "description": self.description,
            "source_line": self.source_line,
            "parameters": list(self.parameters.keys()),
            "rendering_opts": self.rendering_opts,
            "symbols": self.symbols,
            "assumptions": self.assumptions,
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
        id="membrane_hierarchy",
        name="membrane_hierarchy",
        expr=sp.Integer(2) ** d,
        description="Maximum hierarchical depth in a P-system with d membrane levels",
        parameters={"d": d},
        assumptions={"d": {"positive": True, "integer": True}},
        source_line=82,
    ),
    # === 2. Multiset Operations ===
    "multiset_cardinality": Formula(
        id="multiset_cardinality",
        name="multiset_cardinality",
        expr=sp.binomial(n + m - 1, m),
        description="Number of distinct multisets with n objects distributed among m types",
        parameters={"n": n, "m": m},
        assumptions={"n": {"positive": True, "integer": True}, "m": {"positive": True, "integer": True}},
        source_line=90,
    ),
    # === 3. Evolution Rules & Parallelism ===
    "max_rules_per_step": Formula(
        id="max_rules_per_step",
        name="max_rules_per_step",
        expr=n,
        description="Maximum number of rules that can fire simultaneously in maximal parallelism",
        parameters={"n": n},
        assumptions={"n": {"positive": True, "integer": True}},
        source_line=98,
    ),
    # === 4. The Multiplication Example (3 × 2) ===
    "mult_input": Formula(
        id="mult_input",
        name="mult_input",
        expr=initial_a,
        description="Multiplication example: input count (three 'a' objects)",
        source_line=106,
    ),
    "mult_rule1": Formula(
        id="mult_rule1",
        name="mult_rule1",
        expr=sp.Lambda((n,), 2 * n),
        description="Rule 1: a → bb (multiply by 2)",
        parameters={"n": n},
        assumptions={"n": {"positive": True, "integer": True}},
        source_line=113,
    ),
    "mult_step1_output": Formula(
        id="mult_step1_output",
        name="mult_step1_output",
        expr=rule1_output,
        description="Multiplication example: Step 1 output (3 × 2 = 6)",
        source_line=120,
    ),
    "mult_final": Formula(
        id="mult_final",
        name="mult_final",
        expr=final_c,
        description="Multiplication example: final output (6 c's in output membrane)",
        source_line=127,
    ),
    # === 5. Computational Complexity ===
    "time_complexity": Formula(
        id="time_complexity",
        name="time_complexity",
        expr=2**t,
        description="Theoretical computational power: O(2^t) with exponential parallelism",
        parameters={"t": t},
        assumptions={"t": {"positive": True, "integer": True}},
        source_line=134,
    ),
    "objects_per_step": Formula(
        id="objects_per_step",
        name="objects_per_step",
        expr=n * 2,
        description="Maximum objects created in one step (conservative bound: 2n)",
        parameters={"n": n},
        assumptions={"n": {"positive": True, "integer": True}},
        source_line=141,
    ),
}


def export_json(output_path="qips_equations.json"):
    """Export formulas as JSON for build pipeline."""
    data = {formula.id: formula.to_dict() for formula in FORMULAS.values()}
    Path(output_path).write_text(json.dumps(data, indent=2))
    return data


if __name__ == "__main__":
    export_json()
    print("✅ Exported qips_equations.json")
    if FORMULAS:
        print("\nFormulas:")
        for formula in FORMULAS.values():
            print(f"  {formula.id}: {formula.to_latex()}")
    else:
        print("\n⚠️  No formulas defined yet. Complete literature review and update FORMULAS dict.")
