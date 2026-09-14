from typing import Annotated

import typer

from malta.cli.dev import dev_app
from malta.simulation import run as run_simulation

app = typer.Typer(name="malta", help="Membrane-computing (P System) simulation CLI.")

app.add_typer(dev_app, name="dev")


@app.command("run")
def run(
    idx: Annotated[
        int,
        typer.Argument(help="Which built-in SimulationFactory example to run (1-4)."),
    ] = 1,
) -> None:
    """Run a built-in membrane simulation to completion."""
    run_simulation(idx)


if __name__ == "__main__":
    app()
