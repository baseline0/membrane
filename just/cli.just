# Auto-generated Justfile from Typer CLI introspection
set shell := ["bash", "-c"]

# Default recipe
default:
	@just --list

# Run a built-in membrane simulation to completion.
run *args:
	uv run python -m malta.cli.main run {{args}}
