"""Unified benchmark harness: 30-seed runner with Wilcoxon tests and statistical export."""

from collections import defaultdict

import numpy as np
import pandas as pd
from scipy import stats

from benchmarks.suites.base import BenchmarkFunction, BenchmarkSuite


class BenchmarkHarness:
    """Orchestrates 30+ seed experiments with statistical analysis."""

    def __init__(self, suite: BenchmarkSuite):
        self.suite = suite

    def run_single_seed(self, algorithm, problem: BenchmarkFunction, seed: int) -> float:
        """Run one algorithm on one problem with one seed."""
        return algorithm.optimize(problem, seed=seed)

    def run_algorithm_on_problem(self, algorithm, problem: BenchmarkFunction, n_seeds: int = 30) -> dict:
        """Run algorithm on problem for n_seeds times, return statistics."""
        results = [self.run_single_seed(algorithm, problem, seed) for seed in range(n_seeds)]
        results_arr = np.array(results)
        return {
            "mean": float(np.mean(results_arr)),
            "std": float(np.std(results_arr)),
            "median": float(np.median(results_arr)),
            "best": float(np.min(results_arr)),
            "worst": float(np.max(results_arr)),
            "error_mean": float(np.mean(results_arr) - problem.optimum_value),
            "results": results,
        }

    def wilcoxon_test(self, results1: list[float], results2: list[float]) -> dict:
        """Pairwise Wilcoxon signed-rank test (non-parametric)."""
        statistic, p_value = stats.wilcoxon(results1, results2)
        return {
            "statistic": float(statistic),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
        }

    def run_full_benchmark(self, algorithms: dict, n_seeds: int = 30) -> pd.DataFrame:
        """Run all algorithms on all functions, return comparison DataFrame."""
        results = []

        for dimension in self.suite.supported_dimensions:
            functions = self.suite.list_functions(dimension)
            for func in functions:
                for alg_name, alg in algorithms.items():
                    stats_dict = self.run_algorithm_on_problem(alg, func, n_seeds=n_seeds)
                    results.append(
                        {
                            "dimension": dimension,
                            "function": func.name,
                            "algorithm": alg_name,
                            "mean": stats_dict["mean"],
                            "std": stats_dict["std"],
                            "median": stats_dict["median"],
                            "best": stats_dict["best"],
                            "worst": stats_dict["worst"],
                            "error_mean": stats_dict["error_mean"],
                        }
                    )

        return pd.DataFrame(results)

    def pairwise_wilcoxon(self, algorithms: dict, n_seeds: int = 30) -> pd.DataFrame:
        """Run pairwise Wilcoxon tests across all functions for all algorithm pairs."""
        alg_names = list(algorithms.keys())
        dimension = self.suite.supported_dimensions[0]
        functions = self.suite.list_functions(dimension)

        # Store results per algorithm per function
        algo_results = defaultdict(lambda: defaultdict(list))
        for func in functions:
            for alg_name, alg in algorithms.items():
                stats_dict = self.run_algorithm_on_problem(alg, func, n_seeds=n_seeds)
                algo_results[alg_name][func.id] = stats_dict["results"]

        # Perform pairwise tests
        comparisons = []
        for i, alg1 in enumerate(alg_names):
            for alg2 in alg_names[i + 1 :]:
                # Aggregate results across all functions
                results1 = []
                results2 = []
                for func in functions:
                    results1.extend(algo_results[alg1][func.id])
                    results2.extend(algo_results[alg2][func.id])

                test_result = self.wilcoxon_test(results1, results2)
                comparisons.append(
                    {
                        "algorithm_1": alg1,
                        "algorithm_2": alg2,
                        "statistic": test_result["statistic"],
                        "p_value": test_result["p_value"],
                        "significant": test_result["significant"],
                        "mean_1": float(np.mean(results1)),
                        "mean_2": float(np.mean(results2)),
                    }
                )

        return pd.DataFrame(comparisons)

    def export_csv(self, df: pd.DataFrame, filepath: str) -> None:
        """Export DataFrame to CSV."""
        df.to_csv(filepath, index=False)

    def export_json(self, df: pd.DataFrame, filepath: str) -> None:
        """Export DataFrame to JSON."""
        df.to_json(filepath, orient="records", indent=2)
