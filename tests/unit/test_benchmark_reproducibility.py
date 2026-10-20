"""Reproducibility contract for benchmark artifacts (schema v2): the manifest, its validator, and the CLI.

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
    parse_siblings,
    report,
    validate,
    write_manifest,
)
from benchmarks.reproducibility_cli import app

ENVIRONMENT = {"python": "3.13.16", "numpy": "2.5.3", "scipy": "1.18.1", "pandas": "3.0.5"}
EXECUTION = {
    "image": "test-runner-313",
    "image_fingerprint": "64fb379940c2bde4504e1c4e289dd6d88244aa3c1654fc84336636389e262c84",
    "network": "provision-only",
}
FUNCTIONS = ("F1: Bent Cigar", "F3: Rosenbrock")
ALGORITHMS = ("GA", "PSO")
MANIFEST_NAME = "benchmarks_example.manifest.json"
SIBLING_SHA = "82c05b33e1127eee28f24aafe1b13b28b7277903"


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


def _init_repo(path: Path) -> str:
    """Create a git repository with one commit. Returns its HEAD."""
    path.mkdir(parents=True)
    _git(path, "init", "-q")
    (path / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(path, "add", "README.md")
    _git(path, "commit", "-q", "-m", "fixture")
    return _git(path, "rev-parse", "HEAD")


def _ensure_sibling(path: Path) -> str:
    """The sibling repository at path, created on first use. Returns its HEAD."""
    if path.exists():
        return _git(path, "rev-parse", "HEAD")
    return _init_repo(path)


def make_run(
    root: Path,
    *,
    n_seeds: int = 30,
    method: str = "git-archive",
    commit: str | None = None,
    siblings: dict[str, str] | None = None,
    sibling_paths: dict[str, str] | None = None,
    network: str = "provision-only",
    rows=None,
) -> Path:
    """Build a repository with one artifact and its manifest. Returns the manifest path.

    By default the single sibling is a git repository at root.parent / "sibling", recorded by relative path
    "../sibling" and pinned at its current HEAD.
    """
    head = _init_repo(root)

    if siblings is None:
        siblings = {"sibling": _ensure_sibling(root.parent / "sibling")}
    if sibling_paths is None:
        sibling_paths = dict.fromkeys(siblings, "../sibling")

    csv_path = root / "benchmarks_example.csv"
    _write_csv(csv_path, rows if rows is not None else _rows())
    manifest = build_manifest(
        csv_path=csv_path,
        commit=commit or head,
        siblings=siblings,
        sibling_paths=sibling_paths,
        execution={**EXECUTION, "network": network},
        command=["just", "bench-experiment", str(n_seeds), "2", "10"],
        n_seeds=n_seeds,
        n_functions=len(FUNCTIONS),
        dimension=10,
        algorithms=list(ALGORITHMS),
        functions=list(FUNCTIONS),
        environment=ENVIRONMENT,
        created_at="2026-10-13T00:00:00+00:00",
    )
    if method != "git-archive":
        manifest["source"]["method"] = method
    manifest_path = root / MANIFEST_NAME
    write_manifest(manifest_path, manifest)
    return manifest_path


def _failed(checks) -> set[str]:
    return {c.name for c in checks if not c.passed}


class TestValidArtifact:
    """A complete, archived, consistent artifact passes every check."""

    def test_every_check_passes(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")

        checks = validate(manifest, repo_root=tmp_path / "run")

        assert _failed(checks) == set()
        assert {c.name for c in checks} >= {"schema", "required_fields", "artifact_sha256", "source_archived"}

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

    def test_a_schema_v1_manifest_is_rejected(self, tmp_path: Path):
        """v1 manifests described a clean working tree, which v2 no longer accepts as evidence."""
        manifest = make_run(tmp_path / "run")
        data = json.loads(manifest.read_text())
        data["schema"] = "membrane.benchmark-run/1"
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


class TestSourceAndExecution:
    """The result must come from an archived, known commit, with its execution environment recorded."""

    def test_a_working_tree_source_fails(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", method="working-tree")

        assert _failed(validate(manifest, repo_root=tmp_path / "run")) == {"source_archived"}

    def test_a_commit_missing_from_the_repository_is_stale(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", commit="0" * 40)

        assert _failed(validate(manifest, repo_root=tmp_path / "run")) == {"source_known"}

    def test_a_sibling_that_is_not_a_full_sha_fails(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", siblings={"sibling": "main"})

        assert "source_siblings" in _failed(validate(manifest, repo_root=tmp_path / "run"))

    def test_an_unknown_network_policy_fails(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", network="open")

        assert _failed(validate(manifest, repo_root=tmp_path / "run")) == {"execution_recorded"}

    def test_no_siblings_is_valid(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", siblings={})

        assert _failed(validate(manifest, repo_root=tmp_path / "run")) == set()


class TestSiblingRepositories:
    """Each sibling is a repository at its recorded path, at the pinned SHA; an absent one is skipped, not passed."""

    def test_a_sibling_at_the_pinned_sha_passes(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")

        checks = validate(manifest, repo_root=tmp_path / "run")

        assert _failed(checks) == set()
        sibling = next(c for c in checks if c.name == "sibling_sha")
        assert sibling.passed and not sibling.skipped

    def test_a_stale_sibling_sha_fails_and_names_the_sibling(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")
        _git(tmp_path / "sibling", "commit", "-q", "--allow-empty", "-m", "newer")

        checks = validate(manifest, repo_root=tmp_path / "run")

        assert _failed(checks) == {"sibling_sha"}
        assert "sibling sibling" in next(c for c in checks if c.name == "sibling_sha").detail

    def test_a_missing_sibling_is_skipped_with_its_reason(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", sibling_paths={"sibling": "../absent"})

        checks = validate(manifest, repo_root=tmp_path / "run")

        sibling = next(c for c in checks if c.name == "sibling_sha")
        assert sibling.skipped and not sibling.passed
        assert "not present on this machine" in sibling.detail
        assert _failed(checks) == {"sibling_sha"}
        assert report(checks)["passed"] is False

    def test_a_sibling_without_a_recorded_path_fails(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", sibling_paths={})

        checks = validate(manifest, repo_root=tmp_path / "run")

        assert _failed(checks) == {"sibling_sha"}
        assert "no path recorded" in next(c for c in checks if c.name == "sibling_sha").detail

    def test_an_absolute_sibling_path_is_refused(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", sibling_paths={"sibling": str(tmp_path / "sibling")})

        assert _failed(validate(manifest, repo_root=tmp_path / "run")) == {"sibling_sha"}


class TestSiblingParsing:
    """The sibling option is name=sha pairs; anything else fails at the boundary."""

    def test_pairs_parse_into_a_mapping(self):
        assert parse_siblings(f"a={SIBLING_SHA}, b={SIBLING_SHA}") == {"a": SIBLING_SHA, "b": SIBLING_SHA}

    def test_an_empty_spec_means_no_siblings(self):
        assert parse_siblings("") == {}

    def test_an_item_without_a_sha_is_refused(self):
        try:
            parse_siblings("tool-lit-review")
        except ValueError as exc:
            assert "name=sha" in str(exc)
        else:
            raise AssertionError("expected ValueError")


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
            commit=data["source"]["commit"],
            siblings=data["source"]["siblings"],
            sibling_paths=data["source"]["sibling_paths"],
            execution=data["execution"],
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


class TestWriteManifestCommand:
    """The in-container producer: run facts from run.json, source facts from options, output that validates."""

    def _run_dir(self, tmp_path: Path) -> Path:
        out = tmp_path / "out"
        out.mkdir()
        _write_csv(out / "benchmarks_example.csv", _rows())
        (out / "benchmarks_example.run.json").write_text(
            json.dumps(
                {
                    "command": ["python", "-m", "benchmarks.run_example", "30", "2", "10"],
                    "n_seeds": 30,
                    "n_functions": len(FUNCTIONS),
                    "dimension": 10,
                    "algorithms": list(ALGORITHMS),
                    "functions": list(FUNCTIONS),
                }
            ),
            encoding="utf-8",
        )
        return out

    def test_the_written_manifest_validates(self, tmp_path: Path):
        out = self._run_dir(tmp_path)
        repo = tmp_path / "repo"
        make_run(repo)  # provides a real commit for the manifest to name
        commit = _git(repo, "rev-parse", "HEAD")
        sibling_sha = _ensure_sibling(tmp_path / "sibling")
        env = {
            "EXPERIMENT_COMMIT": commit,
            "EXPERIMENT_SIBLINGS": f"sibling={sibling_sha}",
            "EXPERIMENT_SIBLING_PATHS": "sibling=../sibling",
            "EXPERIMENT_IMAGE": "test-runner-313",
            "EXPERIMENT_IMAGE_FINGERPRINT": EXECUTION["image_fingerprint"],
            "EXPERIMENT_NETWORK": "provision-only",
        }

        result = CliRunner().invoke(app, ["write-manifest", "--out-dir", str(out)], env=env)

        assert result.exit_code == 0, result.output
        assert _failed(validate(out / MANIFEST_NAME, repo_root=repo)) == set()


class TestCommandLine:
    """The validator CLI exits 0 when every check passes and 1 when any fails, and prints the report."""

    def test_a_valid_artifact_exits_zero_and_prints_passed(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run")

        result = CliRunner().invoke(
            app, ["validate", "--manifest", str(manifest), "--repo-root", str(tmp_path / "run")]
        )

        assert result.exit_code == 0
        assert json.loads(result.output)["passed"] is True

    def test_a_failing_artifact_exits_one_and_names_the_failure(self, tmp_path: Path):
        manifest = make_run(tmp_path / "run", method="working-tree")

        result = CliRunner().invoke(
            app, ["validate", "--manifest", str(manifest), "--repo-root", str(tmp_path / "run")]
        )

        assert result.exit_code == 1
        failed = [c["name"] for c in json.loads(result.output)["checks"] if not c["passed"]]
        assert failed == ["source_archived"]
