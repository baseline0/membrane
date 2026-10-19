# Top-level manually curated Justfile

import 'just/repo-push.just'

import 'just/fleet-clean.just'

set default-list := true

# Shared recipes from fleet-agents (includes ci-check for shift-left validation)
import "just/mod.just"

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
    rm -rf sims/ out/ malta/output/ malta/sims/ tests/out/ tests/_trial_temp/
    rm -rf .pytest_cache/ .ruff_cache/
    find . -type d -name "__pycache__" -exec rm -r {} +

# --- Benchmarking: C Library Build (Docker) ---

# Build CEC2017 library in Docker (reproducible, isolated)
docker-build-cec2017:
    @echo "Building CEC2017 library in Docker..."
    mkdir -p benchmarks/c_src/cec2017
    cd .. && docker build -t malta-cec2017:latest -f cyprus/Dockerfile . && \
    docker run --rm -v $(pwd)/cyprus/benchmarks/c_src/cec2017:/output malta-cec2017:latest
    @echo "✓ libcec2017.so ready at benchmarks/c_src/cec2017/libcec2017.so"

# Legacy: direct gcc build (requires local gcc, less reproducible)
build-cec2017:
    @echo "Building CEC2017 shared library (direct)..."
    mkdir -p benchmarks/c_src/cec2017
    gcc -shared -fPIC -O3 -lm benchmarks/c_src/cec2017/cec17_test_func.c -o benchmarks/c_src/cec2017/libcec2017.so 2>/dev/null || \
    (echo "Note: gcc build requires cec17_test_func.c in benchmarks/c_src/cec2017/" && exit 1)
    @echo "libcec2017.so built successfully"

# --- Paper & Presentation ---

# Build formula-driven presentation (build slides + validate formulas + generate index)
present:
    @cd paper && \
    echo "🚀 Building formula-driven presentation..." && \
    uv run python model.py && \
    uv run python build_slides.py && \
    uv run python validate_formulas.py && \
    echo "" && \
    echo "✅ Presentation ready!" && \
    echo "   Generated files:" && \
    echo "     - presentation_generated.md (Marp)" && \
    echo "     - formula_index.md (traceability)" && \
    echo "     - qips_equations.json (formulas)" && \
    echo "" && \
    echo "📊 Next: Open in Marp VS Code extension or run:" && \
    echo "   marp presentation_generated.md -o presentation.pdf"

# Generate formula index (verify consistency)
formula-check:
    @cd paper && uv run python validate_formulas.py

# Build paper (Typst) from formulas
paper:
    @cd paper && uv run python build_paper.py

# Render the formula index as a standalone PDF appendix (run formula-check first)
formula-index-pdf:
    @uv run python paper/build_formula_index_pdf.py

# Build everything: paper + presentation + checks
paper-all: paper present
    @echo "✅ All paper artifacts built successfully"

# Display artifact manifest (Artifact Contract v1)
artifacts-list:
    @uv run python scripts/display_artifacts.py

# Generate the interactive demo visualizations into generated/visualization/ (gitignored)
@demo-visualizations:
    uv run python -m benchmarks.visualization.demo

# Pyright ratchet: fails when a file gains errors (scripts in fleet-base; mode from pyproject.toml).
check-types:
    fleet ratchet --action check

# Unit tests: the gate the pre-push hook runs (fleet hook standard, fleet_base.hook_standard R4)
test-unit:
    just check-unit-tests

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

# Falls back to manual commit if Ollama unavailable or commitmate fails
commit:
    fleet recipe --name commit

# Add all untracked files and commit with LLM or custom message
commit-all:
    fleet recipe --name commit-all

# Check formatting and lint without modifying files (CI-equivalent)
fmt-check:
    fleet recipe --name fmt-check

# Workflow discipline: reminder to run ci-check before push
pre-push-reminder:
    fleet recipe --name pre-push-reminder

# Regenerate uv.lock from pyproject.toml. The uv-lock-check hook only checks; run this to fix a stale lock.
lock:
    uv lock
