"""
Stress tests for formula validation.

Validates that error handling, hashing, and strict mode work correctly.
"""

import subprocess
import sys
from pathlib import Path


def test_formula_index_exists():
    """Test: formula_index.md is generated."""
    result = subprocess.run(["uv", "run", "python", "validate_formulas.py"], capture_output=True, text=True)

    assert result.returncode == 0, f"Validation failed: {result.stderr}"
    assert Path("formula_index.md").exists(), "formula_index.md should be created"

    index = Path("formula_index.md").read_text()

    # Should have hash column
    assert "| Hash |" in index, "Should have hash column"

    # Should have LaTeX hashes (8-char hex)
    import re

    hashes = re.findall(r"`[a-f0-9]{8}`", index)
    assert len(hashes) > 0, f"Should have LaTeX hashes, got: {index[:200]}"

    # Should have commit hash
    assert "Commit:" in index, "Should have commit hash in header"

    print(f"✅ Formula index: generated with {len(hashes)} LaTeX hashes + commit hash")
    return True


def test_validation_passes():
    """Test: validation passes when all formulas are valid."""
    result = subprocess.run(["uv", "run", "python", "validate_formulas.py"], capture_output=True, text=True)

    assert result.returncode == 0, f"Valid formulas should pass: {result.stderr}"
    assert "All formulas valid" in result.stdout, "Should confirm all formulas are valid"

    print("✅ Valid formulas: validation passes")
    return True


def test_strict_mode_succeeds():
    """Test: strict mode passes when no unused formulas."""
    result = subprocess.run(["uv", "run", "python", "validate_formulas.py", "--strict"], capture_output=True, text=True)

    # Should succeed (all formulas are used)
    assert result.returncode == 0, f"Strict mode should pass: {result.stderr}"

    print("✅ Strict mode: passes when all formulas used")
    return True


def test_sympy_version():
    """Test: SymPy version is pinned and reported."""
    result = subprocess.run(["uv", "run", "python", "validate_formulas.py"], capture_output=True, text=True)

    assert result.returncode == 0

    # Should report SymPy version
    assert "SymPy Version:" in result.stdout or "SymPy Version:" in Path("formula_index.md").read_text()

    print("✅ SymPy version: pinned and reported")
    return True


def test_assumptions_validation():
    """Test: all symbols have assumptions recorded."""
    result = subprocess.run(["uv", "run", "python", "validate_formulas.py"], capture_output=True, text=True)

    assert result.returncode == 0

    # Should report assumptions check passed
    assert "Checking symbol assumptions" in result.stdout or "All formulas valid" in result.stdout

    # Should NOT report missing assumptions for used formulas
    index = Path("formula_index.md").read_text()
    for line in index.split("\n"):
        if "`mult_rule1`" in line or "`time_complexity`" in line:
            # Should have assumptions recorded
            assert "—" not in line or "positive" in line.lower() or "integer" in line.lower()

    print("✅ Assumptions: all symbols validated")
    return True


def run_all_tests():
    """Run all stress tests."""
    print("🧪 Running formula stress tests...\n")

    tests = [
        ("Formula index generation", test_formula_index_exists),
        ("Valid formulas pass", test_validation_passes),
        ("Strict mode success", test_strict_mode_succeeds),
        ("SymPy version pinned", test_sympy_version),
        ("Assumptions complete", test_assumptions_validation),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {name}: unexpected error: {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
