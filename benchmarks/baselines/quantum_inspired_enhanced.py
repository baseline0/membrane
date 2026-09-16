"""Enhanced quantum-inspired evolutionary algorithm baseline.

Wraps malta.quantum_inspired_enhanced for benchmark harness integration.
"""

import random
import numpy as np

from benchmarks.suites.base import BenchmarkFunction
from malta.quantum_inspired_enhanced import EnhancedQuantumInspiredAlgorithm


class EnhancedQuantumInspiredBaseline:
    """Enhanced quantum-inspired algorithm for benchmarking.

    Features:
    - Multi-bit encoding for fine-grained search
    - Adaptive mutation rates
    - Progressive encoding (optional)
    """

    def __init__(
        self,
        n_compartments: int = 5,
        generations: int = 1000,
        bits_per_dim: int = 8,
        use_progressive: bool = True,
    ):
        """Initialize algorithm.

        Args:
            n_compartments: Number of parallel compartments
            generations: Number of evolution generations
            bits_per_dim: Bits per dimension for encoding
            use_progressive: Whether to use progressive encoding
        """
        self.n_compartments = n_compartments
        self.generations = generations
        self.bits_per_dim = bits_per_dim
        self.use_progressive = use_progressive

    def optimize(self, problem: BenchmarkFunction, seed: int | None = None) -> float:
        """Run enhanced quantum-inspired algorithm on problem.

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
        algo = EnhancedQuantumInspiredAlgorithm(
            n_compartments=self.n_compartments,
            n_dims=problem.dimension,
            bounds=problem.bounds,
            max_generations=self.generations,
            bits_per_dim=self.bits_per_dim,
            use_progressive=self.use_progressive,
        )

        # Define objective for this problem
        def objective(x):
            return problem(np.array(x))

        # Run optimization
        best_candidate = algo.optimize(objective)

        return float(best_candidate.fitness)
