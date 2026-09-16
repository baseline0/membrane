"""Unit tests for benchmark metrics collection pipeline."""

import json
import tempfile
from pathlib import Path

from benchmarks.metrics_schema import (
    AlgorithmProfile,
    BenchmarkRun,
    ConvergenceMetrics,
    export_benchmark_metrics,
)


class TestConvergenceMetrics:
    """Test ConvergenceMetrics data class."""

    def test_convergence_metrics_creation(self):
        """Create convergence metric and validate fields."""
        metric = ConvergenceMetrics(
            algorithm="GA",
            function_id=1,
            function_name="F1: Sphere",
            dimension=10,
            n_seeds=30,
            mean_result=100.5,
            std_result=0.2,
            best_result=100.0,
            worst_result=101.0,
            median_result=100.25,
            optimum=100.0,
            error_mean=0.5,
            convergence_ratio=0.005,
            timestamp="2026-09-16T14:00:00",
            runtime_seconds=1.23,
        )

        assert metric.algorithm == "GA"
        assert metric.convergence_ratio == 0.005
        assert metric.error_mean == 0.5

    def test_convergence_metrics_serialization(self):
        """Serialize convergence metric to dict."""
        metric = ConvergenceMetrics(
            algorithm="PSO",
            function_id=3,
            function_name="F3: Sum of Different Powers",
            dimension=10,
            n_seeds=30,
            mean_result=300.0,
            std_result=1.0,
            best_result=300.0,
            worst_result=302.0,
            median_result=300.0,
            optimum=300.0,
            error_mean=0.0,
            convergence_ratio=0.0,
            timestamp="2026-09-16T14:00:00",
            runtime_seconds=2.45,
        )

        d = metric.to_dict()
        assert isinstance(d, dict)
        assert d["algorithm"] == "PSO"
        assert d["convergence_ratio"] == 0.0


class TestAlgorithmProfile:
    """Test AlgorithmProfile aggregation."""

    def test_algorithm_profile_creation(self):
        """Create algorithm profile with success rate."""
        profile = AlgorithmProfile(
            algorithm="GA",
            dimension=10,
            n_seeds=30,
            n_functions=29,
            mean_convergence_ratio=0.45,
            best_convergence_ratio=0.001,
            worst_convergence_ratio=2.15,
            functions_within_10x_optimum=22,
            success_rate=0.76,
            ranking={"GA": 1, "PSO": 2},
            timestamp="2026-09-16T14:00:00",
        )

        assert profile.algorithm == "GA"
        assert profile.success_rate == 0.76
        assert profile.ranking["GA"] == 1

    def test_algorithm_profile_success_rate_calculation(self):
        """Success rate should reflect convergence quality."""
        profile = AlgorithmProfile(
            algorithm="GA",
            dimension=10,
            n_seeds=30,
            n_functions=29,
            mean_convergence_ratio=0.5,
            best_convergence_ratio=0.001,
            worst_convergence_ratio=15.0,
            functions_within_10x_optimum=27,
            success_rate=27 / 29,  # 93%
            ranking={},
            timestamp="2026-09-16T14:00:00",
        )

        assert abs(profile.success_rate - 0.931) < 0.01


class TestBenchmarkRun:
    """Test complete benchmark run aggregation."""

    def test_benchmark_run_creation(self):
        """Create complete benchmark run with metrics."""
        metrics = [
            ConvergenceMetrics(
                algorithm="GA",
                function_id=i,
                function_name=f"F{i}",
                dimension=10,
                n_seeds=30,
                mean_result=float(i * 100),
                std_result=1.0,
                best_result=float(i * 100),
                worst_result=float(i * 100 + 5),
                median_result=float(i * 100),
                optimum=float(i * 100),
                error_mean=0.0,
                convergence_ratio=0.0,
                timestamp="2026-09-16T14:00:00",
                runtime_seconds=1.0,
            )
            for i in range(1, 4)
        ]

        profiles = [
            AlgorithmProfile(
                algorithm="GA",
                dimension=10,
                n_seeds=30,
                n_functions=3,
                mean_convergence_ratio=0.0,
                best_convergence_ratio=0.0,
                worst_convergence_ratio=0.0,
                functions_within_10x_optimum=3,
                success_rate=1.0,
                ranking={"GA": 1},
                timestamp="2026-09-16T14:00:00",
            )
        ]

        run = BenchmarkRun(
            run_id="20260916-140000",
            dimension=10,
            n_seeds=30,
            timestamp="2026-09-16T14:00:00",
            convergence_metrics=metrics,
            algorithm_profiles=profiles,
            trends={"ga_converging_well": True},
        )

        assert run.run_id == "20260916-140000"
        assert len(run.convergence_metrics) == 3
        assert len(run.algorithm_profiles) == 1

    def test_benchmark_run_serialization(self):
        """Serialize benchmark run to nested dict."""
        metrics = [
            ConvergenceMetrics(
                algorithm="GA",
                function_id=1,
                function_name="F1",
                dimension=10,
                n_seeds=30,
                mean_result=100.0,
                std_result=0.0,
                best_result=100.0,
                worst_result=100.0,
                median_result=100.0,
                optimum=100.0,
                error_mean=0.0,
                convergence_ratio=0.0,
                timestamp="2026-09-16T14:00:00",
                runtime_seconds=1.0,
            )
        ]

        profiles = [
            AlgorithmProfile(
                algorithm="GA",
                dimension=10,
                n_seeds=30,
                n_functions=1,
                mean_convergence_ratio=0.0,
                best_convergence_ratio=0.0,
                worst_convergence_ratio=0.0,
                functions_within_10x_optimum=1,
                success_rate=1.0,
                ranking={"GA": 1},
                timestamp="2026-09-16T14:00:00",
            )
        ]

        run = BenchmarkRun(
            run_id="test-run",
            dimension=10,
            n_seeds=30,
            timestamp="2026-09-16T14:00:00",
            convergence_metrics=metrics,
            algorithm_profiles=profiles,
            trends={},
        )

        d = run.to_dict()
        assert isinstance(d, dict)
        assert "convergence_metrics" in d
        assert "algorithm_profiles" in d
        assert len(d["convergence_metrics"]) == 1


class TestMetricsExport:
    """Test metrics export pipeline."""

    def test_export_benchmark_metrics_creates_files(self):
        """Export should create multiple JSON files."""
        metrics = [
            ConvergenceMetrics(
                algorithm="GA",
                function_id=1,
                function_name="F1: Sphere",
                dimension=10,
                n_seeds=30,
                mean_result=100.0,
                std_result=0.5,
                best_result=99.5,
                worst_result=100.5,
                median_result=100.0,
                optimum=100.0,
                error_mean=0.0,
                convergence_ratio=0.0,
                timestamp="2026-09-16T14:00:00",
                runtime_seconds=1.0,
            )
        ]

        profiles = [
            AlgorithmProfile(
                algorithm="GA",
                dimension=10,
                n_seeds=30,
                n_functions=1,
                mean_convergence_ratio=0.0,
                best_convergence_ratio=0.0,
                worst_convergence_ratio=0.0,
                functions_within_10x_optimum=1,
                success_rate=1.0,
                ranking={"GA": 1},
                timestamp="2026-09-16T14:00:00",
            )
        ]

        run = BenchmarkRun(
            run_id="test-export",
            dimension=10,
            n_seeds=30,
            timestamp="2026-09-16T14:00:00",
            convergence_metrics=metrics,
            algorithm_profiles=profiles,
            trends={},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            export_benchmark_metrics(run, output_dir)

            # Check files created
            assert (output_dir / "metrics_test-export.json").exists()
            assert (output_dir / "comparison_10d.json").exists()
            assert (output_dir / "trends_GA_10d.json").exists()

    def test_exported_json_is_valid(self):
        """Exported JSON should be parseable and well-formed."""
        metrics = [
            ConvergenceMetrics(
                algorithm="PSO",
                function_id=2,
                function_name="F2: Elliptic",
                dimension=10,
                n_seeds=30,
                mean_result=200.5,
                std_result=1.0,
                best_result=200.0,
                worst_result=201.0,
                median_result=200.5,
                optimum=200.0,
                error_mean=0.5,
                convergence_ratio=0.0025,
                timestamp="2026-09-16T14:00:00",
                runtime_seconds=2.0,
            )
        ]

        profiles = [
            AlgorithmProfile(
                algorithm="PSO",
                dimension=10,
                n_seeds=30,
                n_functions=1,
                mean_convergence_ratio=0.0025,
                best_convergence_ratio=0.0,
                worst_convergence_ratio=0.0025,
                functions_within_10x_optimum=1,
                success_rate=1.0,
                ranking={"PSO": 1},
                timestamp="2026-09-16T14:00:00",
            )
        ]

        run = BenchmarkRun(
            run_id="json-test",
            dimension=10,
            n_seeds=30,
            timestamp="2026-09-16T14:00:00",
            convergence_metrics=metrics,
            algorithm_profiles=profiles,
            trends={"pso_converging_well": True},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            export_benchmark_metrics(run, output_dir)

            # Parse and validate exported JSON
            metrics_file = output_dir / "metrics_json-test.json"
            data = json.loads(metrics_file.read_text())

            assert data["run_id"] == "json-test"
            assert data["dimension"] == 10
            assert len(data["convergence_metrics"]) == 1
            assert data["convergence_metrics"][0]["algorithm"] == "PSO"
