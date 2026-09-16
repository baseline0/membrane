# Extending the Benchmark Suite

Guide for adding new problem instances, algorithms, and test suites to the benchmark framework.

## Adding New Problem Instances

### 1. Problem Suite Structure

Each problem suite inherits from `BaseProblem` and implements:

```python
class MyProblemSuite:
    """Suite of optimization problems."""

    def list_functions(self, dimension: int) -> list[BaseProblem]:
        """Return problems at given dimensionality."""
        return [MyProblem1(dimension), MyProblem2(dimension), ...]

    def validate_dimension(self, dimension: int) -> None:
        """Check if dimension is supported."""
        if dimension not in self.supported_dimensions:
            raise ValueError(f"Unsupported: {dimension}")
```

### 2. Problem Definition

Each problem implements:

```python
class MyProblem(BaseProblem):
    """Single optimization problem."""

    def __init__(self, dimension: int):
        self.id = 101  # Unique ID for this suite
        self.name = "My Problem"
        self.dimension = dimension
        self.bounds = [(-5.0, 5.0)] * dimension

    def evaluate(self, x: list[float]) -> float:
        """Fitness evaluation. Lower is better."""
        return sum(xi ** 2 for xi in x)

    @property
    def optimum(self) -> float:
        """Global optimum fitness value."""
        return 0.0
```

### 3. Register Suite in Harness

Update `BenchmarkHarness` to load your suite:

```python
def __init__(self, suite: BaseSuite, strict: bool = False):
    self.suite = suite
    # Suite.list_functions() called by run_algorithm_on_problem()
```

## Adding New Algorithms

### 1. Algorithm Interface

Inherit from `BaseAlgorithm`:

```python
class MyAlgorithm(BaseAlgorithm):
    """Custom optimization algorithm."""

    def __init__(self, pop_size: int = 50, generations: int = 200):
        self.pop_size = pop_size
        self.generations = generations

    def solve(self, problem: BaseProblem, seed: int = 42) -> float:
        """
        Optimize problem for N generations.

        Args:
            problem: Optimization problem instance
            seed: Random seed for reproducibility

        Returns:
            Best fitness found
        """
        # Initialization
        rng = np.random.RandomState(seed)
        population = self._initialize(problem, rng)
        best = min(problem.evaluate(p) for p in population)

        # Evolution loop
        for gen in range(self.generations):
            population = self._step(population, problem, rng)
            best = min(best, min(problem.evaluate(p) for p in population))

        return best

    def _initialize(self, problem: BaseProblem, rng):
        """Create initial population."""
        return [rng.uniform(*problem.bounds) for _ in range(self.pop_size)]

    def _step(self, population, problem, rng):
        """Single evolution step. Return new population."""
        raise NotImplementedError
```

### 2. Parameter Tuning

Algorithms should expose key hyperparameters:

```python
class MyAlgorithm(BaseAlgorithm):
    def __init__(
        self,
        pop_size: int = 50,
        generations: int = 200,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
    ):
        """All hyperparams explicit; supports tuning via grid search."""
```

### 3. Register in Benchmark

Add to comparison set:

```python
# benchmarks/run_example.py
algorithms = {
    "GA": GeneticAlgorithm(pop_size=100, generations=300),
    "PSO": ParticleSwarmOptimizer(pop_size=50, generations=300),
    "MyAlgorithm": MyAlgorithm(pop_size=75, generations=250),
}
```

## Running Comparisons

### Quick Comparison (Testing)

```bash
# Test mode: relaxed validation
just bench-example  # 3 seeds, 5 functions, 10D
```

### Publication-Ready (Strict)

```bash
# Strict mode: 30 seeds, full validation
just bench-full  # 30 seeds, 29 functions, 10D (~1-2 hours)
```

### Custom Runs

```bash
# n_seeds n_functions dimension
uv run python -m benchmarks.run_example 30 10 30
```

**Auto Mode Detection:**
- `n_seeds < 30` → Testing mode (relaxed validation)
- `n_seeds ≥ 30` → Strict mode (Wilcoxon-ready, publication)

## Exporting Results

### CSV Export (Existing)

```python
df = main(n_seeds=30, n_functions=29, dimension=10)
out_csv = Path("benchmarks_example.csv")
harness.export_csv(df, str(out_csv))
```

### Dashboard Metrics Export (New)

```bash
just bench-full      # Generate benchmarks_example.csv
just bench-metrics   # Parse CSV → metrics/*.json
```

Outputs:
- `benchmarks/metrics/metrics_*.json` — Full run data
- `benchmarks/metrics/comparison_*.json` — Algorithm comparison
- `benchmarks/metrics/trends_*.json` — Per-algorithm trends

## Validation Framework

### Seed Validation

```python
from benchmarks.validators import validate_n_seeds

# Testing: skip validation with test_mode=True
validate_n_seeds(n_seeds=5, test_mode=True)  # ✓ Passes

# Publication: require 30+ seeds
validate_n_seeds(n_seeds=30, test_mode=False)  # ✓ Passes
validate_n_seeds(n_seeds=5, test_mode=False)   # ✗ Raises error
```

### Result Bounds Validation

```python
from benchmarks.validators import validate_result_bounds

# CEC2017: result must be within ±10x optimum
validate_result_bounds(result=1050, func_id=10, dimension=10)  # ✓ Pass
# (optimum=1000, bounds=[100, 10000], result=1050 ∈ bounds)

validate_result_bounds(result=15000, func_id=10, dimension=10)  # ✗ Fail
```

## Performance Tips

### 1. Use Appropriate Dimensions

- **Development:** 10D (fast, representative)
- **Medium Testing:** 30D (2-3x slower)
- **Publication:** 50D+ (comprehensive but slow)

### 2. Parallel Runs

Harness supports vectorized evaluation:

```python
# Problem evaluations can be parallelized
problem.evaluate(x1)  # Sequential (current)
problem.evaluate_batch([x1, x2, x3])  # Parallel (future)
```

### 3. Caching

Problem evaluations are stateless; cache if needed:

```python
@lru_cache(maxsize=10000)
def evaluate(self, x: tuple) -> float:
    """Memoize expensive evaluations."""
    return expensive_objective(x)
```

## Example: Custom Problem Suite

```python
# benchmarks/suites/my_problems.py

from benchmarks.harness import BaseProblem, BaseSuite

class Sphere(BaseProblem):
    id = 201
    name = "Sphere"
    optimum = 0.0

    def evaluate(self, x):
        return sum(xi ** 2 for xi in x)

class Rastrigin(BaseProblem):
    id = 202
    name = "Rastrigin"
    optimum = 0.0

    def evaluate(self, x):
        A = 10
        n = len(x)
        return A * n + sum(xi ** 2 - A * np.cos(2 * np.pi * xi) for xi in x)

class MyProblemSuite(BaseSuite):
    def list_functions(self, dimension):
        return [Sphere(dimension), Rastrigin(dimension)]

    def validate_dimension(self, dimension):
        if dimension <= 0:
            raise ValueError(f"Dimension must be > 0, got {dimension}")
```

Usage:

```python
# benchmarks/run_custom.py
from benchmarks.suites.my_problems import MyProblemSuite

suite = MyProblemSuite()
harness = BenchmarkHarness(suite, strict=True)
algorithms = {"GA": GeneticAlgorithm(), "PSO": ParticleSwarmOptimizer()}

for func in suite.list_functions(10):
    for alg_name, alg in algorithms.items():
        stats = harness.run_algorithm_on_problem(alg, func, n_seeds=30)
        print(f"{func.name} + {alg_name}: {stats['mean']:.2e}")
```

## Integration with Dashboard

Benchmark metrics feed into fleet dashboard as observable performance trends:

1. **Algorithm Performance** — Convergence ratio trends over time
2. **Suite Coverage** — Which problems are solved well, which are hard
3. **Hyperparameter Effects** — How gen/pop changes impact results
4. **Version Comparison** — Side-by-side algorithm comparisons

See `benchmarks/DASHBOARD_METRICS.md` for full spec.
