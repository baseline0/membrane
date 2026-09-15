"""Adaptive evolution strategies for quantum-inspired algorithm.

Implements:
- Mutation operators (bit flip, Gaussian)
- Adaptive rates based on convergence progress
- Population diversity tracking
- Escape strategies from plateaus
"""

import random
import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class AdaptationState:
    """Current adaptation parameters and metrics."""

    generation: int
    mutation_rate: float  # Probability of mutation per bit
    mutation_strength: float  # Strength of Gaussian mutations
    diversity_score: float  # Population diversity (0-1)
    improvement_trend: float  # Recent improvement rate
    stall_counter: int  # Generations with low improvement


class MutationOperator:
    """Bit-level mutation for basis states."""

    @staticmethod
    def bit_flip(basis_state: str, mutation_rate: float) -> str:
        """Apply bit-flip mutation.

        Each bit has mutation_rate probability of flipping.

        Args:
            basis_state: Binary string
            mutation_rate: Probability per bit (0-1)

        Returns:
            Mutated binary string
        """
        mutated = list(basis_state)
        for i in range(len(mutated)):
            if random.random() < mutation_rate:
                mutated[i] = "0" if mutated[i] == "1" else "1"
        return "".join(mutated)

    @staticmethod
    def gaussian_mutation(
        basis_state: str, strength: float = 0.1
    ) -> str:
        """Apply Gaussian-style mutation (bit clusters).

        Mutates clusters of bits (like Gaussian perturbation in continuous space).

        Args:
            basis_state: Binary string
            strength: Mutation strength (0-1)

        Returns:
            Mutated binary string
        """
        mutated = list(basis_state)
        n_flips = max(1, int(len(mutated) * strength))

        # Randomly select starting position
        start = random.randint(0, len(mutated) - 1)

        # Flip cluster of bits around start position
        for offset in range(n_flips):
            idx = (start + offset) % len(mutated)
            mutated[idx] = "0" if mutated[idx] == "1" else "1"

        return "".join(mutated)


class AdaptiveEvolutionController:
    """Manages adaptive mutation rates and escape strategies."""

    def __init__(self, n_generations: int):
        """Initialize controller.

        Args:
            n_generations: Total generations in run
        """
        self.n_generations = n_generations
        self.state = AdaptationState(
            generation=0,
            mutation_rate=0.01,
            mutation_strength=0.05,
            diversity_score=1.0,
            improvement_trend=0.0,
            stall_counter=0,
        )
        self.fitness_history: list[float] = []

    def update(
        self,
        generation: int,
        current_best_fitness: float,
        prev_best_fitness: Optional[float] = None,
        population_diversity: float = 0.5,
    ) -> None:
        """Update adaptation state based on progress.

        Args:
            generation: Current generation number
            current_best_fitness: Best fitness in current generation
            prev_best_fitness: Best fitness in previous generation
            population_diversity: Diversity metric (0-1, higher = more diverse)
        """
        self.state.generation = generation
        self.fitness_history.append(current_best_fitness)
        self.state.diversity_score = population_diversity

        # Compute improvement
        if prev_best_fitness is not None:
            improvement = prev_best_fitness - current_best_fitness
            # Exponential moving average
            self.state.improvement_trend = (
                0.7 * self.state.improvement_trend + 0.3 * improvement
            )

            # Detect stalling
            if improvement < 1e-6:
                self.state.stall_counter += 1
            else:
                self.state.stall_counter = 0
        else:
            self.state.improvement_trend = 0.0

        # Adapt mutation rate based on progress
        self._adapt_mutation_rate()

        # Escape strategy if stalled
        if self.state.stall_counter > 5:
            self._apply_escape_strategy()

    def _adapt_mutation_rate(self) -> None:
        """Adjust mutation rate based on convergence progress.

        - Early: High exploration (high mutation)
        - Middle: Moderate mutation
        - Late: Low mutation (fine-tuning)
        - Stalled: Increase mutation to escape
        """
        progress = self.state.generation / max(1, self.n_generations)

        # Base rate: start high, decrease over time
        base_rate = 0.05 * (1.0 - 0.7 * progress)

        # Stalling penalty: increase mutation if stuck
        if self.state.improvement_trend < 1e-6:
            escape_boost = 0.02
        else:
            escape_boost = 0.0

        self.state.mutation_rate = base_rate + escape_boost
        self.state.mutation_rate = max(0.001, min(0.2, self.state.mutation_rate))

    def _apply_escape_strategy(self) -> None:
        """Increase mutation strength when stalled."""
        self.state.mutation_strength = min(
            0.3, self.state.mutation_strength * 1.5
        )

    def get_mutation_rate(self) -> float:
        """Get current mutation rate for bit-flip operations.

        Returns:
            Mutation rate (0-1)
        """
        return self.state.mutation_rate

    def get_mutation_strength(self) -> float:
        """Get current mutation strength for Gaussian operations.

        Returns:
            Mutation strength (0-1)
        """
        return self.state.mutation_strength

    def should_restart_population(self) -> bool:
        """Decide if population should be restarted (diversity boost).

        Returns:
            True if should restart with new random individuals
        """
        # Restart if diversity is very low and improvement is stalling
        return (
            self.state.diversity_score < 0.2
            and self.state.improvement_trend < 1e-5
            and self.state.generation > 50
        )


class DiversityMetrics:
    """Compute population diversity from fitness values."""

    @staticmethod
    def hamming_diversity(population: list[str]) -> float:
        """Compute Hamming diversity of basis states.

        Measures average Hamming distance between random pairs.

        Args:
            population: List of binary strings

        Returns:
            Diversity score (0-1)
        """
        if len(population) < 2:
            return 0.0

        n_samples = min(10, len(population) * (len(population) - 1) // 2)
        total_distance = 0
        for _ in range(n_samples):
            idx1, idx2 = random.sample(range(len(population)), 2)
            state1, state2 = population[idx1], population[idx2]

            # Hamming distance
            distance = sum(b1 != b2 for b1, b2 in zip(state1, state2))
            total_distance += distance

        # Normalize by max possible distance
        max_distance = len(population[0]) if population else 1
        avg_distance = total_distance / n_samples if n_samples > 0 else 0
        diversity = avg_distance / max_distance
        return min(1.0, max(0.0, diversity))

    @staticmethod
    def fitness_diversity(fitness_values: list[float]) -> float:
        """Compute fitness diversity (variance-based).

        Args:
            fitness_values: List of fitness values

        Returns:
            Diversity score (0-1)
        """
        if len(fitness_values) < 2:
            return 0.0

        import statistics

        mean = statistics.mean(fitness_values)
        variance = statistics.variance(fitness_values)

        # No variance means no diversity
        if variance == 0:
            return 0.0

        if mean == 0:
            return 0.0

        # Coefficient of variation normalized to [0, 1]
        std_dev = math.sqrt(variance)
        cv = std_dev / abs(mean)

        # Sigmoid to map to [0, 1]
        return 1.0 / (1.0 + math.exp(-cv))
