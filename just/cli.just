# Auto-generated Justfile from Typer CLI introspection
set shell := ["bash", "-c"]

# Default recipe
default:
	@just --list

# Run a built-in membrane simulation to completion.
run *args:
	uv run python -m malta.cli.main run {{args}}

# Run toy problem benchmarks (sphere, Rastrigin, Rosenbrock, Ackley).
benchmark-toy *args:
	uv run python -m malta.cli.main benchmark toy {{args}}

# Run CEC2017 benchmarks with quantum-inspired algorithm.
benchmark-cec2017 *args:
	uv run python -m malta.cli.main benchmark cec2017 {{args}}
