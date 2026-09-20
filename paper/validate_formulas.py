"""
Formula validation and index generation.

Validates that all {{formula:id}} references in presentation.md
actually exist in model.py, and generates a formula index with
full traceability information.
"""

import importlib.util
import re
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("model", "model.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def extract_formula_references(markdown_path: str) -> dict:
    """Extract all {{formula:id}} and {{formula:id|params}} references.

    Returns dict: {formula_id: [(line_num, full_match), ...]}
    """
    references = {}

    with open(markdown_path) as f:
        for line_num, line in enumerate(f, 1):
            matches = re.finditer(r"\{\{formula:([a-zA-Z0-9_]+)(?:\|([^}]*))?\}\}", line)
            for match in matches:
                formula_id = match.group(1)
                params_str = match.group(2)

                if formula_id not in references:
                    references[formula_id] = []

                references[formula_id].append((line_num, match.group(0), params_str))

    return references


def validate_formulas(references: dict, formulas_dict: dict) -> tuple[bool, list]:
    """Validate that all references exist in formulas.

    Returns: (success: bool, errors: list[str])
    """
    errors = []

    for formula_id, occurrences in references.items():
        if formula_id not in formulas_dict:
            for line_num, full_match, _ in occurrences:
                errors.append(
                    f"Line {line_num}: Formula '{formula_id}' not found.\n"
                    f"  Match: {full_match}\n"
                    f"  Available formulas: {', '.join(sorted(formulas_dict.keys()))}"
                )

    return len(errors) == 0, errors


def get_sympy_version() -> str:
    """Get installed SymPy version."""
    import sympy as sp

    return sp.__version__


def generate_formula_index(formulas_dict: dict, references: dict, output_path: str = "formula_index.md") -> bool:
    """Generate formula index with full traceability.

    Creates a Markdown file (formula_index.md) listing:
    - All formulas with source, LaTeX, parameters, assumptions
    - SymPy version used for rendering
    - Usage map (which slides use which formulas)
    """
    sympy_version = get_sympy_version()

    # Build the index
    lines = [
        "# Formula Index",
        "",
        "*Auto-generated from model.py via validate_formulas.py*",
        f"*SymPy Version: {sympy_version}*",
        "",
        "## All Formulas",
        "",
        "| ID | Source | LaTeX | Parameters | Assumptions | Rendering Options |",
        "|----|----|----|----|----|----|",
    ]

    # Add each formula as a row
    for formula_id in sorted(formulas_dict.keys()):
        formula = formulas_dict[formula_id]
        params = ", ".join(formula.parameters.keys()) if formula.parameters else "—"
        assumptions = str(formula.assumptions) if formula.assumptions else "—"
        rendering = str(formula.rendering_opts)

        lines.append(
            f"| `{formula_id}` | model.py:{formula.source_line} | "
            f"`{formula.to_latex()}` | {params} | {assumptions} | {rendering} |"
        )

    # Add usage map
    lines.extend(
        [
            "",
            "## Usage Map",
            "",
            "| Formula ID | Used In | Line(s) |",
            "|---|---|---|",
        ]
    )

    for formula_id in sorted(references.keys()):
        occurrences = references[formula_id]
        line_nums = ", ".join(str(line_num) for line_num, _, _ in occurrences)
        lines.append(f"| `{formula_id}` | presentation.md | {line_nums} |")

    # Write to file
    index_content = "\n".join(lines)
    Path(output_path).write_text(index_content)
    return True


def main(strict: bool = False) -> bool:
    """Validate formulas and generate index.

    Args:
        strict: If True, fail if any formulas are unused

    Returns:
        True if validation passes, False otherwise
    """
    print("🔍 Validating formulas...\n")

    # Load formulas from model.py
    formulas_dict = {formula.id: formula for formula in model.FORMULAS.values()}
    print(f"📦 Loaded {len(formulas_dict)} formulas from model.py")

    # Extract references from presentation.md
    references = extract_formula_references("presentation.md")
    print(f"📍 Found {len(references)} formula references in presentation.md")

    # Validate
    success, errors = validate_formulas(references, formulas_dict)

    if errors:
        print("\n❌ Validation failed:\n")
        for error in errors:
            print(error)
        return False

    # Check for unused formulas (warning, not failure)
    unused = set(formulas_dict.keys()) - set(references.keys())
    if unused:
        print(f"\n⚠️  Unused formulas: {', '.join(sorted(unused))}")
        if strict:
            print("   (Strict mode: failing)")
            return False
        print("   (OK in normal mode)")

    # Generate index
    print("\n📋 Generating formula index...")
    if generate_formula_index(formulas_dict, references):
        print("✅ Generated formula_index.md")
    else:
        print("❌ Failed to generate formula_index.md")
        return False

    print("\n✅ All formulas valid and consistent")
    return True


if __name__ == "__main__":
    strict_mode = "--strict" in sys.argv
    success = main(strict=strict_mode)
    sys.exit(0 if success else 1)
