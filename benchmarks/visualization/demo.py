#!/usr/bin/env python
"""Quick demo of pluggable visualization system.

Run this to generate interactive visualizations from sample data:
    python -m benchmarks.visualization.demo

Generates, under generated/visualization/:
    - convergence_curves_demo.html (interactive plot)
    - algorithm_comparison_demo.html (interactive comparison)
"""

from pathlib import Path

from .registry import VizFactory
from .base import UseCase
from .sample_data import SampleMetrics


def main(output_dir: Path = Path("generated/visualization")):
    """Generate demo visualizations into output_dir (gitignored by default)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    # Load sample metrics
    print("📊 Loading sample benchmark metrics...")
    metrics = SampleMetrics.load_default()
    print(f"   ✓ Loaded: {metrics['run_id']}")
    print(f"   - Algorithms: {set(m['algorithm'] for m in metrics['convergence_metrics'])}")
    print(f"   - Functions tested: {len(set(m['function_id'] for m in metrics['convergence_metrics']))}")

    # Demo 1: Convergence curves (interactive)
    print("\n📈 Generating convergence curves...")
    viz = VizFactory.get("convergence_curves", UseCase.DEMO)
    fig = viz.render(metrics)
    output_1 = output_dir / "convergence_curves_demo.html"
    fig.write_html(str(output_1))
    print(f"   ✓ Saved: {output_1}")

    # Demo 2: Algorithm comparison (interactive)
    print("\n📊 Generating algorithm comparison...")
    viz = VizFactory.get("algorithm_comparison", UseCase.DEMO)
    fig = viz.render(metrics)
    output_2 = output_dir / "algorithm_comparison_demo.html"
    fig.write_html(str(output_2))
    print(f"   ✓ Saved: {output_2}")

    # Info
    print("\n✨ Demo complete!")
    print(f"   Open in browser:")
    print(f"     - {output_1.absolute()}")
    print(f"     - {output_2.absolute()}")
    print(f"\n   Available charts:")
    for chart_type, use_cases in sorted(VizFactory.list_charts().items()):
        print(f"     - {chart_type}: {', '.join(use_cases)}")


if __name__ == "__main__":
    main()
