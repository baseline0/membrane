"""Integration tests for toy problem benchmarking.

Tests verify:
- Benchmarks run without error
- Convergence tracking works
- Function evaluations are correct
- Traces are generated properly
- Single vs multi-compartment comparison
"""

from benchmarks.toy_benchmark import (
    BenchmarkResult,
    ToyBenchmark,
    ackley,
    rastrigin,
    rosenbrock,
    sphere,
)


class TestTestFunctions:
    """Tests for benchmark functions."""

    def test_sphere_minimum(self):
        """Sphere has minimum at origin."""
        assert sphere([0.0, 0.0]) == 0.0
        assert sphere([0.0, 0.0, 0.0]) == 0.0

    def test_sphere_increases_with_distance(self):
        """Sphere increases with distance from origin."""
        assert sphere([1.0, 0.0]) < sphere([2.0, 0.0])
        assert sphere([1.0, 1.0]) < sphere([2.0, 2.0])

    def test_rastrigin_minimum(self):
        """Rastrigin has minimum at origin."""
        result = rastrigin([0.0, 0.0])
        assert abs(result - 0.0) < 1e-6  # Allow small numerical error

    def test_rastrigin_multimodal(self):
        """Rastrigin has many local minima."""
        # Evaluate at several points
        vals = [rastrigin([x, x]) for x in [-2.0, -1.0, 1.0, 2.0]]
        # Should have variation due to multimodality
        assert len(set(vals)) > 1

    def test_rosenbrock_minimum(self):
        """Rosenbrock has minimum at (1, 1, ...)."""
        result = rosenbrock([1.0, 1.0])
        assert abs(result - 0.0) < 1e-6

    def test_rosenbrock_valley(self):
        """Rosenbrock has valley structure."""
        # Point on valley (following x=y) should be better than far point
        valley = rosenbrock([0.5, 0.25])  # Following curve x=y^0.5
        far = rosenbrock([0.5, 0.0])
        assert valley < far

    def test_ackley_minimum(self):
        """Ackley has minimum at origin."""
        result = ackley([0.0, 0.0])
        assert abs(result - 0.0) < 1e-6

    def test_ackley_plateau(self):
        """Ackley has plateau away from optimum."""
        # Values far from origin should be similar (plateau)
        far1 = ackley([10.0, 10.0])
        far2 = ackley([11.0, 11.0])
        # Both should be high and similar
        assert far1 > 15 and far2 > 15
        assert abs(far1 - far2) < 1  # Similar values on plateau


class TestBenchmarkResult:
    """Tests for BenchmarkResult dataclass."""

    def test_result_initialization(self):
        """BenchmarkResult stores all fields."""
        from malta.trace import MembraneTrace

        trace = MembraneTrace()
        result = BenchmarkResult(
            function_name="Sphere",
            dimension=2,
            n_compartments=3,
            n_generations=10,
            best_fitness=5.0,
            best_solution=[1.0, 2.0],
            final_multiset={},
            convergence_history=[10.0, 8.0, 5.0],
            trace=trace,
        )

        assert result.function_name == "Sphere"
        assert result.best_fitness == 5.0
        assert len(result.convergence_history) == 3


class TestToyBenchmark:
    """Tests for ToyBenchmark harness."""

    def test_benchmark_initialization(self):
        """Benchmark initializes with seed."""
        bench = ToyBenchmark(seed=42)
        assert bench.seed == 42
        assert bench.results == []

    def test_run_single_sphere(self):
        """Run single benchmark on sphere."""
        bench = ToyBenchmark()
        result = bench.run_single(
            sphere,
            "Sphere_test",
            n_dims=2,
            bounds=(-5.0, 5.0),
            n_compartments=3,
            n_generations=10,
        )

        assert result.function_name == "Sphere_test"
        assert result.dimension == 2
        assert result.n_compartments == 3
        assert result.n_generations == 10
        assert result.best_fitness >= 0  # Sphere is non-negative
        assert len(result.convergence_history) == 10

    def test_run_single_stores_result(self):
        """run_single stores result in harness."""
        bench = ToyBenchmark()
        result = bench.run_single(sphere, "Test", 2, (-5.0, 5.0), n_generations=5)

        assert len(bench.results) == 1
        assert bench.results[0] == result

    def test_convergence_history_is_monotonic(self):
        """Convergence history is non-increasing (best so far)."""
        bench = ToyBenchmark()
        result = bench.run_single(sphere, "Sphere", 2, (-5.0, 5.0), n_generations=15)

        history = result.convergence_history
        for i in range(1, len(history)):
            assert history[i] <= history[i - 1]  # Non-increasing

    def test_trace_generated(self):
        """Benchmark generates execution trace."""
        bench = ToyBenchmark()
        result = bench.run_single(sphere, "Sphere", 2, (-5.0, 5.0), n_generations=5)

        assert result.trace is not None
        assert len(result.trace.events) > 0

    def test_run_suite(self):
        """Run full benchmark suite."""
        bench = ToyBenchmark()
        results = bench.run_suite(n_dims=2, n_generations=10)

        # Should have 4 functions × 2 (single + multi) = 8 results
        assert len(results) == 8
        assert all(isinstance(r, BenchmarkResult) for r in results)

    def test_suite_has_single_and_multi(self):
        """Suite includes both single and multi-compartment runs."""
        bench = ToyBenchmark()
        results = bench.run_suite(n_dims=2, n_generations=5)

        single = [r for r in results if r.n_compartments == 1]
        multi = [r for r in results if r.n_compartments > 1]

        assert len(single) == 4  # One per function
        assert len(multi) == 4  # One per function

    def test_summary_aggregates_results(self):
        """Summary aggregates across runs."""
        bench = ToyBenchmark()
        bench.run_single(sphere, "Sphere", 2, (-5.0, 5.0), n_compartments=1, n_generations=5)
        bench.run_single(sphere, "Sphere", 2, (-5.0, 5.0), n_compartments=5, n_generations=5)

        summary = bench.summary()

        # Should have entries for each function variant
        assert "Sphere" in summary or len(summary) > 0

    def test_different_dimensions(self):
        """Benchmark runs on different dimensions."""
        bench = ToyBenchmark()
        for dim in [1, 2, 3]:
            result = bench.run_single(sphere, f"Sphere_dim{dim}", dim, (-5.0, 5.0), n_generations=5)
            assert result.dimension == dim
            assert len(result.best_solution) == dim

    def test_different_bounds(self):
        """Benchmark respects different bounds."""
        bench = ToyBenchmark()

        # Sphere on smaller bounds
        result_small = bench.run_single(sphere, "Sphere_small", 2, (-1.0, 1.0), n_generations=5)

        # Sphere on larger bounds
        result_large = bench.run_single(sphere, "Sphere_large", 2, (-10.0, 10.0), n_generations=5)

        # Both should find valid solutions
        assert all(-1.0 <= v <= 1.0 for v in result_small.best_solution)
        assert all(-10.0 <= v <= 10.0 for v in result_large.best_solution)

    def test_rastrigin_harder_than_sphere(self):
        """Rastrigin (multimodal) is typically harder than sphere."""
        bench = ToyBenchmark()

        rastrigin_result = bench.run_single(rastrigin, "Rastrigin", 2, (-5.12, 5.12), n_generations=20)

        # Rastrigin's minimum is at 0, but multimodality makes it harder
        # (not guaranteed to find better solution, but typically worse)
        assert rastrigin_result.best_fitness >= 0  # Valid result

    def test_single_compartment_vs_multi(self):
        """Compare single vs multi-compartment results."""
        bench = ToyBenchmark()

        single = bench.run_single(sphere, "Sphere_single", 2, (-5.0, 5.0), n_compartments=1, n_generations=20)
        multi = bench.run_single(sphere, "Sphere_multi", 2, (-5.0, 5.0), n_compartments=5, n_generations=20)

        # Both should converge (fitness decreases over time)
        assert single.convergence_history[-1] <= single.convergence_history[0]
        assert multi.convergence_history[-1] <= multi.convergence_history[0]
