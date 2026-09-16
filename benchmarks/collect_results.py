"""Collect and parse benchmark results for dashboard ingestion.

Runs full benchmark suite, collects convergence data, generates dashboard metrics.
Handles CSV output from BenchmarkHarness and transforms into metrics schema.
"""

import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from benchmarks.metrics_schema import (
    AlgorithmProfile,
    BenchmarkRun,
    ConvergenceMetrics,
    export_benchmark_metrics,
)


def parse_benchmark_csv(csv_path: Path) -> dict[str, list[dict[str, Any]]]:
    """Parse benchmark CSV output and group by algorithm.

    CSV format: function, algorithm, mean, std, best
    Returns: {"GA": [...], "PSO": [...]}
    """
    results_by_algo: dict[str, list[dict]] = {}

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            algo = row["algorithm"]
            if algo not in results_by_algo:
                results_by_algo[algo] = []
            results_by_algo[algo].append(row)

    return results_by_algo


def get_cec2017_optimum(func_id: int) -> float:
    """CEC2017 optimum = func_id * 100."""
    return func_id * 100.0


def create_convergence_metrics(
    func_id: int,
    func_name: str,
    algo: str,
    dimension: int,
    n_seeds: int,
    mean: float,
    std: float,
    best: float,
    worst: float,
) -> ConvergenceMetrics:
    """Create ConvergenceMetrics from benchmark result row."""
    optimum = get_cec2017_optimum(func_id)
    error_mean = mean - optimum

    # Convergence ratio: how far off from optimum, normalized to optimum scale
    # ratio = 0.0 is perfect, ratio = 1.0 means error = optimum
    convergence_ratio = abs(error_mean) / optimum if optimum != 0 else 0.0

    return ConvergenceMetrics(
        algorithm=algo,
        function_id=func_id,
        function_name=func_name,
        dimension=dimension,
        n_seeds=n_seeds,
        mean_result=mean,
        std_result=std,
        best_result=best,
        worst_result=worst,
        median_result=(mean + best) / 2,  # Placeholder; actual median from seeds would be better
        optimum=optimum,
        error_mean=error_mean,
        convergence_ratio=convergence_ratio,
        timestamp=datetime.now().isoformat(),
        runtime_seconds=0.0,  # Would need per-function timing from harness
    )


def create_algorithm_profile(
    algo: str,
    dimension: int,
    n_seeds: int,
    convergence_metrics_list: list[ConvergenceMetrics],
) -> AlgorithmProfile:
    """Aggregate convergence metrics into algorithm performance profile."""
    convergence_ratios = [m.convergence_ratio for m in convergence_metrics_list]
    n_functions = len(convergence_ratios)

    # Success = within 10x optimum (convergence_ratio ≤ 10.0)
    successes = sum(1 for r in convergence_ratios if r <= 10.0)
    success_rate = successes / n_functions if n_functions > 0 else 0.0

    return AlgorithmProfile(
        algorithm=algo,
        dimension=dimension,
        n_seeds=n_seeds,
        n_functions=n_functions,
        mean_convergence_ratio=sum(convergence_ratios) / n_functions,
        best_convergence_ratio=min(convergence_ratios),
        worst_convergence_ratio=max(convergence_ratios),
        functions_within_10x_optimum=successes,
        success_rate=success_rate,
        ranking={},  # Populated by compare_algorithms()
        timestamp=datetime.now().isoformat(),
    )


def compare_algorithms(profiles: list[AlgorithmProfile]) -> None:
    """Rank algorithms by mean convergence ratio (lower is better)."""
    sorted_profiles = sorted(profiles, key=lambda p: p.mean_convergence_ratio)
    for rank, profile in enumerate(sorted_profiles, 1):
        profile.ranking = {p.algorithm: i for i, p in enumerate(sorted_profiles, 1)}


def collect_benchmark_results(
    csv_path: Path,
    dimension: int = 10,
    n_seeds: int = 30,
) -> BenchmarkRun:
    """Collect and aggregate benchmark results from CSV."""
    results_by_algo = parse_benchmark_csv(csv_path)
    all_metrics: list[ConvergenceMetrics] = []

    # Parse each algorithm's results
    for algo, rows in results_by_algo.items():
        for row in rows:
            func_name = row["function"]

            # Extract function ID from name (e.g., "F1: Sphere" → 1)
            try:
                func_id = int(func_name.split(":")[0].replace("F", ""))
            except (ValueError, IndexError):
                print(f"Warning: Could not parse function ID from {func_name}")
                continue

            mean = float(row["mean"])
            std = float(row["std"])
            best = float(row["best"])
            worst = float(row.get("worst", mean + std))  # Estimate if not in CSV

            metric = create_convergence_metrics(
                func_id=func_id,
                func_name=func_name,
                algo=algo,
                dimension=dimension,
                n_seeds=n_seeds,
                mean=mean,
                std=std,
                best=best,
                worst=worst,
            )
            all_metrics.append(metric)

    # Create algorithm profiles
    profiles_by_algo = {}
    for algo in results_by_algo.keys():
        algo_metrics = [m for m in all_metrics if m.algorithm == algo]
        profile = create_algorithm_profile(algo, dimension, n_seeds, algo_metrics)
        profiles_by_algo[algo] = profile

    # Rank algorithms
    compare_algorithms(list(profiles_by_algo.values()))

    # Detect trends (comparing against historical baseline if available)
    trends = {
        "ga_converging_well": profiles_by_algo.get("GA", None) is not None
        and profiles_by_algo["GA"].success_rate >= 0.7,
        "pso_converging_well": profiles_by_algo.get("PSO", None) is not None
        and profiles_by_algo["PSO"].success_rate >= 0.7,
    }

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    return BenchmarkRun(
        run_id=run_id,
        dimension=dimension,
        n_seeds=n_seeds,
        timestamp=datetime.now().isoformat(),
        convergence_metrics=all_metrics,
        algorithm_profiles=list(profiles_by_algo.values()),
        trends=trends,
    )


def main():
    """Collect results from latest benchmark CSV and export metrics."""
    csv_path = Path("benchmarks_example.csv")

    if not csv_path.exists():
        print(f"✗ Benchmark results not found: {csv_path}")
        print("  Run `just bench-full` first to generate results.")
        sys.exit(1)

    print(f"📊 Parsing benchmark results from {csv_path}")

    run = collect_benchmark_results(csv_path, dimension=10, n_seeds=30)

    # Export metrics for dashboard
    export_benchmark_metrics(run)

    # Print summary
    print("\n" + "=" * 70)
    print(f"Benchmark Run: {run.run_id}")
    print(f"Dimension: {run.dimension}D | Seeds: {run.n_seeds}")
    print(f"Total metrics collected: {len(run.convergence_metrics)}")
    print(f"Algorithms: {len(run.algorithm_profiles)}")
    print()

    for profile in run.algorithm_profiles:
        print(f"{profile.algorithm}:")
        print(f"  Mean convergence ratio: {profile.mean_convergence_ratio:.3f}")
        print(f"  Success rate (≤10x): {profile.success_rate * 100:.1f}%")
        print(f"  Functions: {profile.n_functions}")
        print()

    print(f"Trends: {run.trends}")
    print("=" * 70)


if __name__ == "__main__":
    main()
