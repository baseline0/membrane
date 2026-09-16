"""Benchmark metrics schema for dashboard consumption.

Defines the structure of benchmark results that feed into fleet health dashboard:
- Convergence metrics (per-algorithm, per-function)
- Trend data (performance over time, across versions)
- Comparative analysis (GA vs PSO vs future algorithms)
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class ConvergenceMetrics:
    """Per-algorithm convergence on a single function."""

    algorithm: str  # "GA", "PSO", "QuantumInspired", etc.
    function_id: int  # 1-30 for CEC2017
    function_name: str
    dimension: int
    n_seeds: int

    # Summary statistics
    mean_result: float  # Best mean result across all seeds
    std_result: float  # Std dev of results
    best_result: float  # Best result achieved
    worst_result: float
    median_result: float

    # Convergence quality (relative to optimum)
    optimum: float
    error_mean: float  # mean_result - optimum
    convergence_ratio: float  # error_mean / optimum (0.0 = perfect)

    # Metadata
    timestamp: str  # ISO-8601
    runtime_seconds: float

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON export."""
        return asdict(self)


@dataclass
class AlgorithmProfile:
    """Aggregated performance profile for one algorithm across all functions."""

    algorithm: str
    dimension: int
    n_seeds: int
    n_functions: int

    # Aggregate scores
    mean_convergence_ratio: float  # Avg error/optimum (lower is better)
    best_convergence_ratio: float  # Best convergence achieved
    worst_convergence_ratio: float

    # Success rate
    functions_within_10x_optimum: int  # Count of functions converging within 10x
    success_rate: float  # Percentage of functions within 10x

    # Performance ranking
    ranking: dict[str, Any]  # {"GA": 1, "PSO": 2, ...} per dimension

    timestamp: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)


@dataclass
class BenchmarkRun:
    """Complete benchmark run (all algorithms, all functions, one dimension)."""

    run_id: str  # UUID or timestamp
    dimension: int
    n_seeds: int
    timestamp: str

    # Metrics for each algorithm-function pair
    convergence_metrics: list[ConvergenceMetrics]

    # Algorithm profiles (aggregated)
    algorithm_profiles: list[AlgorithmProfile]

    # Trend indicators
    trends: dict[str, Any]  # {"ga_improving": True, "pso_stable": True, ...}

    def to_dict(self) -> dict[str, Any]:
        """Serialize with nested objects."""
        return {
            "run_id": self.run_id,
            "dimension": self.dimension,
            "n_seeds": self.n_seeds,
            "timestamp": self.timestamp,
            "convergence_metrics": [m.to_dict() for m in self.convergence_metrics],
            "algorithm_profiles": [p.to_dict() for p in self.algorithm_profiles],
            "trends": self.trends,
        }


def export_benchmark_metrics(
    run: BenchmarkRun,
    output_dir: Path = Path("benchmarks/metrics"),
) -> None:
    """Export benchmark metrics for dashboard consumption.

    Creates:
    - metrics.json: Full run data
    - algorithm_comparison.json: Side-by-side algorithm comparison
    - convergence_trends.json: Trend analysis per algorithm
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Full metrics
    metrics_file = output_dir / f"metrics_{run.run_id}.json"
    metrics_file.write_text(
        json.dumps(run.to_dict(), indent=2, default=str),
        encoding="utf-8",
    )

    # Algorithm comparison
    comparison = {
        "timestamp": run.timestamp,
        "dimension": run.dimension,
        "n_seeds": run.n_seeds,
        "algorithm_profiles": [p.to_dict() for p in run.algorithm_profiles],
    }
    comparison_file = output_dir / f"comparison_{run.dimension}d.json"
    comparison_file.write_text(
        json.dumps(comparison, indent=2, default=str),
        encoding="utf-8",
    )

    # Convergence trends (per algorithm)
    for algo in set(m.algorithm for m in run.convergence_metrics):
        algo_metrics = [m for m in run.convergence_metrics if m.algorithm == algo]
        trends = {
            "algorithm": algo,
            "timestamp": run.timestamp,
            "dimension": run.dimension,
            "convergence_ratios": [
                {
                    "function_id": m.function_id,
                    "function_name": m.function_name,
                    "convergence_ratio": m.convergence_ratio,
                    "error_mean": m.error_mean,
                }
                for m in sorted(algo_metrics, key=lambda m: m.function_id)
            ],
            "stats": {
                "mean_convergence": sum(m.convergence_ratio for m in algo_metrics) / len(algo_metrics),
                "best_convergence": min(m.convergence_ratio for m in algo_metrics),
                "worst_convergence": max(m.convergence_ratio for m in algo_metrics),
            },
        }
        trends_file = output_dir / f"trends_{algo}_{run.dimension}d.json"
        trends_file.write_text(
            json.dumps(trends, indent=2, default=str),
            encoding="utf-8",
        )

    print(f"✓ Exported metrics to {output_dir}")
    print(f"  - metrics_{run.run_id}.json")
    print(f"  - comparison_{run.dimension}d.json")
    print("  - trends_*.json (per algorithm)")
