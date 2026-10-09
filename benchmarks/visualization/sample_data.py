"""Sample benchmark data loader for testing and demos.

Provides bundled benchmark metrics for visualization testing without
requiring a full benchmark run.
"""

import json
from pathlib import Path
from typing import Optional


class SampleMetrics:
    """Access bundled sample benchmark metrics."""

    _SAMPLE_DIR = Path(__file__).parent / "sample_data"

    @classmethod
    def load_default(cls) -> dict:
        """Load default sample benchmark metrics.

        Returns:
            Dictionary with keys: run_id, dimension, convergence_metrics, etc.

        Raises:
            FileNotFoundError: If sample data not found
        """
        sample_file = cls._SAMPLE_DIR / "benchmark_sample_20260916.json"
        if not sample_file.exists():
            raise FileNotFoundError(
                f"Sample data not found: {sample_file}\n"
                f"Available samples: {list(cls._SAMPLE_DIR.glob('*.json'))}"
            )
        return json.loads(sample_file.read_text())

    @classmethod
    def load(cls, name: str) -> dict:
        """Load sample by filename (without .json extension).

        Args:
            name: Sample name, e.g., 'benchmark_sample_20260916'

        Returns:
            Dictionary with benchmark metrics

        Example:
            >>> metrics = SampleMetrics.load('benchmark_sample_20260916')
            >>> print(metrics['run_id'])
            '20260916-143022'
        """
        if not name.endswith(".json"):
            name = f"{name}.json"

        sample_file = cls._SAMPLE_DIR / name
        if not sample_file.exists():
            available = sorted([f.stem for f in cls._SAMPLE_DIR.glob("*.json")])
            raise FileNotFoundError(
                f"Sample '{name}' not found.\nAvailable: {available}"
            )
        return json.loads(sample_file.read_text())

    @classmethod
    def list_available(cls) -> list[str]:
        """List all available sample datasets.

        Returns:
            List of sample names (without .json)
        """
        return sorted([f.stem for f in cls._SAMPLE_DIR.glob("*.json")])
