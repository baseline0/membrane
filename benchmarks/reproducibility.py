"""Reproducibility contract for benchmark result artifacts (schema v2).

A benchmark CSV is an artifact when a sidecar manifest records how it was produced:

- source: the exact commit of this repository and of each sibling repository it depends on, delivered as a
  `git archive` of that commit. The working tree is never used, so uncommitted edits cannot leak into a result.
- execution: the pinned container image that ran the experiment, and the network policy in force.
- run: the command and its parameters, and the library versions that can change the numbers.
- artifact: the CSV's SHA-256 and row count.

Validation is static. It reads the artifact, its manifest, and the repository history, and never reruns the
benchmark. Determinism is a separate step: rerun the experiment from the same commits and compare artifact hashes.

A check fails with a stable name, so reports can be read by tools:
- manifest_readable, schema, required_fields: the manifest exists, is the known schema, and has every field.
- artifact_exists, artifact_sha256: the file is present and unchanged since the manifest was written.
- source_archived: the source was a git archive, not a working tree.
- source_known: the commit is in this repository. A commit missing from its history means the source is stale.
- source_siblings: every sibling commit is a full 40-character SHA.
- sibling_sha (one per sibling): the sibling's recorded relative path, resolved against this repository's root, is
  a git repository whose HEAD is the pinned SHA. A path absent on this machine is skipped, not passed.
- execution_recorded: the container image fingerprint and the network policy are recorded.
- seed_floor: the run used at least MIN_SEEDS seeds, the statistical minimum for the Wilcoxon comparisons.
- table_columns, table_rows, table_pairs, values_finite: the table has the expected columns, one row per
  (function, algorithm) pair, and finite numbers.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import re
import subprocess
from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from importlib.metadata import version
from itertools import product
from pathlib import Path
from typing import Any

RUN_CSV_NAME = "benchmarks_example.csv"
RUN_PARAMS_NAME = "benchmarks_example.run.json"
MANIFEST_NAME = "benchmarks_example.manifest.json"
MANIFEST_SCHEMA = "membrane.benchmark-run/2"
SOURCE_METHOD = "git-archive"
NETWORK_POLICIES = ("none", "provision-only")
MIN_SEEDS = 30
EXPECTED_COLUMNS = ("function", "algorithm", "mean", "std", "best")
_FULL_SHA = re.compile(r"^[0-9a-f]{40}$")

# Dotted path and expected type for each field the manifest must carry.
REQUIRED_FIELDS: tuple[tuple[str, type], ...] = (
    ("artifact.path", str),
    ("artifact.sha256", str),
    ("artifact.rows", int),
    ("source.method", str),
    ("source.commit", str),
    ("source.siblings", dict),
    ("source.sibling_paths", dict),
    ("execution.image", str),
    ("execution.image_fingerprint", str),
    ("execution.network", str),
    ("run.command", list),
    ("run.n_seeds", int),
    ("run.n_functions", int),
    ("run.dimension", int),
    ("run.algorithms", list),
    ("run.functions", list),
    ("environment.python", str),
    ("environment.numpy", str),
    ("environment.scipy", str),
    ("environment.pandas", str),
    ("created_at", str),
)


@dataclass(frozen=True)
class Check:
    """One named check and what it found."""

    name: str
    passed: bool
    detail: str
    skipped: bool = False  # True when the check could not run here; a skipped check never counts as passed


def sha256_of(path: Path) -> str:
    """SHA-256 of a file, read in blocks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True, check=False)


def current_environment() -> dict[str, str]:
    """Interpreter and library versions that can change a benchmark's numbers."""
    return {
        "python": platform.python_version(),
        "numpy": version("numpy"),
        "scipy": version("scipy"),
        "pandas": version("pandas"),
    }


def _read_table(path: Path) -> tuple[tuple[str, ...], list[list[str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        return (), []
    return tuple(rows[0]), rows[1:]


def parse_siblings(spec: str) -> dict[str, str]:
    """Parse "name=sha,name=sha" into a mapping. An empty spec means no siblings.

    Raises ValueError for an item that is not name=sha, so a typo fails at the boundary.
    """
    siblings: dict[str, str] = {}
    for item in filter(None, (part.strip() for part in spec.split(","))):
        name, sep, sha = item.partition("=")
        if not sep or not name or not sha:
            raise ValueError(f"sibling must be name=sha, got {item!r}")
        siblings[name] = sha
    return siblings


def build_manifest(
    *,
    csv_path: Path,
    commit: str,
    siblings: dict[str, str],
    sibling_paths: dict[str, str],
    execution: dict[str, str],
    command: Iterable[str],
    n_seeds: int,
    n_functions: int,
    dimension: int,
    algorithms: list[str],
    functions: list[str],
    environment: dict[str, str],
    created_at: str,
) -> dict[str, Any]:
    """The manifest for an artifact that already exists at csv_path."""
    _, rows = _read_table(csv_path)
    return {
        "schema": MANIFEST_SCHEMA,
        "created_at": created_at,
        "artifact": {"path": csv_path.name, "sha256": sha256_of(csv_path), "rows": len(rows)},
        "source": {
            "method": SOURCE_METHOD,
            "commit": commit,
            "siblings": dict(siblings),
            "sibling_paths": dict(sibling_paths),
        },
        "execution": dict(execution),
        "run": {
            "command": list(command),
            "n_seeds": n_seeds,
            "n_functions": n_functions,
            "dimension": dimension,
            "algorithms": list(algorithms),
            "functions": list(functions),
        },
        "environment": dict(environment),
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    """Write the manifest as stable, sorted JSON."""
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _lookup(data: dict[str, Any], dotted: str) -> tuple[bool, Any]:
    value: Any = data
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return False, None
        value = value[part]
    return True, value


def _missing_fields(data: dict[str, Any]) -> list[str]:
    missing = []
    for dotted, expected in REQUIRED_FIELDS:
        found, value = _lookup(data, dotted)
        wrong_type = not isinstance(value, expected) or (expected is int and isinstance(value, bool))
        if not found or wrong_type:
            missing.append(dotted)
    return missing


def _commit_exists(repo_root: Path, commit: str) -> bool:
    try:
        result = _git(repo_root, "cat-file", "-e", f"{commit}^{{commit}}")
    except OSError:
        return False
    return result.returncode == 0


def _sibling_check(name: str, sha: str, relative_path: str | None, repo_root: Path) -> Check:
    """Check one sibling: its recorded path, resolved from repo_root, must be a repository at the pinned SHA."""
    if relative_path is None:
        return Check("sibling_sha", False, f"{name}: no path recorded in source.sibling_paths")
    if Path(relative_path).is_absolute():
        return Check("sibling_sha", False, f"{name}: path {relative_path!r} must be relative to the repository root")

    location = (Path(repo_root) / relative_path).resolve()
    if not location.is_dir():
        return Check(
            "sibling_sha",
            False,
            f"{name}: skipped, {location} is not present on this machine",
            skipped=True,
        )
    try:
        result = _git(location, "rev-parse", "HEAD")
    except OSError as exc:
        return Check("sibling_sha", False, f"{name}: cannot run git in {location}: {exc}")
    if result.returncode != 0:
        return Check("sibling_sha", False, f"{name}: {location} is not a git repository")

    head = result.stdout.strip()
    if head != sha:
        return Check("sibling_sha", False, f"sibling {name} is at {head}, manifest pins {sha}")
    return Check("sibling_sha", True, f"sibling {name} is at {sha}")


def _table_checks(artifact_path: Path, run: dict[str, Any], expected_rows: int) -> list[Check]:
    try:
        columns, rows = _read_table(artifact_path)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        return [Check("table_columns", False, f"cannot read the table: {exc}")]

    columns_ok = columns == EXPECTED_COLUMNS
    checks = [
        Check(
            "table_columns",
            columns_ok,
            "columns are " + ",".join(EXPECTED_COLUMNS) if columns_ok else f"found {','.join(columns) or 'no header'}",
        )
    ]
    if not columns_ok:
        return checks

    checks.append(Check("table_rows", len(rows) == expected_rows, f"{len(rows)} rows, manifest says {expected_rows}"))

    expected_pairs = set(product(run["functions"], run["algorithms"]))
    seen = Counter((row[0], row[1]) for row in rows if len(row) >= 2)
    missing = sorted(expected_pairs - set(seen))
    unexpected = sorted(set(seen) - expected_pairs)
    duplicated = sorted(pair for pair, count in seen.items() if count > 1)
    pairs_ok = not (missing or unexpected or duplicated)
    checks.append(
        Check(
            "table_pairs",
            pairs_ok,
            f"{len(expected_pairs)} pairs, each once"
            if pairs_ok
            else f"missing {missing}; unexpected {unexpected}; duplicated {duplicated}",
        )
    )

    bad_values = []
    for row in rows:
        for column, value in zip(columns, row, strict=False):
            if column in ("mean", "std", "best"):
                try:
                    number = float(value)
                except ValueError:
                    bad_values.append(f"{row[0]}/{row[1]}/{column}={value!r}")
                    continue
                if not math.isfinite(number):
                    bad_values.append(f"{row[0]}/{row[1]}/{column}={value}")
    checks.append(
        Check(
            "values_finite",
            not bad_values,
            "all mean, std and best values are finite" if not bad_values else "; ".join(bad_values[:10]),
        )
    )
    return checks


def validate(manifest_path: Path, repo_root: Path) -> list[Check]:
    """Run every check against one artifact. Later checks are skipped when an earlier one makes them meaningless."""
    manifest_path = Path(manifest_path)
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [Check("manifest_readable", False, f"{manifest_path}: {exc}")]

    checks = [Check("manifest_readable", True, str(manifest_path))]
    if not isinstance(data, dict) or data.get("schema") != MANIFEST_SCHEMA:
        found = data.get("schema") if isinstance(data, dict) else type(data).__name__
        return [*checks, Check("schema", False, f"expected {MANIFEST_SCHEMA}, found {found}")]
    checks.append(Check("schema", True, MANIFEST_SCHEMA))

    missing = _missing_fields(data)
    if missing:
        return [*checks, Check("required_fields", False, "missing or mistyped: " + ", ".join(missing))]
    checks.append(Check("required_fields", True, f"{len(REQUIRED_FIELDS)} fields present"))

    artifact = data["artifact"]
    artifact_path = manifest_path.parent / artifact["path"]
    if not artifact_path.is_file():
        return [*checks, Check("artifact_exists", False, f"no file at {artifact_path}")]
    checks.append(Check("artifact_exists", True, str(artifact_path)))

    actual = sha256_of(artifact_path)
    checks.append(
        Check(
            "artifact_sha256",
            actual == artifact["sha256"],
            f"sha256 {actual}" if actual == artifact["sha256"] else f"manifest {artifact['sha256']}, file {actual}",
        )
    )

    source = data["source"]
    archived = source["method"] == SOURCE_METHOD
    checks.append(
        Check(
            "source_archived",
            archived,
            f"source is a {SOURCE_METHOD} of the commit"
            if archived
            else f"source method is {source['method']!r}; results must come from {SOURCE_METHOD}",
        )
    )
    known = _commit_exists(repo_root, source["commit"])
    checks.append(
        Check(
            "source_known",
            known,
            f"commit {source['commit']} is in {repo_root}"
            if known
            else f"commit {source['commit']} not in {repo_root}",
        )
    )
    bad_siblings = sorted(name for name, sha in source["siblings"].items() if not _FULL_SHA.match(str(sha)))
    checks.append(
        Check(
            "source_siblings",
            not bad_siblings,
            f"{len(source['siblings'])} sibling commits pinned"
            if not bad_siblings
            else f"not full commit SHAs: {', '.join(bad_siblings)}",
        )
    )
    sibling_paths = source["sibling_paths"]
    for name, sha in sorted(source["siblings"].items()):
        checks.append(_sibling_check(name, str(sha), sibling_paths.get(name), repo_root))

    execution = data["execution"]
    policy_ok = execution["network"] in NETWORK_POLICIES and bool(execution["image_fingerprint"].strip())
    checks.append(
        Check(
            "execution_recorded",
            policy_ok,
            f"image {execution['image']} {execution['image_fingerprint'][:12]}, network {execution['network']}"
            if policy_ok
            else f"network must be one of {NETWORK_POLICIES}, found {execution['network']!r}; image fingerprint required",
        )
    )

    n_seeds = data["run"]["n_seeds"]
    checks.append(
        Check(
            "seed_floor",
            n_seeds >= MIN_SEEDS,
            f"{n_seeds} seeds" if n_seeds >= MIN_SEEDS else f"{n_seeds} seeds, minimum is {MIN_SEEDS}",
        )
    )

    checks.extend(_table_checks(artifact_path, data["run"], artifact["rows"]))
    return checks


def report(checks: list[Check]) -> dict[str, Any]:
    """The machine-readable result: overall pass, then each check in order. A skipped check is not a pass."""
    return {"passed": all(check.passed for check in checks), "checks": [asdict(check) for check in checks]}
