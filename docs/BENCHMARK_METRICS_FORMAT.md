# Benchmark Metrics Export Format

Standard JSON format for benchmark results to enable dashboard visualization and historical comparison.

## Overview

When you run `just bench-metrics` (after `just bench-full`), the system exports three JSON files to `benchmarks/metrics/`:

1. **Full metrics** — Complete convergence data per algorithm-function pair
2. **Algorithm comparison** — Side-by-side algorithm scores
3. **Convergence trends** — Per-algorithm convergence curves for plotting

## File Locations

```
benchmarks/metrics/
├── metrics_20260916-143022.json          # Full run data
├── comparison_10d.json                   # Algorithm comparison
├── trends_GA_10d.json                    # GA convergence trend
└── trends_PSO_10d.json                   # PSO convergence trend
```

## Schema: metrics_*.json (Full Run)

Complete benchmark run with all metrics.

```json
{
  "run_id": "20260916-143022",
  "dimension": 10,
  "n_seeds": 30,
  "timestamp": "2026-09-16T14:30:22.123456",
  "convergence_metrics": [
    {
      "algorithm": "GA",
      "function_id": 1,
      "function_name": "F1: Sphere",
      "dimension": 10,
      "n_seeds": 30,
      "mean_result": 100.2,
      "std_result": 0.5,
      "best_result": 99.5,
      "worst_result": 100.5,
      "median_result": 100.0,
      "optimum": 100.0,
      "error_mean": 0.2,
      "convergence_ratio": 0.002,
      "timestamp": "2026-09-16T14:00:00",
      "runtime_seconds": 1.23
    }
  ],
  "algorithm_profiles": [
    {
      "algorithm": "GA",
      "dimension": 10,
      "n_seeds": 30,
      "n_functions": 29,
      "mean_convergence_ratio": 0.45,
      "best_convergence_ratio": 0.001,
      "worst_convergence_ratio": 2.15,
      "functions_within_10x_optimum": 22,
      "success_rate": 0.76,
      "ranking": {"GA": 1, "PSO": 2},
      "timestamp": "2026-09-16T14:30:22"
    }
  ],
  "trends": {
    "ga_converging_well": true,
    "pso_converging_well": true
  }
}
```

## Schema: comparison_*.json (Algorithm Comparison)

Side-by-side algorithm performance for easy comparison.

```json
{
  "timestamp": "2026-09-16T14:30:22",
  "dimension": 10,
  "n_seeds": 30,
  "algorithm_profiles": [
    {
      "algorithm": "GA",
      "dimension": 10,
      "n_seeds": 30,
      "n_functions": 29,
      "mean_convergence_ratio": 0.45,
      "best_convergence_ratio": 0.001,
      "worst_convergence_ratio": 2.15,
      "functions_within_10x_optimum": 22,
      "success_rate": 0.76,
      "ranking": {"GA": 1, "PSO": 2},
      "timestamp": "2026-09-16T14:30:22"
    },
    {
      "algorithm": "PSO",
      "dimension": 10,
      "n_seeds": 30,
      "n_functions": 29,
      "mean_convergence_ratio": 0.38,
      "best_convergence_ratio": 0.0,
      "worst_convergence_ratio": 1.8,
      "functions_within_10x_optimum": 27,
      "success_rate": 0.93,
      "ranking": {"GA": 1, "PSO": 2},
      "timestamp": "2026-09-16T14:30:22"
    }
  ]
}
```

## Schema: trends_*.json (Convergence Trend)

Per-algorithm convergence data for plotting fitness curves.

```json
{
  "algorithm": "GA",
  "timestamp": "2026-09-16T14:30:22",
  "dimension": 10,
  "convergence_ratios": [
    {
      "function_id": 1,
      "function_name": "F1: Sphere",
      "convergence_ratio": 0.002,
      "error_mean": 0.2
    },
    {
      "function_id": 3,
      "function_name": "F3: Sum of Different Powers",
      "convergence_ratio": 0.15,
      "error_mean": 45.0
    }
  ],
  "stats": {
    "mean_convergence": 0.45,
    "best_convergence": 0.001,
    "worst_convergence": 2.15
  }
}
```

## Key Metrics Definitions

### Convergence Ratio

Normalized error: how far from optimum, as a fraction of optimum scale.

```
convergence_ratio = |mean_result - optimum| / optimum
```

**Interpretation:**
- `0.0` = Perfect convergence (mean result = optimum)
- `0.1` = 10% error (mean result = 1.1x optimum)
- `1.0` = 100% error (mean result = 2x optimum)
- `10.0` = 1000% error (mean result = 11x optimum)

**Dashboard Classification:**
- **Green (0.0-0.5):** Excellent convergence
- **Yellow (0.5-5.0):** Good convergence
- **Red (5.0+):** Poor convergence

### Success Rate

Fraction of functions where algorithm converged within 10x optimum.

```
success_rate = (# functions with convergence_ratio ≤ 10.0) / total_functions
```

**Dashboard Display:**
- PSO: `success_rate = 0.93` → "93% of functions solved well"
- GA: `success_rate = 0.76` → "76% of functions solved well"

### Function Classification

Based on difficulty (convergence_ratio):
- **Easy:** Convergence_ratio < 0.5 (most algorithms succeed)
- **Medium:** Convergence_ratio 0.5-5.0 (selective success)
- **Hard:** Convergence_ratio > 5.0 (most algorithms fail)

## CEC2017 Test Suite Reference

Functions tested: F1–F30 (29 total; F2 excluded)

Each function F_i has optimum = i * 100:
- F1: Sphere (optimum = 100)
- F3: Sum of Different Powers (optimum = 300)
- ...
- F30: Composition (optimum = 3000)

## Usage by Dashboard

### Algorithm Scorecard
Load `comparison_*.json` → Display AlgorithmProfile cards:
```
GA:
  Mean Convergence: 0.45
  Success Rate: 76%
  Best on: F1 (0.002), F4 (0.008), ...
```

### Function Heatmap
Load `trends_*.json` → 2D heatmap (functions × algorithms):
```
     GA    PSO   QuantumX
F1   ✅    ✅    ✅
F3   🟡    ✅    ✅
F10  🔴    🟡    ✅
```

### Convergence Curves
Load `trends_*.json` → Plot per algorithm:
```
Convergence (log scale)
│
10 ┤     ╱─╲
   │    ╱   ╲    PSO
 1 ┤   ╱     ╲╱──
   │  ╱   GA     ╲
0.1├ ╱           ╲
   └──────────────
     F1  F3  F10 F30
```

## Export Pipeline

```
just bench-full
  └─ benchmarks/run_example.py runs 30 seeds, 29 functions, 10D
       └─ BenchmarkHarness.export_csv() → benchmarks_example.csv

just bench-metrics
  └─ benchmarks/collect_results.py parses CSV
       └─ ConvergenceMetrics aggregation
            └─ export_benchmark_metrics() writes to benchmarks/metrics/
                 ├─ metrics_<run_id>.json (full)
                 ├─ comparison_10d.json (comparison)
                 └─ trends_<algo>_10d.json (per-algo)
```

## Historical Comparison

To track optimization progress over time:

1. Run `just bench-full-metrics` weekly
2. Rename output: `cp benchmarks/metrics/metrics_*.json results/benchmark_history/metrics_20260916.json`
3. Dashboard reads all `results/benchmark_history/*.json`
4. Plot trend: mean_convergence_ratio over time

Example multi-run trend:
```json
[
  {"date": "2026-09-09", "algorithm": "GA", "mean_convergence": 0.55},
  {"date": "2026-09-16", "algorithm": "GA", "mean_convergence": 0.45},
  {"date": "2026-09-23", "algorithm": "GA", "mean_convergence": 0.38}
]
```

Shows: "GA improving — convergence ratio dropping 17% over 2 weeks"

## Validation Checklist

Before dashboard ingestion:

- [ ] `run_id` is unique timestamp
- [ ] `n_seeds >= 30` (publication-ready)
- [ ] `convergence_ratio` in all metrics (no missing values)
- [ ] `success_rate` between 0.0 and 1.0
- [ ] Timestamp is ISO-8601 format
- [ ] All algorithm profiles present
- [ ] No NaN or infinity in numeric fields

## Phase 5 Dashboard Integration

Benchmark metrics feed into:
- **Optimization Trends Panel** — Mean convergence ratio trend lines
- **Algorithm Status Widget** — "GA 76% success | PSO 93% success"
- **Function Coverage Heatmap** — Which functions solved well
- **ROI Narrative** — "Optimization improving: convergence up 20% in 30 days"

See `dashboards/METRICS_SCHEMA.md` for full dashboard spec.
