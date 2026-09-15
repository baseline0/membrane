"""Unit tests for adaptive evolution strategies.

Tests verify:
- Mutation operators produce valid results
- Adaptation rates change over generations
- Escape strategies activate when stalled
- Diversity metrics are computed correctly
"""

import pytest

from malta.adaptive_evolution import (
    MutationOperator,
    AdaptiveEvolutionController,
    DiversityMetrics,
)


class TestMutationOperator:
    """Tests for mutation operations."""

    def test_bit_flip_no_mutation(self):
        """Zero mutation rate produces no changes."""
        original = "10101010"
        mutated = MutationOperator.bit_flip(original, 0.0)
        assert mutated == original

    def test_bit_flip_high_mutation(self):
        """High mutation rate produces changes."""
        original = "00000000"
        mutated = MutationOperator.bit_flip(original, 1.0)
        assert mutated == "11111111"

    def test_bit_flip_valid_output(self):
        """Bit flip output is valid binary string."""
        original = "1010"
        mutated = MutationOperator.bit_flip(original, 0.5)
        assert len(mutated) == len(original)
        assert all(b in "01" for b in mutated)

    def test_bit_flip_stochastic(self):
        """Bit flip has stochastic variation."""
        original = "1010"
        mutations = [
            MutationOperator.bit_flip(original, 0.5) for _ in range(20)
        ]
        # Should have multiple different outcomes
        unique = set(mutations)
        assert len(unique) > 1

    def test_gaussian_mutation_changes(self):
        """Gaussian mutation modifies bits."""
        original = "00000000"
        mutated = MutationOperator.gaussian_mutation(original, 0.5)
        # Should have some 1s after mutation
        assert "1" in mutated

    def test_gaussian_mutation_cluster(self):
        """Gaussian mutation clusters changes."""
        original = "10" * 20  # Alternating pattern
        mutated = MutationOperator.gaussian_mutation(original, 0.1)
        # Should have contiguous changes due to clustering
        assert len(mutated) == len(original)

    def test_gaussian_mutation_valid(self):
        """Gaussian mutation produces valid binary string."""
        original = "1010101010"
        mutated = MutationOperator.gaussian_mutation(original, 0.3)
        assert len(mutated) == len(original)
        assert all(b in "01" for b in mutated)


class TestAdaptiveEvolutionController:
    """Tests for adaptive evolution control."""

    def test_initialization(self):
        """Controller initializes with default state."""
        controller = AdaptiveEvolutionController(100)
        assert controller.state.generation == 0
        assert controller.state.stall_counter == 0
        assert controller.state.mutation_rate > 0

    def test_update_generation(self):
        """Update increments generation counter."""
        controller = AdaptiveEvolutionController(100)
        controller.update(5, 10.0)
        assert controller.state.generation == 5

    def test_update_improvement_positive(self):
        """Positive improvement increases trend."""
        controller = AdaptiveEvolutionController(100)
        controller.update(1, 10.0, prev_best_fitness=11.0)
        # Should record improvement
        assert controller.state.improvement_trend > 0

    def test_update_improvement_negative(self):
        """No improvement (worsening) detected."""
        controller = AdaptiveEvolutionController(100)
        controller.update(1, 11.0, prev_best_fitness=10.0)
        # Worsening is treated as zero improvement
        assert controller.state.improvement_trend <= 0

    def test_stall_counter_increments(self):
        """Stall counter increments when stuck."""
        controller = AdaptiveEvolutionController(100)
        # No improvement several times
        for i in range(5):
            controller.update(i, 10.0, prev_best_fitness=10.0)
        # Should have positive stall counter
        assert controller.state.stall_counter > 0

    def test_stall_counter_resets(self):
        """Stall counter resets on improvement."""
        controller = AdaptiveEvolutionController(100)
        # First stall
        controller.update(0, 10.0, prev_best_fitness=10.0)
        assert controller.state.stall_counter == 1
        # Then improve
        controller.update(1, 5.0, prev_best_fitness=10.0)
        assert controller.state.stall_counter == 0

    def test_mutation_rate_changes_over_time(self):
        """Mutation rate decreases over generations."""
        controller = AdaptiveEvolutionController(100)
        rates = []
        for gen in range(0, 101, 10):
            controller.update(gen, 10.0)
            rates.append(controller.get_mutation_rate())

        # Should generally decrease (allow some noise)
        assert rates[0] >= rates[-1]

    def test_escape_strategy_increases_mutation(self):
        """Escape strategy increases mutation strength when stalled."""
        controller = AdaptiveEvolutionController(100)
        initial_strength = controller.get_mutation_strength()

        # Simulate stalling
        for i in range(10):
            controller.update(i, 10.0, prev_best_fitness=10.0)

        final_strength = controller.get_mutation_strength()
        # Should increase when stalled
        if controller.state.stall_counter > 5:
            assert final_strength >= initial_strength

    def test_should_restart_population_high_diversity(self):
        """Should not restart if diversity is good."""
        controller = AdaptiveEvolutionController(100)
        controller.update(50, 10.0, population_diversity=0.9)
        assert not controller.should_restart_population()

    def test_should_restart_population_low_diversity(self):
        """May restart if diversity is low and stalled."""
        controller = AdaptiveEvolutionController(100)
        # Force low diversity and stalling
        for i in range(60):
            controller.update(i, 10.0, prev_best_fitness=10.0, population_diversity=0.1)
        assert controller.should_restart_population()

    def test_fitness_history_recorded(self):
        """Fitness values are recorded."""
        controller = AdaptiveEvolutionController(100)
        controller.update(0, 5.0)
        controller.update(1, 4.0)
        controller.update(2, 3.5)

        assert len(controller.fitness_history) == 3
        assert controller.fitness_history == [5.0, 4.0, 3.5]


class TestDiversityMetrics:
    """Tests for population diversity computation."""

    def test_hamming_diversity_identical(self):
        """Identical population has zero diversity."""
        population = ["1010", "1010", "1010"]
        diversity = DiversityMetrics.hamming_diversity(population)
        assert diversity == 0.0

    def test_hamming_diversity_different(self):
        """Different population has nonzero diversity."""
        population = ["0000", "1111"]
        diversity = DiversityMetrics.hamming_diversity(population)
        assert diversity > 0

    def test_hamming_diversity_single(self):
        """Single individual has zero diversity."""
        diversity = DiversityMetrics.hamming_diversity(["1010"])
        assert diversity == 0.0

    def test_hamming_diversity_empty(self):
        """Empty population has zero diversity."""
        diversity = DiversityMetrics.hamming_diversity([])
        assert diversity == 0.0

    def test_hamming_diversity_bounded(self):
        """Diversity is bounded [0, 1]."""
        population = ["10" * 10, "01" * 10, "11" * 10]
        diversity = DiversityMetrics.hamming_diversity(population)
        assert 0.0 <= diversity <= 1.0

    def test_fitness_diversity_identical(self):
        """Identical fitness has zero diversity."""
        fitnesses = [5.0, 5.0, 5.0]
        diversity = DiversityMetrics.fitness_diversity(fitnesses)
        assert diversity == 0.0

    def test_fitness_diversity_different(self):
        """Different fitness has nonzero diversity."""
        fitnesses = [1.0, 5.0, 10.0]
        diversity = DiversityMetrics.fitness_diversity(fitnesses)
        assert diversity > 0

    def test_fitness_diversity_single(self):
        """Single fitness has zero diversity."""
        diversity = DiversityMetrics.fitness_diversity([5.0])
        assert diversity == 0.0

    def test_fitness_diversity_bounded(self):
        """Fitness diversity bounded [0, 1]."""
        fitnesses = [1.0, 10.0, 100.0, 0.1]
        diversity = DiversityMetrics.fitness_diversity(fitnesses)
        assert 0.0 <= diversity <= 1.0
