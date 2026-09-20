"""
Formula validation and index generation with hardening checks.

Validates that all {{formula:id}} references in presentation.md
actually exist in model.py, generates a formula index with
full traceability (LaTeX hash, commit hash, SymPy version),
and ensures all symbols have assumptions recorded.
"""

import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("model", "model.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def get_latex_hash(latex_str: str) -> str:
    """Compute SHA256 hash of LaTeX string (first 8 chars for brevity)."""
    return hashlib.sha256(latex_str.encode()).hexdigest()[:8]


def get_commit_hash() -> str:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=".",
        )
        if result.returncode == 0:
            return result.stdout.strip()[:8]
    except Exception:
        pass
    return "unknown"


def validate_symbol_assumptions(formulas_dict: dict) -> list:
    """Validate that all symbols in formulas have assumptions recorded.

    Returns: list of errors (empty if all OK)
    """
    errors = []

    for formula_id, formula in formulas_dict.items():
        # Extract symbols from expression
        expr_symbols = set()
        if hasattr(formula.expr, "free_symbols"):
            expr_symbols = {sym.name for sym in formula.expr.free_symbols}

        # Check each symbol has assumptions
        recorded_symbols = set(formula.assumptions.keys())
        missing = expr_symbols - recorded_symbols

        if missing:
            errors.append(
                f"Formula '{formula_id}': Symbols without assumptions: {', '.join(sorted(missing))}\n"
                f"  (Add to assumptions dict to ensure reproducible rendering)"
            )

    return errors


def extract_formula_references(markdown_path: str) -> dict:
    """Extract all {{formula:id}} and {{formula:id|params}} references.

    Returns dict: {formula_id: [(line_num, full_match, params_str), ...]}
    """
    references = {}

    with open(markdown_path) as f:
        lines_content = f.readlines()

    for line_num, line in enumerate(lines_content, 1):
        matches = re.finditer(r"\{\{formula:([a-zA-Z0-9_]+)(?:\|([^}]*))?\}\}", line)
        for match in matches:
            formula_id = match.group(1)
            params_str = match.group(2)

            if formula_id not in references:
                references[formula_id] = []

            # Store context for error reporting
            context_start = max(0, line_num - 2)
            context_lines = lines_content[context_start:line_num]
            context = "".join(context_lines).strip()

            references[formula_id].append((line_num, match.group(0), params_str, context))

    return references


def validate_formulas(references: dict, formulas_dict: dict) -> tuple[bool, list]:
    """Validate that all references exist in formulas.

    Returns: (success: bool, errors: list[str])
    """
    errors = []

    for formula_id, occurrences in references.items():
        if formula_id not in formulas_dict:
            for line_num, full_match, _, context in occurrences:
                available = ", ".join(sorted(formulas_dict.keys()))
                errors.append(
                    f"❌ presentation.md:{line_num}: Formula '{formula_id}' not found\n"
                    f"   Match: {full_match}\n"
                    f"   Context: {context}\n"
                    f"   Available: {available}\n"
                    f"   Hint: Check spelling or add to model.py"
                )

    return len(errors) == 0, errors


def get_sympy_version() -> str:
    """Get installed SymPy version."""
    import sympy as sp

    return sp.__version__


def generate_formula_index(formulas_dict: dict, references: dict, output_path: str = "formula_index.md") -> bool:
    """Generate formula index with full traceability.

    Creates a Markdown file (formula_index.md) listing:
    - All formulas with source, LaTeX hash, parameters, assumptions
    - SymPy version and commit hash for audit trail
    - Usage map (which slides use which formulas)
    """
    sympy_version = get_sympy_version()
    commit_hash = get_commit_hash()

    # Build the index
    lines = [
        "# Formula Index",
        "",
        "*Auto-generated from model.py via validate_formulas.py*",
        f"*SymPy Version: {sympy_version} | Commit: {commit_hash}*",
        f"*Generated at: {__file__}*",
        "",
        "## All Formulas",
        "",
        "| ID | Source | LaTeX | Hash | Parameters | Assumptions |",
        "|----|----|----|----|----|----|",
    ]

    # Add each formula as a row
    for formula_id in sorted(formulas_dict.keys()):
        formula = formulas_dict[formula_id]
        latex = formula.to_latex()
        latex_hash = get_latex_hash(latex)
        params = ", ".join(formula.parameters.keys()) if formula.parameters else "—"
        assumptions = str(formula.assumptions).replace("{", "").replace("}", "") if formula.assumptions else "—"

        lines.append(
            f"| `{formula_id}` | model.py:{formula.source_line} | "
            f"`{latex}` | `{latex_hash}` | {params} | {assumptions} |"
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
        line_nums = ", ".join(str(line_num) for line_num, _, _, _ in occurrences)
        lines.append(f"| `{formula_id}` | presentation.md | {line_nums} |")

    # Write to file
    index_content = "\n".join(lines)
    Path(output_path).write_text(index_content)
    return True


def main(strict: bool = False) -> bool:
    """Validate formulas and generate index.

    Args:
        strict: If True, fail if any formulas are unused or have missing assumptions

    Returns:
        True if validation passes, False otherwise
    """
    print("🔍 Validating formulas...\n")

    # Load formulas from model.py
    formulas_dict = {formula.id: formula for formula in model.FORMULAS.values()}
    print(f"📦 Loaded {len(formulas_dict)} formulas from model.py")

    # Validate assumptions completeness
    print("✓ Checking symbol assumptions...")
    assumption_errors = validate_symbol_assumptions(formulas_dict)
    if assumption_errors:
        if strict:
            print("\n❌ Assumption validation failed:\n")
            for error in assumption_errors:
                print(error)
            return False
        else:
            print("⚠️  Some formulas have symbols without assumptions:")
            for error in assumption_errors:
                print(f"   {error}")
            print("   (OK in normal mode, but recommended for reproducibility)")

    # Extract references from presentation.md
    references = extract_formula_references("presentation.md")
    print(f"📍 Found {len(references)} formula references in presentation.md")

    # Validate formula references
    print("✓ Validating formula references...")
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
    print(f"✓ SymPy Version: {get_sympy_version()}")
    print(f"✓ Commit: {get_commit_hash()}")
    return True


if __name__ == "__main__":
    strict_mode = "--strict" in sys.argv
    success = main(strict=strict_mode)
    sys.exit(0 if success else 1)
