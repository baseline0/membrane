# Top-level manually curated Justfile

import 'just/repo-push.just'

import 'just/fleet-clean.just'

set default-list := true

# Never let a plain `uv run` rewrite uv.lock; lock changes must be explicit (uv lock / uv sync)
export UV_FROZEN := "1"

# Shared recipes from fleet-agents (includes ci-check for shift-left validation)
import "just/mod.just"
import 'just/fleet-checks.just'
import 'just/fleet-commit.just'
import 'just/fleet-test.just'

# --- Development ---

# Run unit tests only (fast, safe to run frequently) with timing of slowest 5
# Note: shared.just provides the base test-unit recipe; override here if needed
_membrane-test-unit:
    uv run pytest tests/unit -m unit -v --durations=5

# Run integration tests (slower, tests component interactions)
# Note: shared.just provides the base test-integration recipe; override here if needed
_membrane-test-integration:
    uv run pytest tests/integration -m integration -v --durations=5

# Install the pre-commit git hook (run once per clone)
pre-commit-install:
    uv run pre-commit install

# Run pre-commit hooks (ruff + basic hygiene checks) against all files
pre-commit:
    uv run pre-commit run --all-files

# Print tree with file/line counts (respects .gitignore)
tree:
    @uv run python scripts/dev/tree_with_stats.py

# Regenerate just/cli.just by introspecting the Typer CLI
gen-just:
    uv run malta dev gen-just --output just/cli.just

# --- Benchmarking Demo ---

# Quick and full runs write to scratch/bench, so they never replace the tracked benchmarks_example.csv artifact.

# Run example benchmark: 3 seeds, 5 functions, 10D (fast demo)
bench-example:
    BENCH_OUT_DIR=scratch/bench uv run python -m benchmarks.run_example 3 5 10

# Run quick benchmark: 10 seeds, 10 functions, 30D (medium)
bench-quick:
    BENCH_OUT_DIR=scratch/bench uv run python -m benchmarks.run_example 10 10 30

# Run full benchmark: 30 seeds, all 29 functions, 10D (slow, ~1 hour)
bench-full:
    @echo "Running full CEC2017 benchmark (expect 1-2 hours)..."
    BENCH_OUT_DIR=scratch/bench uv run python -m benchmarks.run_example 30 29 10

# The reproducible run. Called inside the experiment container (infrastructure/scripts/lxc/run-experiment.sh),
# where the working directory is a git archive of the pinned commit. Writes out/ with the CSV and its manifest.
bench-experiment SEEDS FUNCTIONS DIM:
    BENCH_OUT_DIR=out uv run python -m benchmarks.run_example {{SEEDS}} {{FUNCTIONS}} {{DIM}}
    uv run python -m benchmarks.reproducibility_cli write-manifest --out-dir out

# Collect benchmark metrics for dashboard (parse benchmarks_example.csv)
bench-metrics:
    @echo "Collecting benchmark metrics..."
    uv run python -m benchmarks.collect_results

# Run full benchmark and collect metrics for dashboard
bench-full-metrics: bench-full bench-metrics

# Remove generated artifacts: caches, simulation output, build byproducts
# Renamed from `clean`: removes simulation, output, and trial directories, which are generated results, not caches. The shared clean (fleet-clean.just) removes caches only.
clean-artifacts:
    rm -rf sims/ out/ src/malta/output/ src/malta/sims/ tests/out/ tests/_trial_temp/
    rm -rf .pytest_cache/ .ruff_cache/
    find . -type d -name "__pycache__" -exec rm -r {} +

# --- Benchmarking: C Library Build (local gcc) ---

# Build libcec2017.so (gitignored output; loaded by benchmarks/suites/cec2017.py). Default: the tracked stub.
# CEC2017_SRC=/path/to/"C version" builds the real bound-constrained functions from that directory, for local use only.
# The upstream source and its input_data are not redistributable and are never committed (see c_src/README.md).
build-cec2017:
    #!/usr/bin/env bash
    set -euo pipefail
    command -v gcc >/dev/null 2>&1 || { echo "error: gcc not found on PATH; install a C compiler (e.g. apt install build-essential)" >&2; exit 1; }
    dir=src/benchmarks/c_src/cec2017
    if [ -z "${CEC2017_SRC:-}" ]; then
        echo "Building CEC2017 stub library with gcc..."
        gcc -O2 -fPIC -shared "$dir/cec17_test_func.c" -o "$dir/libcec2017.so" -lm
        echo "libcec2017.so built from the tracked stub"
        exit 0
    fi
    [ -f "$CEC2017_SRC/cec17_test_func.cpp" ] || { echo "error: CEC2017_SRC has no cec17_test_func.cpp: $CEC2017_SRC" >&2; exit 1; }
    tmp="$(mktemp -d)"
    trap 'rm -rf "$tmp"' EXIT
    # Two Linux fixes, both named in the upstream readme: drop the <WINDOWS.H> include Linux lacks, and read doubles with
    # %lf, not %Lf (long double), which otherwise writes the wrong width into the double arrays and gives inf.
    sed -e 's|#include <WINDOWS.H>|/* WINDOWS.H not needed on Linux */|' -e 's|%Lf|%lf|g' "$CEC2017_SRC/cec17_test_func.cpp" > "$tmp/cec17_upstream.cpp"
    g++ -O2 -fPIC -Dcec17_test_func=cec17_upstream_impl -c "$tmp/cec17_upstream.cpp" -o "$tmp/upstream.o"
    g++ -O2 -fPIC -c "$dir/cec17_shim.cpp" -o "$tmp/shim.o"
    g++ -shared -o "$dir/libcec2017.so" "$tmp/upstream.o" "$tmp/shim.o" -lm
    mkdir -p "$dir/input_data"
    cp "$CEC2017_SRC"/input_data/* "$dir/input_data/"
    echo "libcec2017.so built from CEC2017_SRC: local use only, not for redistribution"

# Generate the interactive demo visualizations into generated/visualization/ (gitignored)
@demo-visualizations:
    uv run python -m benchmarks.visualization.demo

# Pyright ratchet: fails when a file gains errors (scripts in fleet-base; mode from pyproject.toml).
check-types:
    fleet ratchet --action check

# Unit tests only (what CI and the pre-push gate run). Self-contained: depends on no other recipe.
test-unit:
    #!/usr/bin/env bash
    set -euo pipefail
    if uv run pytest --version >/dev/null 2>&1; then
        uv run pytest -m unit --tb=short -v
        exit 0
    fi
    echo "error: test-unit cannot run in this repo: install pytest as a dev dependency (uv add --dev pytest)" >&2
    exit 1

# Run tests
test: test-unit

# Host tests: use real git, so they run on the host, never in the git-free container.
test-host:
    uv run pytest tests/host -q

# ============================================================================
# Shared fleet recipes, run by fleet-base's installed tool (run `just -f ~/projects/fleet-base/justfile install-fleet`; ADR-020).
# Each line calls `fleet recipe NAME`; define a recipe here instead to override it.
# ============================================================================

# Fix failing tests via aider (auto-detect and fix)
aider-fix:
    fleet recipe --name aider-fix

# Implement a feature or task via aider
aider-implement *ARGS:
    fleet recipe --name aider-implement {{ARGS}}

check-pre-commit:
    fleet recipe --name check-pre-commit

# Mypy variant, only when pyproject.toml configures it. Named apart from common.just check-types (pyright).
check-types-mypy:
    fleet recipe --name check-types-mypy

check-unit-tests:
    fleet recipe --name check-unit-tests

check-workflows:
    fleet recipe --name check-workflows

# GitHub CI will run full validation including actionlint and pre-commit hooks.
ci-check:
    fleet recipe --name ci-check

# Check formatting and lint without modifying files (CI-equivalent)
fmt-check:
    fleet recipe --name fmt-check

# Workflow discipline: reminder to run ci-check before push
pre-push-reminder:
    fleet recipe --name pre-push-reminder

# Regenerate uv.lock from pyproject.toml. The uv-lock-check hook only checks; run this to fix a stale lock.
lock:
    uv lock

# Format and fix lint in place. Pre-commit only checks; this is the one place that writes formatting.
fmt:
    git ls-files -z -- '*.py' | xargs -0 -r uv run ruff format
    git ls-files -z -- '*.py' | xargs -0 -r uv run ruff check --fix
