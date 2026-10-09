"""Visualization registry and factory for pluggable viz strategies.

Allows registration of new viz backends and routing by chart type + use case.
"""

from typing import Dict, Type

from .base import UseCase, VizStrategy


class VizRegistry:
    """Registry of visualization strategies, keyed by (chart_type, use_case)."""

    # Map: (chart_type, use_case) -> VizStrategy class
    _strategies: Dict[tuple[str, UseCase], Type[VizStrategy]] = {}

    @classmethod
    def register(
        cls,
        chart_type: str,
        use_case: UseCase,
        strategy_class: Type[VizStrategy],
    ):
        """Register a visualization strategy.

        Args:
            chart_type: Name of chart (e.g., 'convergence_curves', 'heatmap')
            use_case: Target use case (DEMO, PUBLICATION, DASHBOARD)
            strategy_class: Class implementing VizStrategy
        """
        key = (chart_type, use_case)
        cls._strategies[key] = strategy_class

    @classmethod
    def get(
        cls,
        chart_type: str,
        use_case: UseCase,
    ) -> VizStrategy:
        """Retrieve registered strategy for chart type + use case.

        Args:
            chart_type: Chart type (e.g., 'convergence_curves')
            use_case: Use case (DEMO, PUBLICATION, DASHBOARD)

        Returns:
            Instantiated VizStrategy

        Raises:
            KeyError: If no strategy registered for (chart_type, use_case)
        """
        key = (chart_type, use_case)
        if key not in cls._strategies:
            available = [k for k in cls._strategies.keys() if k[0] == chart_type]
            raise KeyError(
                f"No strategy registered for {key}. "
                f"Available for '{chart_type}': {[k[1].value for k in available]}"
            )
        strategy_class = cls._strategies[key]
        return strategy_class(use_case=use_case)

    @classmethod
    def list_strategies(cls) -> Dict[str, list[str]]:
        """List all registered strategies by chart type.

        Returns:
            Dict mapping chart_type -> list of use_cases
        """
        result = {}
        for (chart_type, use_case), _ in cls._strategies.items():
            if chart_type not in result:
                result[chart_type] = []
            result[chart_type].append(use_case.value)
        return {k: sorted(v) for k, v in sorted(result.items())}


class VizFactory:
    """Convenience factory for creating visualizations."""

    @staticmethod
    def get(chart_type: str, use_case: UseCase = UseCase.DEMO) -> VizStrategy:
        """Get a visualization strategy.

        Args:
            chart_type: Name of chart (e.g., 'convergence_curves')
            use_case: Target use case (default: DEMO for interactive)

        Returns:
            Instantiated VizStrategy ready to render()

        Example:
            >>> from membrane.benchmarks.visualization import VizFactory, UseCase
            >>> viz = VizFactory.get('convergence_curves', UseCase.DEMO)
            >>> fig = viz.render(metrics_data)
            >>> fig.show()
        """
        return VizRegistry.get(chart_type, use_case)

    @staticmethod
    def list_charts() -> Dict[str, list[str]]:
        """List all available charts and their supported use cases.

        Returns:
            Dict mapping chart_type -> list of use_cases
        """
        return VizRegistry.list_strategies()
