# Reproducible Experiments Guide

This guide shows how to run reproducible benchmark experiments using the unified CLI.

## Quick Start

### Toy Problem Benchmarks

Test on standard functions (Sphere, Rastrigin, Rosenbrock, Ackley):

```bash
# Quick test: 2D, 10 generations
python -m malta.cli.main benchmark toy --n-dims 2 --n-generations 10

# With output
python -m malta.cli.main benchmark toy \
  --n-dims 3 \
  --n-generations 30 \
  --output results/toy_3d.json
```

### CEC2017 Benchmarks

Full benchmark on CEC2017 functions:

```bash
# Quick validation: 3 functions, 10D, 10 seeds
python -m malta.cli.main benchmark cec2017 \
  --n-functions 3 \
  --dimension 10 \
  --n-seeds 10

# With results saved
python -m malta.cli.main benchmark cec2017 \
  --n-functions 5 \
  --dimension 10 \
  --n-seeds 30 \
  --output-dir results/cec2017

# Include baseline algorithms (slower)
python -m malta.cli.main benchmark cec2017 \
  --n-functions 3 \
  --dimension 10 \
  --n-seeds 30 \
  --include-baselines
```

## Reproducibility

### Seeding

All experiments use fixed seeds (42 for toy benchmarks, 0-n for CEC2017 seeds):

```python
# Toy benchmark: seed=42
bench = ToyBenchmark(seed=42)

# CEC2017: seeds 0-29 (with --n-seeds 30)
# Each algorithm run uses: random.seed(i), np.random.seed(i)
```

For truly reproducible results:
1. Use same seed values (default is fixed)
2. Use same Python version (3.13+)
3. Same environment (`uv sync` to install exact versions)

### Output Files

Results are saved as JSON with full metadata:

```json
{
  "metadata": {
    "n_dims": 10,
    "n_generations": 30,
    "seeds": 30,
    "timestamp": "2026-09-15T12:34:56Z"
  },
  "summary": {
    "QIEA-Enhanced": {
      "mean_error": 1.23e-4,
      "best_error": 5.67e-5
    }
  },
  "results": [
    {
      "function_id": 1,
      "function_name": "Sphere",
      "algorithm": "QIEA-Enhanced",
      "mean": 123.45,
      "std": 45.67,
      "best": 89.01
    }
  ]
}
```

## Algorithm Configuration

### Enhanced Quantum-Inspired (QIEA-Enhanced)

```bash
python -m malta.cli.main benchmark cec2017 \
  --n-functions 3 \
  --dimension 10 \
  --n-seeds 30
  # Defaults:
  # - n_compartments: 5
  # - bits_per_dim: 8
  # - generations: 1000
  # - use_progressive: True (encoding resolution increases over time)
```

### Simple Quantum-Inspired (QIEA)

```bash
# Also included by default in CEC2017 benchmarks
# Defaults:
# - n_compartments: 5
# - bits_per_dim: 1 (single-bit encoding)
# - generations: 1000
```

### Baselines (GA, PSO)

```bash
# Included with --include-baselines flag
# GA: pop_size=100, generations=1000
# PSO: pop_size=50, generations=1000
```

## Statistical Rigor

### Minimum Seeds Recommendation

- **Development/validation**: 10 seeds (quick feedback)
- **Publication-ready**: 30 seeds (Wilcoxon test requires ≥30)

```bash
# Development
python -m malta.cli.main benchmark cec2017 \
  --n-functions 3 --n-seeds 10

# Publication
python -m malta.cli.main benchmark cec2017 \
  --n-functions 10 --n-seeds 30 --include-baselines
```

### Analysis

Results include standard statistical metrics:
- Mean, median, std, min, max
- Error vs optimum (error_mean)
- Ready for Wilcoxon/Friedman tests (via `benchmarks.harness.wilcoxon_test`)

## Advanced Usage

### Direct Python API

```python
from benchmarks.harness import BenchmarkHarness
from benchmarks.baselines.quantum_inspired_enhanced import EnhancedQuantumInspiredBaseline
from benchmarks.suites.cec2017 import CEC2017Suite

harness = BenchmarkHarness(CEC2017Suite(), strict=False)
algo = EnhancedQuantumInspiredBaseline(
    n_compartments=5,
    bits_per_dim=8,
    use_progressive=True,
    generations=1000
)

problem = CEC2017Suite().get_function(1, 10)  # F1, 10D
stats = harness.run_algorithm_on_problem(algo, problem, n_seeds=30)

print(f"Mean: {stats['mean']:.2e}")
print(f"Best: {stats['best']:.2e}")
```

### Custom Output Processing

```python
import json
from pathlib import Path

# Load results
results_file = Path("results/cec2017_10d_30seeds.json")
data = json.loads(results_file.read_text())

# Filter by algorithm
enhanced_results = [
    r for r in data["results"]
    if r["algorithm"] == "QIEA-Enhanced"
]

# Compute custom metrics
for func_id in [1, 3, 4]:
    func_results = [r for r in enhanced_results if r["function_id"] == func_id]
    avg_best = sum(r["best"] for r in func_results) / len(func_results)
    print(f"F{func_id}: avg best = {avg_best:.2e}")
```

## Example Workflows

### Validate Algorithm Changes

```bash
# Before modification
python -m malta.cli.main benchmark toy \
  --n-dims 2 --n-generations 30 --output baseline.json

# Make changes to quantum_inspired_enhanced.py

# After modification
python -m malta.cli.main benchmark toy \
  --n-dims 2 --n-generations 30 --output modified.json

# Compare results
python -c "
import json
baseline = json.loads(open('baseline.json').read())
modified = json.loads(open('modified.json').read())
# Analyze differences
"
```

### Publication Benchmark

```bash
# Run full CEC2017 with all functions, multiple dimensions
for dim in 10 30; do
  python -m malta.cli.main benchmark cec2017 \
    --n-functions 10 \
    --dimension $dim \
    --n-seeds 30 \
    --include-baselines \
    --output-dir results/paper
done
```

### Sensitivity Analysis

```bash
# Test different encoding resolutions
for bits in 4 6 8 10; do
  # Use Python API for custom configurations
  python -c "
from benchmarks.harness import BenchmarkHarness
from benchmarks.baselines.quantum_inspired_enhanced import EnhancedQuantumInspiredBaseline
# ... configure with bits_per_dim=$bits
  "
done
```

## Troubleshooting

### Import Errors

```bash
# Reinstall package in development mode
uv sync
```

### Slow Benchmarks

```bash
# Use fewer seeds during development
python -m malta.cli.main benchmark cec2017 \
  --n-functions 3 --n-seeds 5  # Quick validation

# Reduce generations
# (Modify in Python API: generations=100 instead of 1000)
```

### Memory Issues with Large n_bits

```bash
# For very high-resolution encoding (16+ bits per dimension),
# the basis state space becomes huge (2^(16*10) for 10D).
# The algorithm samples instead of enumerating all states.
# Reduce bits_per_dim if memory is tight:
python -c "
from benchmarks.baselines.quantum_inspired_enhanced import EnhancedQuantumInspiredBaseline
algo = EnhancedQuantumInspiredBaseline(bits_per_dim=6)  # Reduced from 8
"
```

## See Also

- [Convergence Analysis](../malta/convergence.py) - Analyze fitness trajectories
- [Toy Benchmarks](../benchmarks/toy_benchmark.py) - Simple test functions
- [Harness Integration](../benchmarks/harness.py) - Core benchmarking infrastructure
