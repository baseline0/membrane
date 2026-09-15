"""Integration tests for benchmark harness."""

import numpy as np
import pandas as pd
import pytest

from benchmarks.baselines.ga import GeneticAlgorithm
from benchmarks.baselines.pso import ParticleSwarmOptimizer
from benchmarks.harness import BenchmarkHarness
from benchmarks.suites.base import BenchmarkFunction, BenchmarkSuite


class SimpleBenchmarkSuite(BenchmarkSuite):
    """Simple test suite with one sphere function."""

    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "SimpleSuite"

    @property
    def supported_dimensions(self) -> list[int]:
        return [5]

    def get_function(self, func_id, dimension) -> BenchmarkFunction:
        def sphere(x):
            return float(np.sum(x**2))

        return BenchmarkFunction(
            id=1,
            name="Sphere",
            dimension=dimension,
            bounds=(-5.0, 5.0),
            optimum_value=0.0,
            func=sphere,
        )

    def list_functions(self, dimension) -> list[BenchmarkFunction]:
        return [self.get_function(1, dimension)]


@pytest.fixture
def harness():
    """Create a harness with simple test suite (non-strict for testing)."""
    suite = SimpleBenchmarkSuite()
    return BenchmarkHarness(suite, strict=False)


@pytest.fixture
def algorithms():
    """Create simple test algorithms."""
    return {
        "ga": GeneticAlgorithm(pop_size=20, generations=10),
        "pso": ParticleSwarmOptimizer(pop_size=10, generations=10),
    }


class TestBenchmarkHarness:
    def test_run_single_seed(self, harness, algorithms):
        """Test single seed run returns float."""
        problem = harness.suite.get_function(1, 5)
        result = harness.run_single_seed(algorithms["ga"], problem, seed=42)
        assert isinstance(result, float)
        assert result >= problem.optimum_value

    def test_run_algorithm_on_problem(self, harness, algorithms):
        """Test algorithm on problem with multiple seeds."""
        problem = harness.suite.get_function(1, 5)
        stats = harness.run_algorithm_on_problem(algorithms["ga"], problem, n_seeds=5)

        assert isinstance(stats, dict)
        assert "mean" in stats
        assert "std" in stats
        assert "median" in stats
        assert "best" in stats
        assert "worst" in stats
        assert "results" in stats
        assert len(stats["results"]) == 5
        assert stats["best"] <= stats["mean"] <= stats["worst"]

    def test_wilcoxon_test(self, harness):
        """Test Wilcoxon test returns correct structure."""
        results1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        results2 = [2.0, 3.0, 4.0, 5.0, 6.0]
        test_result = harness.wilcoxon_test(results1, results2)

        assert isinstance(test_result, dict)
        assert "statistic" in test_result
        assert "p_value" in test_result
        assert "significant" in test_result
        assert isinstance(test_result["p_value"], float)
        assert 0.0 <= test_result["p_value"] <= 1.0

    def test_run_full_benchmark(self, harness, algorithms):
        """Test full benchmark run with multiple algorithms."""
        df = harness.run_full_benchmark(algorithms, n_seeds=3)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2  # 2 algorithms
        assert "dimension" in df.columns
        assert "function" in df.columns
        assert "algorithm" in df.columns
        assert "mean" in df.columns
        assert "std" in df.columns
        assert "error_mean" in df.columns

    def test_export_csv(self, harness, algorithms, tmp_path):
        """Test CSV export."""
        df = harness.run_full_benchmark(algorithms, n_seeds=3)
        csv_path = tmp_path / "results.csv"
        harness.export_csv(df, str(csv_path))

        assert csv_path.exists()
        loaded = pd.read_csv(csv_path)
        assert len(loaded) == len(df)

    def test_export_json(self, harness, algorithms, tmp_path):
        """Test JSON export."""
        df = harness.run_full_benchmark(algorithms, n_seeds=3)
        json_path = tmp_path / "results.json"
        harness.export_json(df, str(json_path))

        assert json_path.exists()
        loaded = pd.read_json(json_path)
        assert len(loaded) == len(df)
