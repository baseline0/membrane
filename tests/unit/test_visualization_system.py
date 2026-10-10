"""Tests for pluggable visualization system.

Verifies:
- Registry registration and retrieval
- Strategy instantiation with use case
- Sample data loading
- Render output types
"""

import pytest

from benchmarks.visualization import (
    AlgorithmComparisonPlotly,
    ConvergenceCurvesPlotly,
    SampleMetrics,
    UseCase,
    VizFactory,
    VizRegistry,
)


class TestSampleMetrics:
    """Test sample data loading."""

    def test_load_default(self):
        """Load default sample data."""
        metrics = SampleMetrics.load_default()
        assert "run_id" in metrics
        assert "convergence_metrics" in metrics
        assert len(metrics["convergence_metrics"]) > 0

    def test_list_available(self):
        """List available samples."""
        samples = SampleMetrics.list_available()
        assert isinstance(samples, list)
        assert len(samples) > 0
        assert "benchmark_sample_20260916" in samples


class TestVizRegistry:
    """Test visualization registry."""

    def test_register_and_get(self):
        """Register and retrieve strategy."""
        VizRegistry.register("test_chart", UseCase.DEMO, ConvergenceCurvesPlotly)
        strategy = VizRegistry.get("test_chart", UseCase.DEMO)
        assert isinstance(strategy, ConvergenceCurvesPlotly)
        assert strategy.use_case == UseCase.DEMO

    def test_list_strategies(self):
        """List all registered strategies."""
        strategies = VizRegistry.list_strategies()
        assert "convergence_curves" in strategies
        assert "algorithm_comparison" in strategies
        assert "demo" in strategies["convergence_curves"]

    def test_get_missing_raises_keyerror(self):
        """Missing strategy raises KeyError."""
        with pytest.raises(KeyError, match="No strategy registered"):
            VizRegistry.get("nonexistent_chart", UseCase.DEMO)


class TestVizFactory:
    """Test convenience factory."""

    def test_get_convergence_curves(self):
        """Factory retrieves convergence curves strategy."""
        viz = VizFactory.get("convergence_curves", UseCase.DEMO)
        assert isinstance(viz, ConvergenceCurvesPlotly)

    def test_get_algorithm_comparison(self):
        """Factory retrieves algorithm comparison strategy."""
        viz = VizFactory.get("algorithm_comparison", UseCase.DEMO)
        assert isinstance(viz, AlgorithmComparisonPlotly)

    def test_list_charts(self):
        """Factory lists available charts."""
        charts = VizFactory.list_charts()
        assert "convergence_curves" in charts
        assert "algorithm_comparison" in charts


class TestConvergenceCurvesPlotly:
    """Test convergence curves visualization."""

    def test_render_returns_figure(self):
        """Render returns Plotly Figure."""
        metrics = SampleMetrics.load_default()
        viz = ConvergenceCurvesPlotly(use_case=UseCase.DEMO)
        fig = viz.render(metrics)

        # Plotly Figure object
        assert hasattr(fig, "show")
        assert hasattr(fig, "write_html")

    def test_render_with_empty_data_raises(self):
        """Render with no convergence data raises ValueError."""
        viz = ConvergenceCurvesPlotly()
        with pytest.raises(ValueError, match="No convergence_metrics"):
            viz.render({})

    def test_export_formats(self):
        """Plotly supports multiple export formats."""
        viz = ConvergenceCurvesPlotly()
        formats = viz.export_formats
        assert "html" in formats
        assert "png" in formats


class TestAlgorithmComparisonPlotly:
    """Test algorithm comparison visualization."""

    def test_render_returns_figure(self):
        """Render returns Plotly Figure."""
        metrics = SampleMetrics.load_default()
        viz = AlgorithmComparisonPlotly(use_case=UseCase.DEMO)
        fig = viz.render(metrics)

        assert hasattr(fig, "show")
        assert hasattr(fig, "write_html")

    def test_render_with_empty_data_raises(self):
        """Render with no algorithm profiles raises ValueError."""
        viz = AlgorithmComparisonPlotly()
        with pytest.raises(ValueError, match="No algorithm_profiles"):
            viz.render({})


class TestUseCase:
    """Test use case enum."""

    def test_use_case_values(self):
        """Use case enum has expected values."""
        assert UseCase.DEMO.value == "demo"
        assert UseCase.PUBLICATION.value == "publication"
        assert UseCase.DASHBOARD.value == "dashboard"
