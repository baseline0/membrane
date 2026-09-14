"""Tests for abstract benchmark suite interface."""

import numpy as np
import pytest

from benchmarks.suites.base import BenchmarkFunction


def test_benchmark_function_eval_correct_dimension():
    """Test that BenchmarkFunction validates dimension match."""

    def dummy_func(x):
        return float(np.sum(x**2))

    f = BenchmarkFunction(
        id=1,
        name="Test Function",
        dimension=5,
        bounds=(-100.0, 100.0),
        optimum_value=0.0,
        func=dummy_func,
    )

    x = np.random.uniform(-100, 100, size=5)
    result = f(x)
    assert isinstance(result, float)
    assert result >= 0  # Sum of squares is non-negative


def test_benchmark_function_dimension_mismatch():
    """Test that BenchmarkFunction raises on dimension mismatch."""

    def dummy_func(x):
        return float(np.sum(x**2))

    f = BenchmarkFunction(
        id=1,
        name="Test Function",
        dimension=5,
        bounds=(-100.0, 100.0),
        optimum_value=0.0,
        func=dummy_func,
    )

    x_wrong = np.random.uniform(-100, 100, size=3)
    with pytest.raises(ValueError, match="Dimension mismatch"):
        f(x_wrong)


def test_benchmark_function_is_frozen():
    """Test that BenchmarkFunction dataclass is immutable."""

    def dummy_func(x):
        return float(np.sum(x**2))

    f = BenchmarkFunction(
        id=1,
        name="Test Function",
        dimension=5,
        bounds=(-100.0, 100.0),
        optimum_value=0.0,
        func=dummy_func,
    )

    with pytest.raises((AttributeError, ValueError)):
        f.id = 2
