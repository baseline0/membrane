"""Reproducibility contract for benchmark artifacts: the manifest, its validator, and the CLI.

Each fixture is a small git repository with a benchmark CSV and a manifest beside it. Each test changes one thing
and checks that exactly the matching check fails, with its name in the report.
"""

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from benchmarks.reproducibility import (
    MIN_SEEDS,
    build_manifest,
    report,
    validate,
    write_manifest,
)
from benchmarks.reproducibility_cli import app

ENVIRONMENT = {"python": "3.13.15", "numpy": "2.2.0", "scipy": "1.15.0", "pandas": "2.2.3"}
FUNCTIONS = ("F1: Bent Cigar", "F3: Rosenbrock")
ALGORITHMS = ("GA", "PSO")
MANIFEST_NAME = "benchmarks_example.manifest.json"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write_csv(path: Path, rows: list[tuple[str, str, float, float, float]]) -> None:
    lines = ["function,algorithm,mean,std,best"]
    lines += [f"{f},{a},{mean},{std},{best}" for f, a, mean, std, best in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _rows(functions=FUNCTIONS, algorithms=ALGORITHMS):
    return [(f, a, 100.0, 0.5, 99.0) for f in functions for a in algorithms]


def make_run(
    root: Path,
    *,
    n_seeds: int = 30,
    dirty: bool = False,
    commit: str | None = None,
    rows=None,
) -> Path:
    """Build a repository with one artifact and its manifest. Returns the manifest path."""
    root.mkdir(parents=True)
    _git(root, "init", "-q")
    (root / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(root, "add", "README.md")
    _git(root, "commit", "-q", "-m", "fixture")
    head = _git(root, "rev-parse", "HEAD")

    csv_path = root / "benchmarks_example.csv"
    _write_csv(csv_path, rows if rows is not None else _rows())
    manifest = build_manifest(
        csv_path=csv_path,
        source={"commit": commit or head, "dirty": dirty},
        command=["python", "-m", "benchmarks.run_example", str(n_seeds), "2", "10"],
        n_seeds=n_seeds,
        n_functions=len(FUNCTIONS),
        dimension=10,
        algorithms=list(ALGORITHMS),
        functions=list(FUNCTIONS),
        environment=ENVIRONMENT,
        created_at="2026-10-13T00:00:00+00:00",
    )
    manifest_path = root / MANIFEST_NAME
    write_manifest(manifest_path, manifest)
    return manifest_path


def _failed(checks) -> set[str]:
    return {c.name for c in checks if not c.passed}


class TestValidArtifact:
    """A complete, clean, consistent artifact passes every check."""

    def test_every_check_passes(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")

        checks = validate(manifest, repo_root=tmp_path / "run")

        assert _failed(checks) == set()
        assert {c.name for c in checks} >= {"schema", "required_fields", "artifact_sha256", "source_clean"}

    def test_the_report_is_byte_identical_for_the_same_inputs(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")

        first = report(validate(manifest, repo_root=tmp_path / "run"))
        second = report(validate(manifest, repo_root=tmp_path / "run"))

        assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
        assert first["passed"] is True


class TestManifestContract:
    """The manifest must say what produced the artifact, in a known schema."""

    def test_a_missing_manifest_fails_with_its_name(self, tmp_path: Path):
        checks = validate(tmp_path / "absent.json", repo_root=tmp_path)

        assert _failed(checks) == {"manifest_readable"}

    def test_an_unknown_schema_is_rejected(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")
        data = json.loads(manifest.read_text())
        data["schema"] = "something-else/9"
        manifest.write_text(json.dumps(data))

        assert _failed(validate(manifest, repo_root=tmp_path / "run")) == {"schema"}

    def test_a_missing_field_is_named_by_its_path(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")
        data = json.loads(manifest.read_text())
        del data["run"]["n_seeds"]
        manifest.write_text(json.dumps(data))

        checks = validate(manifest, repo_root=tmp_path / "run")

        assert _failed(checks) == {"required_fields"}
        assert "run.n_seeds" in next(c for c in checks if c.name == "required_fields").detail


class TestArtifactIntegrity:
    """The artifact on disk must be the one the manifest describes."""

    def test_an_edited_artifact_fails_the_hash_check(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")
        (tmp_path / "run" / "benchmarks_example.csv").write_text("changed\n", encoding="utf-8")

        assert "artifact_sha256" in _failed(validate(manifest, repo_root=tmp_path / "run"))

    def test_a_missing_artifact_fails(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")
        (tmp_path / "run" / "benchmarks_example.csv").unlink()

        assert "artifact_exists" in _failed(validate(manifest, repo_root=tmp_path / "run"))


class TestSourceRevision:
    """The result must come from a clean, known commit."""

    def test_a_dirty_source_tree_fails(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", dirty=True)

        assert _failed(validate(manifest, repo_root=tmp_path / "run")) == {"source_clean"}

    def test_a_commit_missing_from_the_repository_is_stale(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", commit="0" * 40)

        assert _failed(validate(manifest, repo_root=tmp_path / "run")) == {"source_known"}


class TestStatisticalFloor:
    """Claims need at least the statistical minimum of seeds."""

    def test_fewer_seeds_than_the_minimum_fails(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", n_seeds=MIN_SEEDS - 1)

        assert _failed(validate(manifest, repo_root=tmp_path / "run")) == {"seed_floor"}


class TestTableConsistency:
    """Every function and algorithm pair appears exactly once, with finite numbers."""

    def test_a_missing_pair_is_named(self, tmp_path: Path):
        rows = _rows()[:-1]
        manifest = make_run(tmp_path / "run", rows=rows)

        checks = validate(manifest, repo_root=tmp_path / "run")

        assert "table_pairs" in _failed(checks)
        assert "PSO" in next(c for c in checks if c.name == "table_pairs").detail

    def test_a_duplicate_pair_fails(self, tmp_path: Path):
        rows = [*_rows(), _rows()[0]]
        manifest = make_run(tmp_path / "run", rows=rows)

        assert "table_pairs" in _failed(validate(manifest, repo_root=tmp_path / "run"))

    def test_a_non_finite_value_fails(self, tmp_path: Path):
        rows = _rows()
        rows[0] = (rows[0][0], rows[0][1], float("nan"), 0.5, 99.0)
        manifest = make_run(tmp_path / "run", rows=rows)

        assert _failed(validate(manifest, repo_root=tmp_path / "run")) == {"values_finite"}

    def test_wrong_columns_fail_the_table_shape_check(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")
        csv_path = tmp_path / "run" / "benchmarks_example.csv"
        csv_path.write_text("function,algorithm,mean\nF1,GA,1.0\n", encoding="utf-8")
        data = json.loads(manifest.read_text())
        data["artifact"]["sha256"] = build_manifest(
            csv_path=csv_path,
            source=data["source"],
            command=data["run"]["command"],
            n_seeds=30,
            n_functions=2,
            dimension=10,
            algorithms=list(ALGORITHMS),
            functions=list(FUNCTIONS),
            environment=ENVIRONMENT,
            created_at=data["created_at"],
        )["artifact"]["sha256"]
        manifest.write_text(json.dumps(data))

        assert "table_columns" in _failed(validate(manifest, repo_root=tmp_path / "run"))


class TestProducerAndValidatorAgree:
    """A manifest written by the producer is one the validator accepts."""

    def test_write_then_validate_round_trips(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")

        assert validate(manifest, repo_root=tmp_path / "run")
        assert _failed(validate(manifest, repo_root=tmp_path / "run")) == set()


class TestCommandLine:
    """The CLI exits 0 when every check passes and 1 when any fails, and prints the report."""

    def test_a_valid_artifact_exits_zero_and_prints_passed(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")

        result = CliRunner().invoke(app, ["--manifest", str(manifest), "--repo-root", str(tmp_path / "run")])

        assert result.exit_code == 0
        assert json.loads(result.output)["passed"] is True

    def test_a_failing_artifact_exits_one_and_names_the_failure(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", dirty=True)

        result = CliRunner().invoke(app, ["--manifest", str(manifest), "--repo-root", str(tmp_path / "run")])

        assert result.exit_code == 1
        failed = [c["name"] for c in json.loads(result.output)["checks"] if not c["passed"]]
        assert failed == ["source_clean"]
