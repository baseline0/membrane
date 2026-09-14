# Top-level manually curated Justfile

set default-list := true

import "just/mod.just"

# --- Development ---

# Run all test suites
test:
    uv run pytest tests/unit tests/integration tests/e2e --ignore=tests/cyprus -v

# Run unit tests only (fast, safe to run frequently) with timing of slowest 5
test-unit:
    uv run pytest tests/unit -m unit -v --durations=5

# Run integration tests (slower, tests component interactions)
test-integration:
    uv run pytest tests/integration -m integration -v --durations=5

lint:
    uv run ruff check malta tests

fmt:
    uv run ruff format malta tests

# Install the pre-commit git hook (run once per clone)
pre-commit-install:
    uv run pre-commit install

# Run pre-commit hooks (ruff + basic hygiene checks) against all files
pre-commit:
    uv run pre-commit run --all-files

# Regenerate just/cli.just by introspecting the Typer CLI
gen-just:
    uv run malta dev gen-just

# Remove generated artifacts: caches, simulation output, build byproducts
clean:
    rm -rf sims/ out/ malta/output/ malta/sims/ tests/out/ tests/_trial_temp/
    rm -rf .pytest_cache/ .ruff_cache/
    find . -type d -name "__pycache__" -exec rm -r {} +"
