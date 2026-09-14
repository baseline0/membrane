# Top-level manually curated Justfile

set default-list := true

import "just/mod.just"

# --- Development ---

# Run the malta test suite (cyprus/ is a separate, untouched legacy package)
test:
    uv run pytest tests/ --ignore=tests/cyprus -v

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
    find . -type d -name "__pycache__" -exec rm -r {} +
