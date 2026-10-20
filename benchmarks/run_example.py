"""Example: Run benchmarks on CEC2017 functions with GA and PSO."""

import json
import os
import sys
from pathlib import Path

from benchmarks.artifact_sidecar import write_sidecar
from benchmarks.baselines.ga import GeneticAlgorithm
from benchmarks.baselines.pso import ParticleSwarmOptimizer
from benchmarks.harness import BenchmarkHarness
from benchmarks.reproducibility import RUN_CSV_NAME, RUN_PARAMS_NAME
from benchmarks.suites.cec2017 import CEC2017Suite


def main(n_seeds: int = 3, n_functions: int = 5, dimension: int = 10):
    """Run example benchmark on subset of CEC2017, writing the CSV and its run parameters.

    The output directory is BENCH_OUT_DIR (default: the current directory). The reproducibility manifest is not
    written here: the experiment runner records the source, the container, and the environment, and
    `benchmarks.reproducibility_cli write-manifest` writes it.
    """
    # Use non-strict mode for quick testing (relaxes statistical rigor requirements)
    strict_mode = n_seeds >= 30
    print(f"Running benchmark: {n_functions} functions, {dimension}D, {n_seeds} seeds per run")
    print(f"Mode: {'strict (publication-ready)' if strict_mode else 'testing (relaxed)'}")
    print("-" * 70)

    suite = CEC2017Suite()
    harness = BenchmarkHarness(suite, strict=strict_mode)

    algorithms = {
        "GA": GeneticAlgorithm(pop_size=100, generations=300),
        "PSO": ParticleSwarmOptimizer(pop_size=50, generations=300),
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

    out_dir = Path(os.environ.get("BENCH_OUT_DIR", "."))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / RUN_CSV_NAME
    harness.export_csv(df, str(out_csv))
    print(f"\n✓ Results exported to {out_csv}")

    params = {
        "command": ["python", "-m", "benchmarks.run_example", str(n_seeds), str(n_functions), str(dimension)],
        "n_seeds": n_seeds,
        "n_functions": len(functions),
        "dimension": dimension,
        "algorithms": list(algorithms),
        "functions": [func.name for func in functions],
    }
    params_path = out_dir / RUN_PARAMS_NAME
    params_path.write_text(json.dumps(params, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_sidecar(params_path)

    return df


if __name__ == "__main__":
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    n_functions = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    dimension = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    main(n_seeds=n_seeds, n_functions=n_functions, dimension=dimension)
