from pathlib import Path
from typing import Annotated

import typer

dev_app = typer.Typer(help="Developer workflow commands.")


@dev_app.command("gen-just")
def generate_justfile(
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Path where generated Justfile recipes will be saved.",
        ),
    ] = Path("just/cli.just"),
) -> None:
    """Regenerate Justfile recipes by introspecting Typer commands."""
    # Deferred import avoids a circular import during app setup.
    from malta.cli.introspect import typer_to_justfile
    from malta.cli.main import app

    output.parent.mkdir(parents=True, exist_ok=True)
    typer_to_justfile(app, output)

    typer.echo(f"Successfully generated Justfile recipes -> {output}")
