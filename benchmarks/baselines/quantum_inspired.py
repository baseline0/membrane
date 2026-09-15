"""Quantum-inspired evolutionary algorithm baseline.

Wraps malta.quantum_inspired for benchmark harness integration.
"""

import random
import numpy as np

from benchmarks.suites.base import BenchmarkFunction
from malta.quantum_inspired import QuantumInspiredEvolutionaryAlgorithm


class QuantumInspiredBaseline:
    """Quantum-inspired evolutionary algorithm for benchmarking.

    Adapts malta.quantum_inspired to benchmark harness interface.
    """

    def __init__(
        self,
        n_compartments: int = 5,
        generations: int = 1000,
    ):
        """Initialize algorithm.

        Args:
            n_compartments: Number of parallel membrane compartments
            generations: Number of evolution generations
        """
        self.n_compartments = n_compartments
        self.generations = generations

    def optimize(self, problem: BenchmarkFunction, seed: int | None = None) -> float:
        """Run quantum-inspired algorithm on problem.

        Args:
            problem: BenchmarkFunction to minimize
            seed: Random seed for reproducibility

        Returns:
            Best fitness found
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Create algorithm instance
        algo = QuantumInspiredEvolutionaryAlgorithm(
            n_compartments=self.n_compartments,
            n_dims=problem.dimension,
            bounds=problem.bounds,
            max_generations=self.generations,
        )

        # Define objective for this problem
        def objective(x):
            return problem(np.array(x))

        # Run optimization
        best_candidate = algo.optimize(objective)

        return float(best_candidate.fitness)
