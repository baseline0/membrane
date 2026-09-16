"""Unit tests for convergence analysis.

Tests verify:
- Convergence detection (stalling)
- Trajectory comparison
- Speed and efficiency metrics
"""

import pytest

from malta.convergence import ConvergenceAnalyzer


class TestConvergenceAnalyzer:
    """Tests for convergence analysis."""

    def test_analyze_perfect_convergence(self):
        """Analyze trajectory with perfect monotonic improvement."""
        trajectory = [10.0, 8.0, 6.0, 4.0, 2.0, 0.0]

        metrics = ConvergenceAnalyzer.analyze_trajectory(trajectory)

        assert metrics.best_initial_fitness == 10.0
        assert metrics.best_final_fitness == 0.0
        assert metrics.total_improvement == 10.0
        assert metrics.improvement_rate == 10.0 / 6

    def test_analyze_stalled_convergence(self):
        """Analyze trajectory that converges early then stalls."""
        trajectory = [10.0, 5.0, 2.0, 1.9, 1.85, 1.84, 1.84, 1.84]

        metrics = ConvergenceAnalyzer.analyze_trajectory(trajectory, convergence_threshold=0.1, stall_window=3)

        # Should detect convergence around generation 4
        assert metrics.generations_to_convergence is not None
        assert metrics.generations_to_convergence <= 5
        assert metrics.total_improvement > 0

    def test_analyze_no_improvement(self):
        """Analyze trajectory with no improvement (stuck)."""
        trajectory = [10.0, 10.0, 10.0, 10.0, 10.0]

        metrics = ConvergenceAnalyzer.analyze_trajectory(trajectory)

        assert metrics.total_improvement == 0.0
        assert metrics.improvement_rate == 0.0

    def test_analyze_single_point(self):
        """Single point trajectory is valid."""
        trajectory = [5.0]

        metrics = ConvergenceAnalyzer.analyze_trajectory(trajectory)

        assert metrics.best_initial_fitness == 5.0
        assert metrics.best_final_fitness == 5.0
        assert metrics.total_improvement == 0.0

    def test_analyze_empty_raises(self):
        """Empty trajectory raises error."""
        with pytest.raises(ValueError):
            ConvergenceAnalyzer.analyze_trajectory([])

    def test_compare_trajectories(self):
        """Compare two trajectories."""
        traj_a = [10.0, 8.0, 6.0, 4.0, 2.0]
        traj_b = [10.0, 7.0, 4.5, 2.5, 1.0]

        comparison = ConvergenceAnalyzer.compare_trajectories(traj_a, traj_b, labels=("Linear", "Exponential"))

        assert "algorithm_a" in comparison
        assert "algorithm_b" in comparison
        assert "comparison" in comparison

        # Both should show improvement
        assert comparison["algorithm_a"]["total_improvement"] == 8.0
        assert comparison["algorithm_b"]["total_improvement"] == 9.0

    def test_compare_identifies_better(self):
        """Comparison identifies better algorithm."""
        traj_better = [10.0, 5.0, 1.0]  # Better
        traj_worse = [10.0, 8.0, 6.0]  # Worse

        comparison = ConvergenceAnalyzer.compare_trajectories(traj_worse, traj_better, labels=("Worse", "Better"))

        # Better should have lower final fitness
        assert comparison["algorithm_b"]["final_fitness"] < comparison["algorithm_a"]["final_fitness"]

    def test_convergence_speed_all_percentiles(self):
        """Analyze speed to reach improvement percentiles."""
        # Linear improvement: 10 -> 0 over 10 generations
        trajectory = [10.0 - i for i in range(11)]

        speed = ConvergenceAnalyzer.convergence_speed(trajectory, percentiles=[25, 50, 75, 100])

        assert "reached_25%" in speed
        assert "reached_50%" in speed
        assert "reached_75%" in speed
        assert "reached_100%" in speed

        # Linear trajectory should reach percentiles at expected generations
        # 25% improvement: fitness 7.5, reached at gen 2-3
        # 50% improvement: fitness 5.0, reached at gen 5
        # 75% improvement: fitness 2.5, reached at gen 7-8
        assert speed["reached_50%"] == 5

    def test_convergence_speed_no_improvement(self):
        """Speed analysis with no improvement returns generation count."""
        trajectory = [10.0, 10.0, 10.0]

        speed = ConvergenceAnalyzer.convergence_speed(trajectory)

        # All percentiles unreached
        for key in speed:
            assert speed[key] == len(trajectory)

    def test_efficiency_score_perfect(self):
        """Perfect convergence has efficiency close to 1.0."""
        # Reaches optimum immediately
        trajectory = [10.0, 0.0, 0.0, 0.0]

        score = ConvergenceAnalyzer.efficiency_score(trajectory)

        assert score > 0.8  # Should be high

    def test_efficiency_score_gradual(self):
        """Gradual convergence has lower efficiency."""
        # Linear improvement
        trajectory = [10.0, 9.0, 8.0, 7.0, 6.0]

        score_linear = ConvergenceAnalyzer.efficiency_score(trajectory)

        # Steep improvement
        trajectory_steep = [10.0, 2.0, 0.5, 0.1, 0.0]

        score_steep = ConvergenceAnalyzer.efficiency_score(trajectory_steep)

        # Steep should be more efficient
        assert score_steep > score_linear

    def test_efficiency_score_no_improvement(self):
        """No improvement has zero efficiency."""
        trajectory = [10.0, 10.0, 10.0]

        score = ConvergenceAnalyzer.efficiency_score(trajectory)

        assert score == 0.0

    def test_efficiency_score_single_point(self):
        """Single point has zero efficiency."""
        trajectory = [5.0]

        score = ConvergenceAnalyzer.efficiency_score(trajectory)

        assert score == 0.0

    def test_convergence_threshold_affects_detection(self):
        """Different thresholds affect convergence generation."""
        trajectory = [10.0, 5.0, 4.9, 4.85, 4.84, 4.84]

        # Strict threshold
        strict = ConvergenceAnalyzer.analyze_trajectory(trajectory, convergence_threshold=0.01, stall_window=2)

        # Loose threshold
        loose = ConvergenceAnalyzer.analyze_trajectory(trajectory, convergence_threshold=1.0, stall_window=2)

        # Loose should detect stall earlier
        if strict.generations_to_convergence and loose.generations_to_convergence:
            assert loose.generations_to_convergence <= strict.generations_to_convergence

    def test_trajectory_stored(self):
        """Trajectory is preserved in metrics."""
        original = [10.0, 5.0, 2.0, 1.0]
        metrics = ConvergenceAnalyzer.analyze_trajectory(original)

        assert metrics.trajectory == original
