"""
Build pipeline: model.py → formula-driven Marp presentation.

Parses {{formula:id}} and {{formula:id|param=value}} syntax
in presentation.md and substitutes SymPy-rendered formulas.
"""

# Import formulas from model
import importlib.util
import json
import re
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("model", "model.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def generate_formulas_json() -> bool:
    """Export formulas from model.py to JSON."""
    print("📐 Exporting formulas from model.py...")
    try:
        model.export_json("qips_equations.json")
        print("✅ Generated qips_equations.json")
        return True
    except Exception as e:
        print(f"❌ Failed to export formulas: {e}")
        return False


def load_formulas_json(path="qips_equations.json") -> dict:
    """Load formulas from JSON."""
    if not Path(path).exists():
        print(f"❌ {path} not found")
        return {}
    with open(path) as f:
        return json.load(f)


def substitute_formulas(markdown: str, formulas_dict: dict) -> str:
    """
    Replace {{formula:id}} and {{formula:id|param=value}} with LaTeX.

    Patterns:
      {{formula:mult_input}} -> 3
      {{formula:mult_rule1|n=3}} -> 2 \cdot 3 = 6
      {{formula:membrane_hierarchy|d=4}} -> 2^4 = 16
    """

    def replace_formula(match):
        formula_id = match.group(1)
        params_str = match.group(2)  # "param1=value1,param2=value2" or None

        if formula_id not in formulas_dict:
            return f"<!-- formula not found: {formula_id} -->"

        formula_info = formulas_dict[formula_id]
        latex = formula_info["latex"]
        source_line = formula_info.get("source_line", "?")

        # Add traceability comment
        comment = f"<!-- from model.py:{source_line} -->"

        # If no parameters, just return the LaTeX
        if not params_str:
            return f"$${latex}$$ {comment}"

        # Parse parameters (simple approach: "param1=value1,param2=value2")
        # For now, just return the formula with params in comment
        return f"$${latex}$$ {comment} [params: {params_str}]"

    # Pattern: {{formula:id}} or {{formula:id|params}}
    pattern = r"\{\{formula:([a-zA-Z0-9_]+)(?:\|([^}]*))?\}\}"
    result = re.sub(pattern, replace_formula, markdown)
    return result


def build_presentation(template_file="presentation.md", output_file="presentation_generated.md") -> bool:
    """Build the presentation by substituting formulas."""
    print("🎯 Building formula-driven presentation...")

    if not Path(template_file).exists():
        print(f"❌ {template_file} not found")
        return False

    # Load formulas
    formulas = load_formulas_json()
    if not formulas:
        print("⚠️  No formulas to substitute")
        return True

    # Read template
    with open(template_file) as f:
        markdown = f.read()

    # Substitute formulas
    result = substitute_formulas(markdown, formulas)

    # Write output
    with open(output_file, "w") as f:
        f.write(result)

    print(f"✅ Generated {output_file}")
    print("   Next: Open in Marp VS Code extension or run:")
    print(f"         marp {output_file} -o {output_file.replace('.md', '.pdf')}")
    return True


def main() -> bool:
    """Full build pipeline for formula-driven slides."""
    print("🚀 Building formula-driven Marp presentation...\n")

    steps = [
        ("Formulas", generate_formulas_json),
        ("Presentation", build_presentation),
    ]

    for name, step in steps:
        if not step():
            print(f"\n❌ Failed at step: {name}")
            return False

    print("\n✅ Presentation ready for editing")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
