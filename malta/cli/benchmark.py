"""Benchmark and optimization experiment CLI.

Provides reproducible experiment runs with proper seeding and result export.
"""

from typing import Annotated, Optional
from pathlib import Path
import json

import typer

from benchmarks.harness import BenchmarkHarness
from benchmarks.baselines.ga import GeneticAlgorithm
from benchmarks.baselines.pso import ParticleSwarmOptimizer
from benchmarks.baselines.quantum_inspired import QuantumInspiredBaseline
from benchmarks.baselines.quantum_inspired_enhanced import EnhancedQuantumInspiredBaseline
from benchmarks.suites.cec2017 import CEC2017Suite
from benchmarks.toy_benchmark import ToyBenchmark

benchmark_app = typer.Typer(
    name="benchmark",
    help="Run optimization benchmarks on standard test functions.",
)


@benchmark_app.command("toy")
def run_toy_benchmark(
    n_dims: Annotated[
        int,
        typer.Option(help="Problem dimensionality"),
    ] = 2,
    n_generations: Annotated[
        int,
        typer.Option(help="Generations per run"),
    ] = 30,
    output: Annotated[
        Optional[str],
        typer.Option(help="Output JSON file (optional)"),
    ] = None,
) -> None:
    """Run toy problem benchmarks (sphere, Rastrigin, Rosenbrock, Ackley).

    Tests quantum-inspired algorithm on standard functions with convergence tracking.

    Example:
        malta benchmark toy --n-dims 3 --n-generations 50 --output results.json
    """
    typer.echo(f"Running toy benchmarks: {n_dims}D, {n_generations} generations")

    bench = ToyBenchmark(seed=42)
    results = bench.run_suite(n_dims=n_dims, n_generations=n_generations)

    summary = bench.summary()

    typer.echo("\nResults:")
    for func_name, stats in summary.items():
        typer.echo(f"\n{func_name}:")
        typer.echo(f"  Best fitness: {stats['best_fitness']:.6e}")
        typer.echo(f"  Avg fitness:  {stats['avg_fitness']:.6e}")

    if output:
        output_path = Path(output)
        output_data = {
            "metadata": {
                "n_dims": n_dims,
                "n_generations": n_generations,
            },
            "summary": summary,
            "results": [
                {
                    "function": r.function_name,
                    "dimension": r.dimension,
                    "compartments": r.n_compartments,
                    "best_fitness": r.best_fitness,
                    "convergence_history": r.convergence_history,
                }
                for r in results
            ],
        }
        output_path.write_text(json.dumps(output_data, indent=2))
        typer.echo(f"\nResults saved to: {output_path}")


@benchmark_app.command("cec2017")
def run_cec2017_benchmark(
    n_seeds: Annotated[
        int,
        typer.Option(help="Number of random seeds (minimum 30 for statistical rigor, but 10 for quick test)"),
    ] = 10,
    n_functions: Annotated[
        int,
        typer.Option(help="Number of CEC2017 functions to test"),
    ] = 3,
    dimension: Annotated[
        int,
        typer.Option(help="Problem dimensionality"),
    ] = 10,
    output_dir: Annotated[
        Optional[str],
        typer.Option(help="Output directory for results (default: benchmarks/results)"),
    ] = None,
    include_baselines: Annotated[
        bool,
        typer.Option(help="Include GA and PSO baselines (slower)"),
    ] = False,
) -> None:
    """Run CEC2017 benchmarks with quantum-inspired algorithm.

    Tests on subset of CEC2017 functions with statistical analysis.

    Example:
        malta benchmark cec2017 --n-seeds 10 --n-functions 3 --dimension 10

    Note: 30 seeds recommended for statistical rigor (Wilcoxon test).
    Use lower seeds for quick validation during development.
    """
    typer.echo(
        f"Running CEC2017 benchmarks: {n_functions} functions, "
        f"{dimension}D, {n_seeds} seeds"
    )

    # Setup output
    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = Path("benchmarks") / "results"
    out_path.mkdir(parents=True, exist_ok=True)

    # Create harness
    harness = BenchmarkHarness(CEC2017Suite(), strict=False)
    suite = CEC2017Suite()

    # Get functions (skip F2)
    function_ids = [1, 3, 4, 5, 6][:n_functions]
    functions = [suite.get_function(fid, dimension) for fid in function_ids]

    # Algorithm configuration
    algorithms = {
        "QIEA-Enhanced": EnhancedQuantumInspiredBaseline(
            n_compartments=5,
            generations=1000,
            bits_per_dim=8,
            use_progressive=True,
        ),
        "QIEA": QuantumInspiredBaseline(n_compartments=5, generations=1000),
    }

    if include_baselines:
        algorithms.update({
            "GA": GeneticAlgorithm(pop_size=100, generations=1000),
            "PSO": ParticleSwarmOptimizer(pop_size=50, generations=1000),
        })

    # Run benchmarks
    results = []
    for i, func in enumerate(functions, 1):
        typer.echo(f"\n[{i}/{len(functions)}] {func.name} (F{func.id}/{dimension}D)")

        for alg_name, alg in algorithms.items():
            typer.echo(f"  {alg_name}...", nl=False)

            stats = harness.run_algorithm_on_problem(alg, func, n_seeds=n_seeds)

            results.append({
                "function_id": func.id,
                "function_name": func.name,
                "dimension": dimension,
                "algorithm": alg_name,
                "mean": stats["mean"],
                "std": stats["std"],
                "median": stats["median"],
                "best": stats["best"],
                "worst": stats["worst"],
                "error_mean": stats["error_mean"],
            })

            typer.echo(
                f" mean={stats['mean']:.2e}, best={stats['best']:.2e}"
            )

    # Export results
    output_file = out_path / f"cec2017_{dimension}d_{n_seeds}seeds.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    typer.echo(f"\nResults saved to: {output_file}")

    # Summary statistics
    typer.echo("\n" + "=" * 70)
    typer.echo("SUMMARY BY ALGORITHM")
    typer.echo("=" * 70)

    for alg_name in algorithms.keys():
        alg_results = [r for r in results if r["algorithm"] == alg_name]
        if alg_results:
            mean_error = sum(r["error_mean"] for r in alg_results) / len(alg_results)
            best_error = min(r["error_mean"] for r in alg_results)
            typer.echo(
                f"{alg_name:20s}: mean_error={mean_error:10.2e}, "
                f"best_error={best_error:10.2e}"
            )
