"""Benchmark enhanced quantum-inspired algorithm on CEC2017.

Usage:
    python -m benchmarks.run_cec2017_enhanced [n_seeds] [n_functions] [dimension]

Example:
    python -m benchmarks.run_cec2017_enhanced 10 3 10  # 10 seeds, 3 functions, 10D
"""

import sys
import json
from pathlib import Path

from benchmarks.harness import BenchmarkHarness
from benchmarks.baselines.ga import GeneticAlgorithm
from benchmarks.baselines.pso import ParticleSwarmOptimization
from benchmarks.baselines.quantum_inspired import QuantumInspiredBaseline
from benchmarks.baselines.quantum_inspired_enhanced import EnhancedQuantumInspiredBaseline
from benchmarks.suites.cec2017 import CEC2017Suite


def main(n_seeds: int = 10, n_functions: int = 3, dimension: int = 10):
    """Run benchmarks.

    Args:
        n_seeds: Number of random seeds (default: 10)
        n_functions: Number of CEC2017 functions to test (default: 3)
        dimension: Problem dimensionality (default: 10)
    """
    print(f"Benchmarking CEC2017: {n_functions} functions, {dimension}D, {n_seeds} seeds")
    print()

    # Create harness (strict=False to skip validation issues)
    harness = BenchmarkHarness(CEC2017Suite(), strict=False)
    suite = CEC2017Suite()

    # Get functions (skip F2)
    function_ids = [1, 3, 4, 5, 6][:n_functions]
    functions = [
        suite.get_function(fid, dimension) for fid in function_ids
    ]

    # Algorithm configuration
    algorithms = {
        "GA": GeneticAlgorithm(pop_size=100, generations=1000),
        "PSO": ParticleSwarmOptimization(n_particles=50, generations=1000),
        "QIEA": QuantumInspiredBaseline(n_compartments=5, generations=1000),
        "QIEA-Enhanced": EnhancedQuantumInspiredBaseline(
            n_compartments=5, generations=1000, bits_per_dim=8, use_progressive=True
        ),
    }

    # Run benchmarks
    results = []
    for i, func in enumerate(functions, 1):
        print(f"[{i}/{len(functions)}] {func.name} (F{func.id}/{dimension}D)")

        for alg_name, alg in algorithms.items():
            print(f"  {alg_name}...", end=" ", flush=True)

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

            print(f"mean={stats['mean']:.2e}, best={stats['best']:.2e}")

        print()

    # Export results
    output_dir = Path("benchmarks") / "results"
    output_dir.mkdir(exist_ok=True)

    # JSON export
    output_file = (
        output_dir / f"cec2017_{dimension}d_{n_seeds}seeds.json"
    )
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {output_file}")

    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY BY ALGORITHM")
    print("=" * 70)

    for alg_name in algorithms.keys():
        alg_results = [r for r in results if r["algorithm"] == alg_name]
        mean_error = sum(r["error_mean"] for r in alg_results) / len(alg_results)
        best_error = min(r["error_mean"] for r in alg_results)
        print(f"{alg_name:20s}: mean_error={mean_error:10.2e}, best_error={best_error:10.2e}")


if __name__ == "__main__":
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    n_functions = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    dimension = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    main(n_seeds=n_seeds, n_functions=n_functions, dimension=dimension)
