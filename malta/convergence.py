"""Convergence analysis and metrics for optimization algorithms.

Provides tools to:
- Detect convergence (fitness stalls for N generations)
- Compute convergence rate (improvement per generation)
- Compare single vs multi-compartment efficiency
- Export convergence data for visualization
"""

import statistics
from dataclasses import dataclass
from typing import Optional


@dataclass
class ConvergenceMetrics:
    """Convergence statistics for single run."""

    best_final_fitness: float
    best_initial_fitness: float
    total_improvement: float  # absolute value decrease
    improvement_rate: float  # improvement per generation
    generations_to_convergence: Optional[int]  # when stalled at threshold
    convergence_threshold: float  # fitness change threshold
    stall_generations: int  # consecutive generations with < threshold change
    trajectory: list[float]  # fitness at each generation


class ConvergenceAnalyzer:
    """Analyze convergence behavior of optimization runs."""

    @staticmethod
    def analyze_trajectory(
        trajectory: list[float],
        convergence_threshold: float = 1e-6,
        stall_window: int = 5,
    ) -> ConvergenceMetrics:
        """Analyze single convergence trajectory.

        Args:
            trajectory: List of best fitness values over generations
            convergence_threshold: Fitness improvement threshold to detect stall
            stall_window: Number of generations with low improvement to declare stall

        Returns:
            ConvergenceMetrics with detailed analysis
        """
        if not trajectory:
            raise ValueError("Empty trajectory")

        best_initial = trajectory[0]
        best_final = trajectory[-1]
        total_improvement = max(0, best_initial - best_final)
        improvement_rate = total_improvement / len(trajectory)

        # Detect convergence (stalling)
        generations_to_convergence = None
        for i in range(stall_window, len(trajectory)):
            # Check if last `stall_window` generations had low improvement
            window = trajectory[i - stall_window : i + 1]
            max_change = abs(window[0] - window[-1])

            if max_change < convergence_threshold:
                generations_to_convergence = i - stall_window
                break

        return ConvergenceMetrics(
            best_final_fitness=best_final,
            best_initial_fitness=best_initial,
            total_improvement=total_improvement,
            improvement_rate=improvement_rate,
            generations_to_convergence=generations_to_convergence,
            convergence_threshold=convergence_threshold,
            stall_generations=stall_window,
            trajectory=trajectory,
        )

    @staticmethod
    def compare_trajectories(
        trajectory_a: list[float],
        trajectory_b: list[float],
        labels: tuple[str, str] = ("Algorithm A", "Algorithm B"),
    ) -> dict:
        """Compare two convergence trajectories.

        Args:
            trajectory_a: First trajectory
            trajectory_b: Second trajectory
            labels: Names for reporting

        Returns:
            Dictionary with comparison metrics
        """
        metrics_a = ConvergenceAnalyzer.analyze_trajectory(trajectory_a)
        metrics_b = ConvergenceAnalyzer.analyze_trajectory(trajectory_b)

        # Normalize to same length for point-wise comparison
        min_len = min(len(trajectory_a), len(trajectory_b))
        a_norm = trajectory_a[:min_len]
        b_norm = trajectory_b[:min_len]

        # Compute point-wise differences (b - a, so positive means b better)
        differences = [b_norm[i] - a_norm[i] for i in range(min_len)]
        avg_diff = statistics.mean(differences)
        std_diff = statistics.stdev(differences) if len(differences) > 1 else 0

        return {
            "algorithm_a": {
                "label": labels[0],
                "final_fitness": metrics_a.best_final_fitness,
                "total_improvement": metrics_a.total_improvement,
                "improvement_rate": metrics_a.improvement_rate,
                "convergence_gen": metrics_a.generations_to_convergence,
            },
            "algorithm_b": {
                "label": labels[1],
                "final_fitness": metrics_b.best_final_fitness,
                "total_improvement": metrics_b.total_improvement,
                "improvement_rate": metrics_b.improvement_rate,
                "convergence_gen": metrics_b.generations_to_convergence,
            },
            "comparison": {
                "avg_difference": avg_diff,  # b - a, positive = b better
                "std_difference": std_diff,
                "better_algorithm": labels[1] if avg_diff < 0 else labels[0],
                "samples": min_len,
            },
        }

    @staticmethod
    def convergence_speed(
        trajectory: list[float],
        percentiles: list[float] = [25, 50, 75, 90],
    ) -> dict:
        """Analyze how quickly algorithm reaches fitness milestones.

        Args:
            trajectory: Fitness trajectory
            percentiles: List of improvement percentiles to analyze (0-100)

        Returns:
            Dictionary mapping percentile to generation achieved
        """
        best_initial = trajectory[0]
        best_final = trajectory[-1]
        improvement_range = best_initial - best_final

        if improvement_range == 0:
            # No improvement; return generation infinity for all percentiles
            return {p: len(trajectory) for p in percentiles}

        results = {}
        for percentile in percentiles:
            # Target fitness: initial - (percentile% of total improvement)
            target = best_initial - (percentile / 100) * improvement_range

            # Find generation where this target is first reached
            gen_reached = len(trajectory)  # Default: never reached
            for gen, fitness in enumerate(trajectory):
                if fitness <= target:
                    gen_reached = gen
                    break

            results[f"reached_{percentile}%"] = gen_reached

        return results

    @staticmethod
    def efficiency_score(
        trajectory: list[float],
        ideal_trajectory: Optional[list[float]] = None,
    ) -> float:
        """Score algorithm efficiency on convergence.

        Simple metric: how much improvement per generation.

        Args:
            trajectory: Fitness trajectory
            ideal_trajectory: Optional baseline (e.g., perfect convergence)

        Returns:
            Efficiency score (0-1, higher is better)
        """
        if len(trajectory) < 2:
            return 0.0

        # Normalize: compare area under curve
        initial = trajectory[0]
        final = trajectory[-1]
        range_val = initial - final

        if range_val == 0:
            return 0.0  # No improvement

        # Area under trajectory (inverted fitness curve)
        area_actual = sum(initial - f for f in trajectory)

        # Theoretical best: linear improvement to final fitness in first 1 generation
        # then stall (steep drop then flat)
        if ideal_trajectory:
            area_ideal = sum(initial - f for f in ideal_trajectory)
        else:
            # Default ideal: reach final in 1 gen, then stall
            area_ideal = range_val + final * (len(trajectory) - 1)

        # Clip to [0, 1]
        efficiency = min(1.0, area_actual / area_ideal) if area_ideal > 0 else 0.0
        return max(0.0, efficiency)
