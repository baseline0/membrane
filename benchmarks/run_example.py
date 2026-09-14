"""Example: Run benchmarks on CEC2017 functions with GA and PSO."""

import sys
from pathlib import Path

from benchmarks.baselines.ga import GeneticAlgorithm
from benchmarks.baselines.pso import ParticleSwarmOptimizer
from benchmarks.harness import BenchmarkHarness
from benchmarks.suites.cec2017 import CEC2017Suite


def main(n_seeds: int = 3, n_functions: int = 5, dimension: int = 10):
    """Run example benchmark on subset of CEC2017."""
    print(f"Running benchmark: {n_functions} functions, {dimension}D, {n_seeds} seeds per run")
    print("-" * 70)

    suite = CEC2017Suite()
    harness = BenchmarkHarness(suite)

    algorithms = {
        "GA": GeneticAlgorithm(pop_size=50, generations=100),
        "PSO": ParticleSwarmOptimizer(pop_size=30, generations=100),
    }

    functions = suite.list_functions(dimension)[:n_functions]

    results = []
    for i, func in enumerate(functions, 1):
        print(f"\n[{i}/{len(functions)}] {func.name}")
        for alg_name, alg in algorithms.items():
            stats = harness.run_algorithm_on_problem(alg, func, n_seeds=n_seeds)
            print(f"  {alg_name:8} → mean={stats['mean']:.2e} std={stats['std']:.2e} best={stats['best']:.2e}")
            results.append(
                {
                    "function": func.name,
                    "algorithm": alg_name,
                    "mean": stats["mean"],
                    "std": stats["std"],
                    "best": stats["best"],
                }
            )

    print("\n" + "=" * 70)
    print("Summary DataFrame:")
    import pandas as pd

    df = pd.DataFrame(results)
    print(df.to_string(index=False))

    out_csv = Path("benchmarks_example.csv")
    harness.export_csv(df, str(out_csv))
    print(f"\n✓ Results exported to {out_csv}")

    return df


if __name__ == "__main__":
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    n_functions = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    dimension = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    main(n_seeds=n_seeds, n_functions=n_functions, dimension=dimension)
