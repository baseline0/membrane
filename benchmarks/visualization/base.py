"""Abstract base class for visualization strategies.

All visualization implementations inherit from VizStrategy and implement
the render() method. This allows pluggable viz backends (Plotly, Matplotlib,
Altair) selected by use case (demo, publication, dashboard).
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class UseCase(Enum):
    """Categorizes visualization intent and selects appropriate backend."""

    DEMO = "demo"  # Interactive, browser-based, for demos/exploration
    PUBLICATION = "publication"  # Static, high-quality, for papers/reports
    DASHBOARD = "dashboard"  # Embeddable, JSON-based, for web dashboards


class VizStrategy(ABC):
    """Abstract base for any visualization strategy.

    Subclasses implement render() to return backend-specific objects
    (Plotly Figure, Matplotlib Figure, Altair Chart, etc.).
    """

    def __init__(self, use_case: UseCase = UseCase.DEMO):
        """Initialize strategy with use case context.

        Args:
            use_case: Determines backend and styling (DEMO, PUBLICATION, DASHBOARD)
        """
        self.use_case = use_case

    @abstractmethod
    def render(self, metrics: dict) -> Any:
        """Render visualization from benchmark metrics.

        Args:
            metrics: Dictionary with benchmark data (convergence_metrics, algorithm_profiles, etc.)

        Returns:
            Backend-specific object (Plotly Figure, Matplotlib Figure, Altair Chart, etc.)
        """
        pass

    @property
    @abstractmethod
    def export_formats(self) -> list[str]:
        """Supported export formats for this strategy.

        Returns:
            List of format strings: ['html'], ['pdf', 'png'], ['json'], etc.
        """
        pass

    def render_and_show(self, metrics: dict):
        """Render and display (interactive mode).

        Default implementation calls render(). Subclasses override if needed.
        """
        return self.render(metrics)

    def render_and_save(self, metrics: dict, filepath: str):
        """Render and save to file (publication mode).

        Default implementation raises NotImplementedError.
        Subclasses override to implement save logic.

        Args:
            metrics: Benchmark data
            filepath: Path to save (e.g., 'figure.pdf', 'chart.json')
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support save(). "
            f"Supported formats: {self.export_formats}"
        )
