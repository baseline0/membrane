"""
CEC2017 Benchmark Runner: Quantum-Inspired vs. GA Baseline

Runs 30 independent trials of each algorithm on the 11-function subset.
Exports results to CSV for analysis and paper generation.

CEC2017 Functions (11-function subset):
  - Unimodal: F1, F3, F4 (3 functions)
  - Multimodal: F5, F6, F8 (3 functions)
  - Hybrid: F11, F14, F17 (3 functions)
  - Composition: F21, F26 (2 functions)
"""

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np

# CEC2017 Function subset: name, function_id, category
FUNCTIONS = [
    ("F1", 1, "unimodal"),
    ("F3", 3, "unimodal"),
    ("F4", 4, "unimodal"),
    ("F5", 5, "multimodal"),
    ("F6", 6, "multimodal"),
    ("F8", 8, "multimodal"),
    ("F11", 11, "hybrid"),
    ("F14", 14, "hybrid"),
    ("F17", 17, "hybrid"),
    ("F21", 21, "composition"),
    ("F26", 26, "composition"),
]

DIMENSIONS = 10  # 10D for initial validation
RUNS = 30  # 30 independent runs per function
MAX_EVALUATIONS = 200 * DIMENSIONS  # Standard: 200 * D


@dataclass
class TrialResult:
    """Result of a single algorithm trial on a single function."""

    function: str
    algorithm: str
    dimension: int
    trial: int
    best_value: float
    mean_value: float
    std_value: float
    evaluations: int
    convergence_curve: List[float]  # Best value per generation

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "function": self.function,
            "algorithm": self.algorithm,
            "dimension": self.dimension,
            "trial": self.trial,
            "best_value": float(self.best_value),
            "mean_value": float(self.mean_value),
            "std_value": float(self.std_value),
            "evaluations": int(self.evaluations),
        }


@dataclass
class AlgorithmConfig:
    """Configuration for an algorithm."""

    name: str
    population: int
    generations: int
    seed_offset: int  # For reproducibility: seed = trial + seed_offset


class CEC2017Runner:
    """Orchestrates benchmark runs."""

    def __init__(self, output_dir: Path = Path("results")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[TrialResult] = []

    def run_trial(
        self,
        func_id: int,
        algorithm: AlgorithmConfig,
        dimension: int,
        trial: int,
    ) -> TrialResult:
        """
        Run a single trial of an algorithm on a function.

        TODO: Implement actual benchmark harness integration
        - Load CEC2017 function (C library wrapper)
        - Initialize algorithm with config
        - Run for MAX_EVALUATIONS
        - Track convergence curve
        - Return TrialResult
        """
        print(f"Running {algorithm.name} on F{func_id} (10D, trial {trial + 1}/{RUNS})...")

        # Placeholder: Generate mock results for demonstration
        # TODO: Replace with actual algorithm runs
        np.random.seed(algorithm.seed_offset + trial)
        convergence = np.sort(np.random.rand(100))[::-1]  # Decreasing curve
        best_value = convergence[-1]
        mean_value = np.mean(convergence)
        std_value = np.std(convergence)

        result = TrialResult(
            function=f"F{func_id}",
            algorithm=algorithm.name,
            dimension=dimension,
            trial=trial,
            best_value=best_value,
            mean_value=mean_value,
            std_value=std_value,
            evaluations=MAX_EVALUATIONS,
            convergence_curve=convergence.tolist(),
        )

        self.results.append(result)
        return result

    def run_suite(self, algorithms: List[AlgorithmConfig]):
        """Run full benchmark suite on all functions."""
        print("\n🚀 Running CEC2017 Benchmark Suite")
        print(f"   Functions: {len(FUNCTIONS)}")
        print(f"   Algorithms: {len(algorithms)}")
        print(f"   Runs per function: {RUNS}")
        print(f"   Dimensions: {DIMENSIONS}D")
        print(f"   Max evaluations: {MAX_EVALUATIONS}")
        print()

        total = len(FUNCTIONS) * len(algorithms) * RUNS
        count = 0

        for func_name, func_id, category in FUNCTIONS:
            for algorithm in algorithms:
                for trial in range(RUNS):
                    self.run_trial(func_id, algorithm, DIMENSIONS, trial)
                    count += 1
                    if count % 10 == 0:
                        print(f"   Progress: {count}/{total} trials")

        print(f"✅ Completed {total} trials")

    def export_csv(self, filename: str = "results.csv"):
        """Export results to CSV."""
        output_path = self.output_dir / filename
        with open(output_path, "w", newline="") as f:
            fieldnames = [
                "function",
                "algorithm",
                "dimension",
                "trial",
                "best_value",
                "mean_value",
                "std_value",
                "evaluations",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                writer.writerow(result.to_dict())
        print(f"✅ Exported {output_path}")

    def export_json(self, filename: str = "results.json"):
        """Export results to JSON (with convergence curves)."""
        output_path = self.output_dir / filename
        data = {
            "metadata": {
                "functions": FUNCTIONS,
                "dimensions": DIMENSIONS,
                "runs": RUNS,
                "max_evaluations": MAX_EVALUATIONS,
            },
            "results": [r.to_dict() for r in self.results],
        }
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Exported {output_path}")

    def generate_summary(self):
        """Generate summary statistics by function and algorithm."""
        print("\n📊 Summary Statistics")
        print("=" * 80)

        summary = {}
        for func_name, _, _ in FUNCTIONS:
            summary[func_name] = {}
            for result in self.results:
                if result.function == func_name:
                    algo = result.algorithm
                    if algo not in summary[func_name]:
                        summary[func_name][algo] = []
                    summary[func_name][algo].append(result.best_value)

        # Print table
        print(f"{'Function':<10} {'Algorithm':<20} {'Mean':<12} {'Std':<12}")
        print("-" * 80)
        for func_name in sorted(summary.keys()):
            for algo in sorted(summary[func_name].keys()):
                values = summary[func_name][algo]
                mean = np.mean(values)
                std = np.std(values)
                print(f"{func_name:<10} {algo:<20} {mean:<12.4e} {std:<12.4e}")
            print()

        return summary


def main():
    """Main entry point: run full benchmark suite."""
    runner = CEC2017Runner()

    # Define algorithms to compare
    algorithms = [
        AlgorithmConfig(name="GA", population=50, generations=200, seed_offset=0),
        # TODO: Add QIPS (Quantum-Inspired P-Systems) once algorithm is implemented
        # AlgorithmConfig(name="QIPS", population=50, generations=200, seed_offset=1000),
    ]

    # Run suite
    runner.run_suite(algorithms)

    # Export results
    runner.export_csv()
    runner.export_json()

    # Print summary
    runner.generate_summary()

    print("\n💾 Results saved to:")
    print(f"   {runner.output_dir}/results.csv")
    print(f"   {runner.output_dir}/results.json")
    print("\nTo generate plots and analysis for paper:")
    print("   cd ../paper && python build_paper.py")


if __name__ == "__main__":
    main()
