# Benchmark Metrics for Fleet Dashboard

This document describes the metrics that benchmark results feed into the fleet health dashboard.

## Overview

The benchmark system produces convergence data for optimization algorithms (GA, PSO) across the CEC2017 test suite. These metrics are collected and exported for dashboard visualization.

## Metrics Schema

### ConvergenceMetrics (Per Algorithm, Per Function)

**What:** Performance of a single algorithm on a single test function.

**Fields:**
- `algorithm` — "GA" or "PSO"
- `function_id` — CEC2017 function ID (1-30, excluding 2)
- `function_name` — "F1: Sphere", "F3: Sum of Different Powers", etc.
- `dimension` — Problem dimensionality (10D)
- `n_seeds` — Number of independent runs (30)
- `mean_result` — Mean best result across all seeds
- `std_result` — Standard deviation of results
- `best_result` — Best result achieved
- `worst_result` — Worst result achieved
- `optimum` — Known global optimum (func_id * 100)
- `error_mean` — How far mean result is from optimum
- `convergence_ratio` — Normalized error (error / optimum). **0.0 = perfect**, **1.0 = 1x error**, etc.
- `timestamp` — When metric was recorded

**Dashboard Use:** Plot convergence_ratio per function, sorted by difficulty.

### AlgorithmProfile (Per Algorithm, Aggregated)

**What:** Overall performance of an algorithm across all test functions.

**Fields:**
- `algorithm` — "GA" or "PSO"
- `dimension` — Problem dimensionality
- `n_seeds` — Number of runs per function
- `n_functions` — Total functions tested (29 for CEC2017)
- `mean_convergence_ratio` — Average convergence ratio across all functions
- `best_convergence_ratio` — Best convergence on any function
- `worst_convergence_ratio` — Worst convergence on any function
- `functions_within_10x_optimum` — Count of functions where convergence_ratio ≤ 10.0
- `success_rate` — Percentage of functions converged well (≤10x optimum)
- `ranking` — Ranking vs other algorithms

**Dashboard Use:** Algorithm scorecard, comparison leaderboard, success metrics.

### BenchmarkRun (Complete Run)

**What:** Entire benchmark execution (all algorithms, all functions, one dimension).

**Fields:**
- `run_id` — Unique run identifier (timestamp)
- `dimension` — Problem dimensionality (10D)
- `n_seeds` — Seeds per problem
- `timestamp` — When run completed
- `convergence_metrics` — List of ConvergenceMetrics (one per algo-function pair)
- `algorithm_profiles` — Aggregated profiles per algorithm
- `trends` — High-level trend indicators (GA improving, PSO stable, etc.)

**Dashboard Use:** Historical runs, trend tracking, version comparison.

## Export Formats

### metrics_{run_id}.json

Full benchmark run with all convergence metrics. Used for detailed analysis.

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
      "convergence_ratio": 0.002,
      "mean_result": 100.2,
      "optimum": 100.0,
      ...
    }
  ],
  "algorithm_profiles": [...],
  "trends": {...}
}
```

### comparison_{dimension}d.json

Side-by-side algorithm comparison. Used for dashboard "Algorithm Showdown" widget.

```json
{
  "timestamp": "2026-09-16T14:30:22",
  "dimension": 10,
  "n_seeds": 30,
  "algorithm_profiles": [
    {
      "algorithm": "GA",
      "mean_convergence_ratio": 0.45,
      "success_rate": 0.76,
      "ranking": {"GA": 1, "PSO": 2}
    },
    {
      "algorithm": "PSO",
      "mean_convergence_ratio": 0.38,
      "success_rate": 0.83,
      "ranking": {"GA": 1, "PSO": 2}
    }
  ]
}
```

### trends_{algorithm}_{dimension}d.json

Convergence trend per algorithm. Used for heatmaps and per-function analysis.

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
    ...
  ],
  "stats": {
    "mean_convergence": 0.45,
    "best_convergence": 0.001,
    "worst_convergence": 2.15
  }
}
```

## Dashboard Widgets (Proposed)

### 1. Algorithm Scorecard
- **Source:** `comparison_*.json` → AlgorithmProfile
- **Display:** Cards per algorithm
  - Mean convergence ratio (primary metric)
  - Success rate % (functions ≤10x optimum)
  - Ranking vs other algorithms
  - Trend indicator (↑ improving, ↓ regressing)

### 2. Function Heatmap
- **Source:** `trends_*.json` → convergence_ratios
- **Display:** 2D heatmap (functions × algorithms)
  - Cells colored by convergence ratio
  - Green (0.0-0.5): excellent convergence
  - Yellow (0.5-5.0): good convergence
  - Red (5.0+): poor convergence
  - Gray (N/A): function not tested

### 3. Convergence Curves
- **Source:** `trends_*.json` + historical runs
- **Display:** Line chart per algorithm
  - X-axis: Functions sorted by difficulty
  - Y-axis: Convergence ratio (log scale)
  - Multi-run overlay to show improvement over time

### 4. Historical Trends
- **Source:** Multiple BenchmarkRun exports
- **Display:** Time-series dashboard
  - Mean convergence ratio trend per algorithm
  - Success rate trend
  - Population/generation tuning effects

## Collection Pipeline

1. **Run Benchmark:** `just bench-full` (30 seeds, 29 functions, 10D, ~1-2h)
2. **Generate CSV:** BenchmarkHarness.export_csv() → benchmarks_example.csv
3. **Collect Metrics:** `just bench-metrics` → Parse CSV, generate JSON exports
4. **Export Location:** benchmarks/metrics/ (git-ignored, not committed)
5. **Dashboard Ingestion:** Pull latest metrics/*.json files into dashboard backend

## Metrics vs Code Tradeoff

- **Why JSON exports:** Dashboard needs pre-computed aggregates (algorithm profiles, rankings, convergence ratios)
- **Why not store in code:** Metrics change frequently (every benchmark run), JSON is lightweight, CSVs are sufficient for recomputation
- **Recomputation:** `just bench-metrics` can reparse benchmarks_example.csv anytime; exports are ephemeral

## Integration with Phase 5 Dashboard

The benchmark metrics feed into the fleet health dashboard as:
- **Optimization Trends:** Mean convergence ratio trend lines
- **Algorithm Status:** "GA 76% success | PSO 83% success"
- **Function Coverage:** Which functions converging well, which struggling
- **Compliance:** Benchmark validation passes (30 seeds, Wilcoxon-ready)
- **Historical Context:** Side-by-side run comparisons

See `dashboard/METRICS_SCHEMA.md` for full fleet dashboard spec.
