"""Abstract base classes for benchmark suites."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class BenchmarkFunction:
    """Represents a single optimization problem instance."""

    id: int | str
    name: str
    dimension: int
    bounds: tuple[float, float]
    optimum_value: float
    func: Callable[[npt.NDArray[np.float64]], float]

    def __call__(self, x: npt.NDArray[np.float64]) -> float:
        """Evaluate candidate vector x."""
        x_arr = np.asarray(x, dtype=np.float64)
        if x_arr.shape[-1] != self.dimension:
            raise ValueError(f"Dimension mismatch for {self.name}: expected {self.dimension}, got {x_arr.shape[-1]}")
        return float(self.func(x_arr))


class BenchmarkSuite(ABC):
    """Abstract base class for optimization benchmark suites."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the benchmark suite."""
        ...

    @property
    @abstractmethod
    def supported_dimensions(self) -> list[int]:
        """Supported problem dimensions (e.g., [10, 30, 50])."""
        ...

    @abstractmethod
    def get_function(self, func_id: int | str, dimension: int) -> BenchmarkFunction:
        """Retrieve a specific benchmark function by ID and dimension."""
        ...

    @abstractmethod
    def list_functions(self, dimension: int) -> list[BenchmarkFunction]:
        """List all benchmark functions available for a given dimension."""
        ...
