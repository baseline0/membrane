"""Plotly-based interactive visualization strategy.

Generates interactive, browser-based charts for demos, exploration, and dashboards.
Supports hover tooltips, zoom, pan, range sliders, and HTML export.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .base import VizStrategy


class ConvergenceCurvesPlotly(VizStrategy):
    """Interactive convergence curves: algorithm performance across functions.

    Shows convergence ratio (error) on Y-axis, functions on X-axis.
    One line per algorithm. Hover shows exact values.
    """

    def render(self, metrics: dict) -> go.Figure:
        """Render convergence curves from benchmark metrics.

        Args:
            metrics: Dictionary with 'convergence_metrics' list

        Returns:
            Plotly Figure with convergence lines
        """
        convergence_data = metrics.get("convergence_metrics", [])
        if not convergence_data:
            raise ValueError("No convergence_metrics in input data")

        # Group by algorithm
        algorithms = {}
        for entry in convergence_data:
            algo = entry["algorithm"]
            if algo not in algorithms:
                algorithms[algo] = []
            algorithms[algo].append(
                {
                    "function_name": entry["function_name"],
                    "function_id": entry["function_id"],
                    "convergence_ratio": entry["convergence_ratio"],
                    "error_mean": entry["error_mean"],
                }
            )

        # Create figure
        fig = go.Figure()

        # Add one line per algorithm
        for algo_name, data_points in sorted(algorithms.items()):
            # Sort by function_id
            data_points = sorted(data_points, key=lambda x: x["function_id"])

            function_names = [d["function_name"] for d in data_points]
            convergence_ratios = [d["convergence_ratio"] for d in data_points]
            error_means = [d["error_mean"] for d in data_points]

            # Hover text with both convergence_ratio and error
            hover_text = [
                f"<b>{name}</b><br>Convergence: {ratio:.4f}<br>Error: {error:.2f}"
                for name, ratio, error in zip(function_names, convergence_ratios, error_means)
            ]

            fig.add_trace(
                go.Scatter(
                    x=function_names,
                    y=convergence_ratios,
                    mode="lines+markers",
                    name=algo_name,
                    hovertext=hover_text,
                    hoverinfo="text",
                    line=dict(width=2),
                    marker=dict(size=8),
                )
            )

        # Add reference zones (color bands)
        fig.add_hrect(
            y0=0.0,
            y1=0.5,
            fillcolor="green",
            opacity=0.1,
            layer="below",
            annotation_text="Excellent",
            annotation_position="right",
        )
        fig.add_hrect(
            y0=0.5,
            y1=5.0,
            fillcolor="yellow",
            opacity=0.1,
            layer="below",
            annotation_text="Good",
            annotation_position="right",
        )
        fig.add_hrect(
            y0=5.0,
            y1=max([e["convergence_ratio"] for e in convergence_data]) * 1.1 or 10.0,
            fillcolor="red",
            opacity=0.1,
            layer="below",
            annotation_text="Poor",
            annotation_position="right",
        )

        # Update layout
        fig.update_layout(
            title="Algorithm Convergence Curves",
            xaxis_title="Function",
            yaxis_title="Convergence Ratio (error / optimum)",
            hovermode="x unified",
            template="plotly_white",
            height=600,
            yaxis_type="log",  # Log scale for better visibility
        )

        return fig

    @property
    def export_formats(self) -> list[str]:
        """Plotly supports interactive HTML and static exports."""
        return ["html", "png", "svg", "json"]

    def render_and_save(self, metrics: dict, filepath: str):
        """Save figure to file.

        Args:
            metrics: Benchmark data
            filepath: Output path (e.g., 'convergence.html', 'convergence.png')
        """
        fig = self.render(metrics)
        fig.write_html(filepath) if filepath.endswith(".html") else fig.write_image(filepath)


class AlgorithmComparisonPlotly(VizStrategy):
    """Interactive algorithm comparison: scorecard view with bars and gauges.

    Shows mean convergence, success rate, best/worst convergence for each algorithm.
    """

    def render(self, metrics: dict) -> go.Figure:
        """Render algorithm comparison from benchmark metrics.

        Args:
            metrics: Dictionary with 'algorithm_profiles' list

        Returns:
            Plotly Figure with algorithm comparison
        """
        profiles = metrics.get("algorithm_profiles", [])
        if not profiles:
            raise ValueError("No algorithm_profiles in input data")

        # Extract data
        algorithms = [p["algorithm"] for p in profiles]
        mean_convergence = [p["mean_convergence_ratio"] for p in profiles]
        success_rates = [p["success_rate"] * 100 for p in profiles]  # Convert to %

        # Create subplots
        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("Mean Convergence Ratio", "Success Rate (%)"),
            specs=[[{"type": "bar"}, {"type": "bar"}]],
        )

        # Mean convergence
        fig.add_trace(
            go.Bar(
                x=algorithms,
                y=mean_convergence,
                name="Mean Convergence",
                marker_color="lightblue",
                hovertemplate="<b>%{x}</b><br>Mean Convergence: %{y:.4f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        # Success rate
        fig.add_trace(
            go.Bar(
                x=algorithms,
                y=success_rates,
                name="Success Rate",
                marker_color="lightgreen",
                hovertemplate="<b>%{x}</b><br>Success Rate: %{y:.1f}%<extra></extra>",
            ),
            row=1,
            col=2,
        )

        # Update axes
        fig.update_yaxes(title_text="Convergence Ratio", row=1, col=1)
        fig.update_yaxes(title_text="Success Rate (%)", row=1, col=2)

        # Update layout
        fig.update_layout(
            title="Algorithm Performance Comparison",
            height=500,
            showlegend=False,
            template="plotly_white",
        )

        return fig

    @property
    def export_formats(self) -> list[str]:
        return ["html", "png", "svg"]

    def render_and_save(self, metrics: dict, filepath: str):
        """Save comparison figure."""
        fig = self.render(metrics)
        fig.write_html(filepath) if filepath.endswith(".html") else fig.write_image(filepath)
