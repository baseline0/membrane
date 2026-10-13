"""Command line for the benchmark reproducibility validator.

    uv run python -m benchmarks.reproducibility_cli --manifest benchmarks_example.manifest.json --repo-root .

Prints the JSON report to stdout. Exits 0 when every check passes and 1 when any fails.
"""

import json
from pathlib import Path

import typer

from benchmarks.reproducibility import report, validate

app = typer.Typer(
    add_completion=False,
    help="Validate a benchmark artifact against its reproducibility manifest.",
)


@app.command()
def validate_command(
    manifest: Path = typer.Option(..., help="Path to the artifact's manifest JSON"),
    repo_root: Path = typer.Option(..., help="Repository that must contain the manifest's source commit"),
) -> None:
    """Check one artifact and print the report."""
    result = report(validate(manifest, repo_root=repo_root))
    typer.echo(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
