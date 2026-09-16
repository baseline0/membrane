# Top-level manually curated Justfile

set default-list := true

# Import shared recipes from agent-tooling (fmt, lint, test, check, commit)
import "../agent-tooling/just/shared.just"

import "just/mod.just"

# --- Development ---

# Run unit tests only (fast, safe to run frequently) with timing of slowest 5
test-unit:
    uv run pytest tests/unit -m unit -v --durations=5

# Run integration tests (slower, tests component interactions)
test-integration:
    uv run pytest tests/integration -m integration -v --durations=5

# Install the pre-commit git hook (run once per clone)
pre-commit-install:
    uv run pre-commit install

# Run pre-commit hooks (ruff + basic hygiene checks) against all files
pre-commit:
    uv run pre-commit run --all-files

# Print tree with file/line counts (respects .gitignore)
tree:
    @python scripts/dev/tree_with_stats.py

# Regenerate just/cli.just by introspecting the Typer CLI
gen-just:
    uv run malta dev gen-just

# --- Benchmarking Demo ---

# Run example benchmark: 3 seeds, 5 functions, 10D (fast demo)
bench-example:
    uv run python -m benchmarks.run_example 3 5 10

# Run quick benchmark: 10 seeds, 10 functions, 30D (medium)
bench-quick:
    uv run python -m benchmarks.run_example 10 10 30

# Run full benchmark: 30 seeds, all 29 functions, 10D (slow, ~1 hour)
bench-full:
    @echo "Running full CEC2017 benchmark (expect 1-2 hours)..."
    uv run python -m benchmarks.run_example 30 29 10

# Collect benchmark metrics for dashboard (parse benchmarks_example.csv)
bench-metrics:
    @echo "Collecting benchmark metrics..."
    uv run python -m benchmarks.collect_results

# Run full benchmark and collect metrics for dashboard
bench-full-metrics: bench-full bench-metrics

# Remove generated artifacts: caches, simulation output, build byproducts
clean:
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
