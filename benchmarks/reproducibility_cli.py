"""Command line for benchmark reproducibility: write a manifest, or validate an artifact against one.

    # inside the experiment container, after the run has written its outputs
    uv run python -m benchmarks.reproducibility_cli write-manifest --out-dir out

    # on the host, against the repository the commit belongs to
    uv run python -m benchmarks.reproducibility_cli validate --manifest out/benchmarks_example.manifest.json \\
        --repo-root .

write-manifest takes its source facts from EXPERIMENT_* environment variables, which the experiment runner sets.
validate prints the JSON report to stdout and exits 1 when any check fails.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import typer

from benchmarks.reproducibility import (
    MANIFEST_NAME,
    RUN_CSV_NAME,
    RUN_PARAMS_NAME,
    build_manifest,
    current_environment,
    parse_siblings,
    report,
    validate,
    write_manifest,
)

app = typer.Typer(
    add_completion=False,
    help="Write or validate benchmark reproducibility manifests.",
)


@app.command("validate")
def validate_command(
    manifest: Path = typer.Option(..., help="Path to the artifact's manifest JSON"),
    repo_root: Path = typer.Option(..., help="Repository that must contain the manifest's source commit"),
) -> None:
    """Check one artifact and print the report."""
    result = report(validate(manifest, repo_root=repo_root))
    typer.echo(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise typer.Exit(code=1)


@app.command("write-manifest")
def write_manifest_command(
    out_dir: Path = typer.Option(
        ..., help="Directory holding the run's CSV and run parameters; the manifest goes here"
    ),
    commit: str = typer.Option(..., envvar="EXPERIMENT_COMMIT", help="Commit the run's source was archived from"),
    siblings: str = typer.Option(
        ...,
        envvar="EXPERIMENT_SIBLINGS",
        help="Sibling commits as name=sha pairs, comma-separated; empty when there are none",
    ),
    image: str = typer.Option(..., envvar="EXPERIMENT_IMAGE", help="Container image alias that ran the experiment"),
    image_fingerprint: str = typer.Option(..., envvar="EXPERIMENT_IMAGE_FINGERPRINT", help="Fingerprint of that image"),
    network: str = typer.Option(..., envvar="EXPERIMENT_NETWORK", help="Network policy in force during the run"),
) -> None:
    """Write the reproducibility manifest beside a finished run's CSV."""
    try:
        sibling_pins = parse_siblings(siblings)
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--siblings") from exc

    params = json.loads((out_dir / RUN_PARAMS_NAME).read_text(encoding="utf-8"))
    manifest = build_manifest(
        csv_path=out_dir / RUN_CSV_NAME,
        commit=commit,
        siblings=sibling_pins,
        execution={"image": image, "image_fingerprint": image_fingerprint, "network": network},
        command=params["command"],
        n_seeds=params["n_seeds"],
        n_functions=params["n_functions"],
        dimension=params["dimension"],
        algorithms=params["algorithms"],
        functions=params["functions"],
        environment=current_environment(),
        created_at=datetime.now(UTC).isoformat(),
    )
    write_manifest(out_dir / MANIFEST_NAME, manifest)
    typer.echo(f"wrote {out_dir / MANIFEST_NAME}")


if __name__ == "__main__":
    app()
