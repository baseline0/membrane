"""Pluggable visualization system for benchmark metrics.

Enables selection of visualization backend (Plotly, Matplotlib, Altair)
based on use case (demo, publication, dashboard).

Usage:
    from membrane.benchmarks.visualization import VizFactory, UseCase, SampleMetrics

    # Load sample data
    metrics = SampleMetrics.load_default()

    # Interactive demo
    viz = VizFactory.get('convergence_curves', UseCase.DEMO)
    fig = viz.render(metrics)
    fig.show()

    # Publication quality
    viz = VizFactory.get('convergence_curves', UseCase.PUBLICATION)
    viz.render_and_save(metrics, 'figure_1.pdf')

Architecture:
    VizStrategy (base)
        ├─ ConvergenceCurvesPlotly
        ├─ AlgorithmComparisonPlotly
        ├─ ConvergenceCurvesMatplotlib (forthcoming)
        └─ ...

    VizRegistry: Maps (chart_type, use_case) → strategy class
    VizFactory: Convenience getter
    SampleMetrics: Bundled sample data loader
"""

from .base import UseCase, VizStrategy
from .plotly_interactive import AlgorithmComparisonPlotly, ConvergenceCurvesPlotly
from .registry import VizFactory, VizRegistry
from .sample_data import SampleMetrics

# Register default strategies
VizRegistry.register("convergence_curves", UseCase.DEMO, ConvergenceCurvesPlotly)
VizRegistry.register("convergence_curves", UseCase.DASHBOARD, ConvergenceCurvesPlotly)

VizRegistry.register("algorithm_comparison", UseCase.DEMO, AlgorithmComparisonPlotly)
VizRegistry.register("algorithm_comparison", UseCase.DASHBOARD, AlgorithmComparisonPlotly)

__all__ = [
    "VizFactory",
    "VizRegistry",
    "VizStrategy",
    "UseCase",
    "SampleMetrics",
    "ConvergenceCurvesPlotly",
    "AlgorithmComparisonPlotly",
]
