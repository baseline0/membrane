# Benchmarking Implementation Spec: CEC2017 & Baseline Integration

## Why CEC2017 (Still, in 2025)

- **Reproducibility:** 80% of MIEA papers (2018–2026) use CEC2017 as baseline
- **Hard benchmark mechanics:** Rotated, shifted, hybrid, and composition functions eliminate axis-aligned cheating
- **Direct comparability:** Published results from competitors available for sanity checks
- **The caveat:** CEC2022/CEC2024 exist, but abstract interface design lets us add them without harness changes

**Decision:** Implement CEC2017 first with abstract `BenchmarkSuite` interface. Dropping in `cec2022.py` later requires zero changes to `harness.py`.

---

## Architecture: Abstract Suite Interface

### 1. Base Class (`benchmarks/suites/base.py`)

Provides abstraction layer so `harness.py` works agnostically with any suite:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable
import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class BenchmarkFunction:
    """Single optimization problem instance."""

    id: int | str
    name: str
    dimension: int
    bounds: tuple[float, float]
    optimum_value: float
    func: Callable[[npt.NDArray[np.float64]], float]

    def __call__(self, x: npt.NDArray[np.float64]) -> float:
        x_arr = np.asarray(x, dtype=np.float64)
        if x_arr.shape[-1] != self.dimension:
            raise ValueError(f"Dimension mismatch: expected {self.dimension}, got {x_arr.shape[-1]}")
        return float(self.func(x_arr))


class BenchmarkSuite(ABC):
    """Abstract base for optimization benchmark suites."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of suite (e.g., 'CEC2017')."""
        ...

    @property
    @abstractmethod
    def supported_dimensions(self) -> list[int]:
        """Supported dimensions (e.g., [10, 30, 50])."""
        ...

    @abstractmethod
    def get_function(self, func_id: int | str, dimension: int) -> BenchmarkFunction:
        """Retrieve specific function by ID and dimension."""
        ...

    @abstractmethod
    def list_functions(self, dimension: int) -> list[BenchmarkFunction]:
        """List all functions for a dimension."""
        ...
```

### 2. CEC2017 Implementation (`benchmarks/suites/cec2017.py`)

Uses `ctypes` to bind to compiled C library (ensures numerical parity with published papers):

```python
import ctypes
from pathlib import Path
import numpy as np
import numpy.typing as npt
from benchmarks.suites.base import BenchmarkFunction, BenchmarkSuite


CEC2017_NAMES: dict[int, str] = {
    1: "Shifted and Rotated Bent Cigar Function",
    3: "Shifted and Rotated Rosenbrock's Function",
    4: "Shifted and Rotated Rastrigin's Function",
    # ... (F1–F30, excluding F2 which was removed)
}


class CEC2017CBinding:
    """ctypes wrapper around libcec2017 shared library."""

    def __init__(self, lib_path: Path):
        if not lib_path.exists():
            raise FileNotFoundError(f"libcec2017.so not found at {lib_path}")

        self.lib = ctypes.CDLL(str(lib_path.resolve()))
        self._test_func = self.lib.cec17_test_func
        self._test_func.argtypes = [
            ctypes.POINTER(ctypes.c_double),  # x
            ctypes.POINTER(ctypes.c_double),  # f
            ctypes.c_int,  # nx (dimension)
            ctypes.c_int,  # mx (num vectors)
            ctypes.c_int,  # func_num
        ]
        self._test_func.restype = None

    def evaluate(self, x: npt.NDArray[np.float64], func_num: int) -> float:
        """Evaluate x on function func_num."""
        nx = len(x)
        f = np.zeros(1, dtype=np.float64)

        x_ptr = x.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        f_ptr = f.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        self._test_func(x_ptr, f_ptr, nx, 1, func_num)
        return float(f[0])


class CEC2017Suite(BenchmarkSuite):
    """CEC2017 Special Session Benchmark Suite."""

    DEFAULT_LIB_DIR = Path("benchmarks/c_src/cec2017")

    def __init__(self, lib_dir: Path | None = None):
        self._lib_dir = lib_dir or self.DEFAULT_LIB_DIR
        lib_file = self._lib_dir / "libcec2017.so"
        self._binding = CEC2017CBinding(lib_file)

    @property
    def name(self) -> str:
        return "CEC2017"

    @property
    def supported_dimensions(self) -> list[int]:
        return [10, 30, 50, 100]

    def get_function(self, func_id: int | str, dimension: int) -> BenchmarkFunction:
        fid = int(func_id)
        if dimension not in self.supported_dimensions:
            raise ValueError(f"Dimension {dimension} not in {self.supported_dimensions}")
        if fid not in CEC2017_NAMES:
            raise ValueError(f"Function F{fid} not in CEC2017")

        optimum = float(fid * 100)  # Theoretical global minimum

        def eval_wrapper(x: npt.NDArray[np.float64]) -> float:
            return self._binding.evaluate(x, fid)

        return BenchmarkFunction(
            id=fid,
            name=f"F{fid}: {CEC2017_NAMES[fid]}",
            dimension=dimension,
            bounds=(-100.0, 100.0),
            optimum_value=optimum,
            func=eval_wrapper,
        )

    def list_functions(self, dimension: int) -> list[BenchmarkFunction]:
        return [self.get_function(fid, dimension) for fid in sorted(CEC2017_NAMES.keys())]
```

---

## Build & Compilation

### Add to `justfile`

```just
# Compile CEC2017 C source into shared library
build-cec2017:
    @echo "Building CEC2017 shared library..."
    mkdir -p benchmarks/c_src/cec2017
    gcc -shared -fPIC -O3 \
        benchmarks/c_src/cec2017/cec17_test_func.c \
        -o benchmarks/c_src/cec2017/libcec2017.so -lm
    @echo "✓ libcec2017.so built successfully"

# Run on first setup
setup-benchmarks: build-cec2017
    @echo "Benchmarking framework ready"
```

### Verification Test

```python
# benchmarks/test_cec2017.py
import numpy as np
from benchmarks.suites.cec2017 import CEC2017Suite


def test_cec2017_load_and_eval():
    suite = CEC2017Suite()
    f1 = suite.get_function(1, dimension=10)

    assert f1.name == "F1: Shifted and Rotated Bent Cigar Function"
    assert f1.bounds == (-100.0, 100.0)
    assert f1.optimum_value == 100.0

    x = np.random.uniform(-100, 100, size=10)
    result = f1(x)
    assert isinstance(result, float)
    assert result >= f1.optimum_value  # Should be at or above optimum
```

---

## Baseline Algorithms

### GA Baseline (`benchmarks/baselines/ga.py`)

Standard genetic algorithm using DEAP:

```python
from deap import base, creator, tools, algorithms
import numpy as np
import numpy.typing as npt
from benchmarks.suites.base import BenchmarkFunction


class GeneticAlgorithm:
    """Standard GA baseline."""

    def __init__(self, pop_size: int = 100, generations: int = 1000, cxpb: float = 0.7, mutpb: float = 0.2):
        self.pop_size = pop_size
        self.generations = generations
        self.cxpb = cxpb
        self.mutpb = mutpb

    def optimize(self, problem: BenchmarkFunction, seed: int | None = None) -> float:
        """Run GA on problem, return best fitness found."""
        if seed is not None:
            np.random.seed(seed)

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        toolbox = base.Toolbox()
        toolbox.register("attr_float", np.random.uniform, *problem.bounds)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=problem.dimension)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", lambda x: (problem(np.array(x)),))
        toolbox.register("mate", tools.cxBlend, alpha=0.5)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
        toolbox.register("select", tools.selBest)

        pop = toolbox.population(n=self.pop_size)
        pop, logbook = algorithms.eaSimple(
            pop, toolbox, cxpb=self.cxpb, mutpb=self.mutpb, ngen=self.generations, verbose=False
        )

        return min([ind.fitness.values[0] for ind in pop])
```

### PSO Baseline (`benchmarks/baselines/pso.py`)

Particle Swarm Optimization:

```python
import numpy as np
from benchmarks.suites.base import BenchmarkFunction


class ParticleSwarmOptimizer:
    """Standard PSO baseline."""

    def __init__(self, pop_size: int = 30, generations: int = 1000, w: float = 0.7, c1: float = 1.5, c2: float = 1.5):
        self.pop_size = pop_size
        self.generations = generations
        self.w = w
        self.c1 = c1
        self.c2 = c2

    def optimize(self, problem: BenchmarkFunction, seed: int | None = None) -> float:
        """Run PSO on problem."""
        if seed is not None:
            np.random.seed(seed)

        # Initialize particles and velocities
        particles = np.random.uniform(*problem.bounds, size=(self.pop_size, problem.dimension))
        velocities = np.random.uniform(-1, 1, size=(self.pop_size, problem.dimension))

        # Fitness evaluation
        fitness = np.array([problem(p) for p in particles])
        best_idx = np.argmin(fitness)
        global_best_pos = particles[best_idx].copy()
        global_best_fit = fitness[best_idx]

        # PSO loop
        for _ in range(self.generations):
            for i in range(self.pop_size):
                r1, r2 = np.random.random((2, problem.dimension))
                velocities[i] = (
                    self.w * velocities[i]
                    + self.c1 * r1 * (particles[i] - particles[i])
                    + self.c2 * r2 * (global_best_pos - particles[i])
                )
                particles[i] += velocities[i]
                particles[i] = np.clip(particles[i], *problem.bounds)

                fit = problem(particles[i])
                if fit < global_best_fit:
                    global_best_fit = fit
                    global_best_pos = particles[i].copy()

        return global_best_fit
```

---

## Unified Harness (`benchmarks/harness.py`)

Orchestrates all algorithms, collects 30-seed statistics, computes Wilcoxon tests:

```python
from pathlib import Path
from typing import Callable
import numpy as np
import pandas as pd
from scipy import stats
from multiprocessing import Pool

from benchmarks.suites.base import BenchmarkSuite, BenchmarkFunction
from benchmarks.baselines import GeneticAlgorithm, ParticleSwarmOptimizer


class BenchmarkHarness:
    """Unified runner for 30+ seed experiments with statistical analysis."""

    def __init__(self, suite: BenchmarkSuite):
        self.suite = suite

    def run_single_seed(self, algorithm: Callable, problem: BenchmarkFunction, seed: int) -> float:
        """Run one algorithm on one problem with one seed."""
        return algorithm.optimize(problem, seed=seed)

    def run_algorithm_on_problem(self, algorithm: Callable, problem: BenchmarkFunction, n_seeds: int = 30) -> dict:
        """Run algorithm on problem for n_seeds times, return stats."""
        results = [self.run_single_seed(algorithm, problem, seed) for seed in range(n_seeds)]
        return {
            "mean": float(np.mean(results)),
            "std": float(np.std(results)),
            "median": float(np.median(results)),
            "best": float(np.min(results)),
            "worst": float(np.max(results)),
            "error_mean": float(np.mean(results) - problem.optimum_value),
            "results": results,
        }

    def wilcoxon_test(self, results1: list[float], results2: list[float]) -> dict:
        """Pairwise Wilcoxon signed-rank test (non-parametric)."""
        statistic, p_value = stats.wilcoxon(results1, results2)
        return {"statistic": float(statistic), "p_value": float(p_value), "significant": p_value < 0.05}

    def run_full_benchmark(self, algorithms: dict[str, Callable], n_seeds: int = 30) -> pd.DataFrame:
        """Run all algorithms on all functions, return comparison DataFrame."""
        results = []

        for dimension in self.suite.supported_dimensions:
            functions = self.suite.list_functions(dimension)
            for func in functions:
                for alg_name, alg in algorithms.items():
                    stats_dict = self.run_algorithm_on_problem(alg, func, n_seeds=n_seeds)
                    results.append(
                        {
                            "dimension": dimension,
                            "function": func.name,
                            "algorithm": alg_name,
                            "mean": stats_dict["mean"],
                            "std": stats_dict["std"],
                            "error_mean": stats_dict["error_mean"],
                        }
                    )

        return pd.DataFrame(results)
```

---

## 4-Week Sprint

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | CEC2017 suite + baselines | `cec2017.py`, `ga.py`, `pso.py`, `build-cec2017` in justfile |
| 2 | Harness + CSV/JSON export | `harness.py`, `BenchmarkHarness` class, export templates |
| 3 | Malta integration | `malta/fuzzy.py`, integrate as baseline in harness |
| 4 | Run experiments + publish | Execute 30-seed runs, generate Pareto plots, sample paper tables |

---

## Success Criteria

- ✓ CEC2017 loads without crashing (`just build-cec2017` works)
- ✓ GA + PSO baselines converge on F1–F5 (sanity check)
- ✓ Harness generates CSV with 30 seeds × 30 functions × 3 algorithms
- ✓ Wilcoxon test identifies significant differences
- ✓ Pareto frontier visualization (accuracy vs computation time)
- ✓ Malta results ready for first paper (empirical benchmark comparison)
