"""Tests for baseline algorithms (GA, PSO)."""

import numpy as np
import pytest

from benchmarks.baselines.ga import GeneticAlgorithm
from benchmarks.baselines.pso import ParticleSwarmOptimizer
from benchmarks.suites.base import BenchmarkFunction


@pytest.fixture
def sphere_function() -> BenchmarkFunction:
    """Simple sphere function (sum of squares) for testing."""

    def sphere(x):
        return float(np.sum(x**2))

    return BenchmarkFunction(
        id="sphere",
        name="Sphere Function",
        dimension=5,
        bounds=(-5.0, 5.0),
        optimum_value=0.0,
        func=sphere,
    )


@pytest.fixture
def rosenbrock_function() -> BenchmarkFunction:
    """Rosenbrock function for testing."""

    def rosenbrock(x):
        return float(np.sum(100 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2))

    return BenchmarkFunction(
        id="rosenbrock",
        name="Rosenbrock Function",
        dimension=5,
        bounds=(-2.0, 2.0),
        optimum_value=0.0,
        func=rosenbrock,
    )


class TestGeneticAlgorithm:
    def test_ga_optimize_returns_float(self, sphere_function):
        """Test that GA optimize returns a float."""
        ga = GeneticAlgorithm(pop_size=20, generations=10)
        result = ga.optimize(sphere_function, seed=42)
        assert isinstance(result, float)

    def test_ga_optimize_with_seed_reproducible(self, sphere_function):
        """Test that GA with same seed produces same result."""
        ga = GeneticAlgorithm(pop_size=20, generations=10)
        result1 = ga.optimize(sphere_function, seed=42)
        result2 = ga.optimize(sphere_function, seed=42)
        assert result1 == result2

    def test_ga_finds_reasonable_solution(self, sphere_function):
        """Test that GA finds a reasonable solution on sphere function."""
        ga = GeneticAlgorithm(pop_size=50, generations=100)
        result = ga.optimize(sphere_function, seed=42)
        assert result < 10.0  # Should find something better than random


class TestParticleSwarmOptimizer:
    def test_pso_optimize_returns_float(self, sphere_function):
        """Test that PSO optimize returns a float."""
        pso = ParticleSwarmOptimizer(pop_size=20, generations=10)
        result = pso.optimize(sphere_function, seed=42)
        assert isinstance(result, float)

    def test_pso_optimize_with_seed_reproducible(self, sphere_function):
        """Test that PSO with same seed produces same result."""
        pso = ParticleSwarmOptimizer(pop_size=20, generations=10)
        result1 = pso.optimize(sphere_function, seed=42)
        result2 = pso.optimize(sphere_function, seed=42)
        assert result1 == result2

    def test_pso_finds_reasonable_solution(self, sphere_function):
        """Test that PSO finds a reasonable solution on sphere function."""
        pso = ParticleSwarmOptimizer(pop_size=30, generations=100)
        result = pso.optimize(sphere_function, seed=42)
        assert result < 10.0  # Should find something better than random
