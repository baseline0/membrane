"""Toy problem benchmarking for quantum-inspired algorithm.

Tests algorithm on small, well-understood problems to validate:
- Convergence behavior
- Solution quality vs problem difficulty
- Compartment count effects
- Trace and export pipeline end-to-end
"""

import math
from dataclasses import dataclass
from typing import Callable

from malta.quantum_inspired import QuantumInspiredEvolutionaryAlgorithm
from malta.trace import MembraneTrace


# Standard test functions
def sphere(x: list[float]) -> float:
    """Sphere: f(x) = Σ x_i².

    Global minimum: 0.0 at (0, 0, ...)
    Difficulty: Very easy (convex, unimodal)
    """
    return sum(xi**2 for xi in x)


def rastrigin(x: list[float]) -> float:
    """Rastrigin: f(x) = 10n + Σ(x_i² - 10cos(2πx_i)).

    Global minimum: 0.0 at (0, 0, ...)
    Difficulty: Hard (highly multimodal, many local minima)
    """
    n = len(x)
    return 10 * n + sum(xi**2 - 10 * math.cos(2 * math.pi * xi) for xi in x)


def rosenbrock(x: list[float]) -> float:
    """Rosenbrock: f(x) = Σ[100(x_{i+1} - x_i²)² + (1 - x_i)²].

    Global minimum: 0.0 at (1, 1, ...)
    Difficulty: Medium (valley-shaped, requires directional search)
    """
    return sum(100 * (x[i + 1] - x[i] ** 2) ** 2 + (1 - x[i]) ** 2 for i in range(len(x) - 1))


def ackley(x: list[float]) -> float:
    """Ackley: Multi-exponential function with narrow global basin.

    Global minimum: 0.0 at (0, 0, ...)
    Difficulty: Medium (deceptive, narrow optimum surrounded by plateau)
    """
    n = len(x)
    sum_sq = sum(xi**2 for xi in x)
    sum_cos = sum(math.cos(2 * math.pi * xi) for xi in x)
    return -20 * math.exp(-0.2 * math.sqrt(sum_sq / n)) - math.exp(sum_cos / n) + 20 + math.e


@dataclass
class BenchmarkResult:
    """Result of single benchmark run."""

    function_name: str
    dimension: int
    n_compartments: int
    n_generations: int
    best_fitness: float
    best_solution: list[float]
    final_multiset: dict
    convergence_history: list[float]  # Best fitness at each generation
    trace: MembraneTrace


class ToyBenchmark:
    """Benchmark suite for toy problems."""

    def __init__(self, seed: int = 42):
        """Initialize benchmark.

        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        self.results: list[BenchmarkResult] = []

    def run_single(
        self,
        objective: Callable[[list[float]], float],
        function_name: str,
        n_dims: int,
        bounds: tuple[float, float],
        n_compartments: int = 3,
        n_generations: int = 30,
    ) -> BenchmarkResult:
        """Run algorithm on single function.

        Args:
            objective: Function to minimize
            function_name: Name for reporting
            n_dims: Problem dimensionality
            bounds: Variable bounds
            n_compartments: Number of parallel compartments
            n_generations: Evolution generations

        Returns:
            BenchmarkResult with trace
        """
        trace = MembraneTrace(description=f"{function_name} (dim={n_dims}, compartments={n_compartments})")

        algo = QuantumInspiredEvolutionaryAlgorithm(
            n_compartments=n_compartments,
            n_dims=n_dims,
            bounds=bounds,
            max_generations=n_generations,
        )

        best = None
        convergence = []

        for generation in range(n_generations):
            all_candidates = []

            # Measure and evaluate
            for compartment in algo.compartments:
                candidate = compartment.measure_and_decode(n_dims, bounds)
                candidate.fitness = objective(candidate.values)
                all_candidates.append(candidate)

                # Trace measurement
                trace.record_measurement(
                    step=generation,
                    membrane_id=f"compartment_{compartment.compartment_id}",
                    quantum_state_before=dict(compartment.quantum_state.state_vector),
                    outcome=str(candidate.values),
                    probability=candidate.fitness,  # Simplified; real probability tracking would be better
                )

            # Track best
            gen_best = min(all_candidates, key=lambda c: c.fitness)
            if best is None or gen_best.fitness < best.fitness:
                best = gen_best.copy()
                trace.record_state_transition(
                    step=generation,
                    membrane_id="global",
                    multiset_before={},
                    multiset_after={"best_found": 1},
                    reason="improved_solution",
                )

            convergence.append(best.fitness)

            # Reinitialize
            for compartment in algo.compartments:
                compartment.initialize_superposition(n_dims)
                compartment.best_candidate = gen_best.copy()

        result = BenchmarkResult(
            function_name=function_name,
            dimension=n_dims,
            n_compartments=n_compartments,
            n_generations=n_generations,
            best_fitness=best.fitness,
            best_solution=best.values,
            final_multiset={},
            convergence_history=convergence,
            trace=trace,
        )

        self.results.append(result)
        return result

    def run_suite(self, n_dims: int = 2, n_generations: int = 30) -> list[BenchmarkResult]:
        """Run benchmark on all toy functions.

        Args:
            n_dims: Problem dimensionality
            n_generations: Generations per run

        Returns:
            List of BenchmarkResult
        """
        functions = [
            (sphere, "Sphere", (-5.0, 5.0)),
            (rastrigin, "Rastrigin", (-5.12, 5.12)),
            (rosenbrock, "Rosenbrock", (-2.048, 2.048)),
            (ackley, "Ackley", (-32.768, 32.768)),
        ]

        results = []
        for objective, name, bounds in functions:
            # Single compartment
            result_single = self.run_single(
                objective,
                f"{name}_single",
                n_dims,
                bounds,
                n_compartments=1,
                n_generations=n_generations,
            )
            results.append(result_single)

            # Multi-compartment
            result_multi = self.run_single(
                objective,
                f"{name}_multi",
                n_dims,
                bounds,
                n_compartments=5,
                n_generations=n_generations,
            )
            results.append(result_multi)

        return results

    def summary(self) -> dict:
        """Get summary statistics across all runs.

        Returns:
            Dictionary with aggregated metrics
        """
        if not self.results:
            return {}

        by_function = {}
        for result in self.results:
            func = result.function_name
            if func not in by_function:
                by_function[func] = []
            by_function[func].append(result)

        summary = {}
        for func, runs in by_function.items():
            summary[func] = {
                "count": len(runs),
                "best_fitness": min(r.best_fitness for r in runs),
                "worst_fitness": max(r.best_fitness for r in runs),
                "avg_fitness": sum(r.best_fitness for r in runs) / len(runs),
                "single_vs_multi": {
                    "single": [r.best_fitness for r in runs if r.n_compartments == 1],
                    "multi": [r.best_fitness for r in runs if r.n_compartments > 1],
                },
            }

        return summary
