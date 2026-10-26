"""Tests for compare_results: a run's table against the committed artifact, within a tolerance.

Each test writes two small CSV tables and changes one thing, then checks which check reports it.
"""

from pathlib import Path

from benchmarks.reproducibility import compare_results

HEADER = "function,algorithm,mean,std,best"
FUNCTION = "F1: Bent Cigar"


def _write(path: Path, *rows: str) -> Path:
    path.write_text("\n".join((HEADER, *rows)) + "\n", encoding="utf-8")
    return path


def _committed(tmp_path: Path, *rows: str) -> Path:
    return _write(tmp_path / "committed.csv", *rows)


def _run(tmp_path: Path, *rows: str) -> Path:
    return _write(tmp_path / "run.csv", *rows)


def _named(checks, name: str):
    return [check for check in checks if check.name == name]


def test_value_within_tolerance_passes(tmp_path: Path) -> None:
    """A metric 4% above the committed value passes the 5% relative tolerance."""
    committed = _committed(tmp_path, f"{FUNCTION},GA,100.0,1.0,90.0")
    run = _run(tmp_path, f"{FUNCTION},GA,104.0,1.0,90.0")

    checks = compare_results(run, committed)

    mean = [c for c in _named(checks, "within_tolerance") if ".mean:" in c.detail]
    assert len(mean) == 1
    assert mean[0].passed


def test_value_exactly_at_tolerance_passes(tmp_path: Path) -> None:
    """A metric exactly 5% above the committed value is on the limit, which passes."""
    committed = _committed(tmp_path, f"{FUNCTION},GA,100.0,1.0,90.0")
    run = _run(tmp_path, f"{FUNCTION},GA,105.0,1.0,90.0")

    checks = compare_results(run, committed)

    assert all(c.passed for c in _named(checks, "within_tolerance"))


def test_value_just_outside_tolerance_fails_with_both_values(tmp_path: Path) -> None:
    """A metric 6% above the committed value fails, and the message names the metric and both values."""
    committed = _committed(tmp_path, f"{FUNCTION},GA,100.0,1.0,90.0")
    run = _run(tmp_path, f"{FUNCTION},GA,106.0,1.0,90.0")

    checks = compare_results(run, committed)

    failed = [c for c in _named(checks, "within_tolerance") if not c.passed]
    assert len(failed) == 1
    assert f"{FUNCTION}/GA.mean" in failed[0].detail
    assert "actual 106.0" in failed[0].detail
    assert "committed 100.0" in failed[0].detail


def test_negative_deviation_uses_committed_magnitude(tmp_path: Path) -> None:
    """A value 6% below a negative committed value fails: the tolerance is relative to |committed|."""
    committed = _committed(tmp_path, f"{FUNCTION},GA,-100.0,1.0,90.0")
    run = _run(tmp_path, f"{FUNCTION},GA,-94.0,1.0,90.0")

    checks = compare_results(run, committed)

    assert any(not c.passed for c in _named(checks, "within_tolerance") if ".mean:" in c.detail)


def test_zero_baseline_uses_absolute_tolerance(tmp_path: Path) -> None:
    """A zero committed value passes within the absolute limit and fails beyond it, never dividing by zero."""
    committed = _committed(tmp_path, f"{FUNCTION},GA,0.0,0.0,0.0")
    near = _write(tmp_path / "near.csv", f"{FUNCTION},GA,0.04,0.0,0.0")
    far = _write(tmp_path / "far.csv", f"{FUNCTION},GA,0.06,0.0,0.0")

    assert all(c.passed for c in _named(compare_results(near, committed), "within_tolerance"))

    failed = [c for c in _named(compare_results(far, committed), "within_tolerance") if not c.passed]
    assert len(failed) == 1
    assert "committed value is zero" in failed[0].detail


def test_missing_metric_column_fails(tmp_path: Path) -> None:
    """A run without a committed metric column fails metric_present for each row, naming the metric."""
    committed = _committed(tmp_path, f"{FUNCTION},GA,100.0,1.0,90.0")
    run = tmp_path / "run.csv"
    run.write_text(f"function,algorithm,mean,best\n{FUNCTION},GA,100.0,90.0\n", encoding="utf-8")

    checks = compare_results(run, committed)

    missing = [c for c in _named(checks, "metric_present") if not c.passed]
    assert len(missing) == 1
    assert f"{FUNCTION}/GA.std" in missing[0].detail


def test_missing_row_fails(tmp_path: Path) -> None:
    """A committed (function, algorithm) pair absent from the run fails metric_present."""
    committed = _committed(tmp_path, f"{FUNCTION},GA,100.0,1.0,90.0")
    run = _run(tmp_path)

    checks = compare_results(run, committed)

    missing = [c for c in _named(checks, "metric_present") if not c.passed]
    assert len(missing) == 1
    assert "row missing from the run" in missing[0].detail


def test_unexpected_row_fails_run_rows(tmp_path: Path) -> None:
    """A run row with a pair the committed artifact does not have fails run_rows."""
    committed = _committed(tmp_path, f"{FUNCTION},GA,100.0,1.0,90.0")
    run = _run(tmp_path, f"{FUNCTION},GA,100.0,1.0,90.0", f"{FUNCTION},PSO,100.0,1.0,90.0")

    checks = compare_results(run, committed)

    rows = _named(checks, "run_rows")
    assert len(rows) == 1
    assert not rows[0].passed
    assert "unexpected" in rows[0].detail


def test_non_numeric_committed_field_is_skipped_not_passed(tmp_path: Path) -> None:
    """A committed metric that is not a number is reported as skipped, and is not counted as passed."""
    committed = _committed(tmp_path, f"{FUNCTION},GA,n/a,1.0,90.0")
    run = _run(tmp_path, f"{FUNCTION},GA,100.0,1.0,90.0")

    checks = compare_results(run, committed)

    skipped = _named(checks, "numeric_metric")
    assert len(skipped) == 1
    assert skipped[0].skipped
    assert not skipped[0].passed
    assert f"{FUNCTION}/GA.mean" in skipped[0].detail
    assert not [c for c in _named(checks, "within_tolerance") if ".mean:" in c.detail]


def test_non_numeric_run_value_fails(tmp_path: Path) -> None:
    """A run value that is not a number fails within_tolerance, because it cannot be compared."""
    committed = _committed(tmp_path, f"{FUNCTION},GA,100.0,1.0,90.0")
    run = _run(tmp_path, f"{FUNCTION},GA,oops,1.0,90.0")

    checks = compare_results(run, committed)

    failed = [c for c in _named(checks, "within_tolerance") if not c.passed]
    assert len(failed) == 1
    assert "not a finite number" in failed[0].detail


def test_unreadable_run_fails_results_readable(tmp_path: Path) -> None:
    """A run file that does not exist fails results_readable instead of raising."""
    committed = _committed(tmp_path, f"{FUNCTION},GA,100.0,1.0,90.0")

    checks = compare_results(tmp_path / "absent.csv", committed)

    assert len(checks) == 1
    assert checks[0].name == "results_readable"
    assert not checks[0].passed
