from typing import Annotated

import typer

from malta.cli.benchmark import benchmark_app
from malta.cli.dev import dev_app
from malta.psystem.engine import run as run_psystem
from malta.psystem.examples import EXAMPLES

MAX_STEPS = 10

app = typer.Typer(name="malta", help="Membrane-computing (P System) simulation CLI.")

app.add_typer(dev_app, name="dev")
app.add_typer(benchmark_app, name="benchmark")


@app.command("run")
def run(
    idx: Annotated[
        int,
        typer.Option("--idx", help="Which built-in example to run (1-4)."),
    ],
    seed: Annotated[
        int,
        typer.Option(
            "--seed", help="Seed for the random examples (3, 4) and the run's choices. The same seed repeats the run."
        ),
    ],
) -> None:
    """Run a built-in P system to completion on the v1 engine."""
    if idx not in EXAMPLES:
        raise typer.BadParameter(f"--idx must be one of {sorted(EXAMPLES)}, got {idx}")
    system = EXAMPLES[idx]() if idx <= 2 else EXAMPLES[idx](seed)
    result = run_psystem(system, seed=seed, max_steps=MAX_STEPS)
    typer.echo(f"status={result.status.value} steps={result.steps}")
    for name, contents in sorted(result.final.items()):
        if contents:
            typer.echo(f"{name}: {' '.join(f'{s}^{n}' for s, n in sorted(contents.items()))}")


if __name__ == "__main__":
    app()
