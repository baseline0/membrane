---
title: Membrane Quantum Computing — Benchmarking Strategy
date: 2025-09-15
tags: [benchmarking, methodology, experimental-design, research-strategy]
type: research_methodology
status: living_document
---

# Benchmarking Strategy for Membrane Quantum Computing

This document outlines the structured approach to benchmarking Malta (our Quantum P-System implementation) against state-of-the-art algorithms, generating publication-quality results, and building an iterative research pipeline.

---

## Overview

We use a **three-phase approach**:

1. **Phase 1: Classical Benchmarks** (Months 1–6)
   - Malta (P-system) vs. GA, PSO, XGBoost on standard optimization benchmarks
   - Goal: Establish baseline competitiveness; publish first paper

2. **Phase 2: Quantum-Inspired Hybrid** (Months 6–12)
   - Add quantum superposition to Malta; test on NP-hard problems (SAT, TSP)
   - Compare against quantum-inspired classical algorithms
   - Goal: Show quantum inspiration provides speedup

3. **Phase 3: Theoretical Quantum P-Systems** (Months 12–24)
   - Implement quantum circuit simulators using P-system rules
   - Test on QASM Bench; characterize complexity
   - Goal: Publish theoretical contributions + open problems

---

## Benchmark Suites & Datasets

### Suite 1: Continuous Optimization (CEC2017)

**Purpose:** Compare Malta on 30 bounded continuous functions.

**Problem Instances:**
- Dimensions: 10, 30, 50, 100
- Dimensions: 10 (beginner), 30 (intermediate), 50 (challenging), 100 (hard)
- 30 test functions with varying properties (unimodal, multimodal, shifted, rotated)

**How to Obtain:**
```bash
# CEC2017 official functions
git clone https://github.com/P-N-Suganthan/CEC2017.git
cd CEC2017 && python3 setup_cec2017.py

# Alternative: scipy.optimize has similar test functions
```

**Metrics:**
- **Solution Quality:** Final fitness value achieved (lower is better)
- **Convergence Rate:** Fitness vs. function evaluations
- **Robustness:** std deviation across 30 independent runs
- **Efficiency:** Time per function evaluation (FLOPs)

**Baselines:**
- Genetic Algorithm (DEAP)
- Particle Swarm Optimization (pyswarms)
- Differential Evolution (scipy)
- XGBoost (if applicable as a black-box optimizer)

---

### Suite 2: Traveling Salesperson Problem (TSPLIB)

**Purpose:** NP-hard combinatorial optimization; benchmark memory + parallelism.

**Problem Instances:**
- **Easy:** a280 (280 cities), ch150 (150 cities)
- **Medium:** pr1002 (1002 cities), d1291 (1291 cities)
- **Hard:** nrw1379 (1379 cities), pla7397 (7397 cities)

**How to Obtain:**
```bash
# TSPLIB instances
wget http://elib.zib.de/WebData/tsplib/tsplib.tar.gz
tar xzf tsplib.tar.gz
```

**Metrics:**
- **Tour Length:** Final solution quality (lower is better)
- **Optimality Gap:** (Found - Optimal) / Optimal × 100%
- **Runtime:** Wall-clock time to convergence
- **Scalability:** How quality degrades as problem size increases

**Baselines:**
- Lin-Kernighan heuristic
- Genetic Algorithm for TSP
- Ant Colony Optimization
- Simulated Annealing

---

### Suite 3: Boolean Satisfiability (DIMACS SAT)

**Purpose:** NP-complete decision problem; tests exponential state space.

**Problem Instances:**
- **3-SAT:** Small (20 vars), Medium (50 vars), Large (100 vars)
- **Industrial:** Real SAT competition instances

**How to Obtain:**
```bash
# SAT competition benchmarks
wget http://www.satcompetition.org/2020/downloads.html
# Or specific instance libraries
wget http://www.cs.ubc.ca/~hoos/SATLIB/benchmarks.html
```

**Metrics:**
- **Satisfiability:** Did the algorithm find a solution? (Yes/No)
- **Time to Satisfaction:** How long to find a solution?
- **Clauses Satisfied:** If unsatisfiable, how many clauses can be satisfied? (MaxSAT variant)

**Baselines:**
- DPLL solver (exact)
- CDCL solver (industrial-strength, e.g., CaDiCaL)
- Quantum-Inspired Genetic Algorithms
- Simulated Annealing

---

### Suite 4: UCI Machine Learning (Classification)

**Purpose:** Real-world problems; tests rule-based system learning.

**Problem Instances:**
- **Iris:** 150 samples, 4 features (toy)
- **Wine:** 178 samples, 13 features (benchmark)
- **Breast Cancer:** 569 samples, 30 features (real-world)
- **Cardiotocography:** 2126 samples, 22 features (medical)

**How to Obtain:**
```python
from sklearn.datasets import load_iris, load_wine
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
```

**Metrics:**
- **Accuracy:** Percentage of correct classifications
- **F1 Score:** Harmonic mean of precision & recall
- **ROC AUC:** Area under receiver operating characteristic curve
- **Training Time:** How long to learn rules

**Baselines:**
- Logistic Regression
- Random Forest
- XGBoost
- SVM
- Neural Networks

---

### Suite 5: Quantum Circuit Synthesis (QASM Bench)

**Purpose:** Test quantum circuit simulation using P-system rules.

**Problem Instances:**
- **Small:** 5-qubit circuits (Deutsch-Jozsa, Grover)
- **Medium:** 10-qubit circuits (VQE, QFT)
- **Large:** 20+ qubit circuits (Shor, QAOA)

**How to Obtain:**
```bash
git clone https://github.com/pqueteg/QASMBench.git
cd QASMBench
# Circuits in OpenQASM format (.qasm files)
```

**Metrics:**
- **Gate Reduction:** Minimize number of gates after compilation
- **Depth Reduction:** Minimize circuit depth (for parallelism)
- **Fidelity:** Accuracy of P-system simulation vs. reference
- **Compilation Time:** How long to optimize circuit

**Baselines:**
- Qiskit compiler
- PyQuil compiler
- Cirq compiler

---

## Experimental Protocol

### 1. Parametrization

For each algorithm and benchmark suite, define:

```python
algorithm_config = {
    "name": "Malta (FRPS)",
    "population_size": 30,
    "generations": 100,
    "mutation_rate": 0.1,
    "crossover_rate": 0.7,
    "timeout": 3600,  # 1 hour
}
```

**Parameter Selection:**
- Use literature defaults for baselines (GA, PSO)
- Tune Malta parameters via small grid search on representative problems
- Fix parameters across all runs (no per-problem tuning)

### 2. Execution Protocol

For **each** (algorithm, problem, seed) triplet:

```python
results = []
for seed in range(30):  # 30 independent runs
    random.seed(seed)
    np.random.seed(seed)
    
    start_time = time.time()
    solution, fitness_history = algorithm.solve(problem, timeout=3600)
    elapsed = time.time() - start_time
    
    results.append({
        "algorithm": algorithm_config["name"],
        "problem": problem.name,
        "seed": seed,
        "final_fitness": fitness_history[-1],
        "best_fitness": min(fitness_history),
        "elapsed_time": elapsed,
        "fitness_history": fitness_history,  # For convergence plots
    })
```

**Why 30 runs?**
- Allows Wilcoxon signed-rank test (nonparametric, accounts for non-normal distributions)
- Sufficient for statistical significance with small effect sizes
- Standard in evolutionary algorithm literature (CEC2017 norm)

### 3. Data Collection

Save results as CSV for each benchmark suite:

```
algorithm,problem,seed,final_fitness,best_fitness,elapsed_time
Malta (FRPS),f1_10d,0,123.45,100.23,45.67
Malta (FRPS),f1_10d,1,125.12,99.87,46.23
XGBoost,f1_10d,0,200.00,150.00,20.00
...
```

### 4. Statistical Analysis

#### A. Pairwise Comparison (Wilcoxon Test)
For each pair of algorithms {A, B} on each problem:

$$H_0: \text{A and B are equally good}$$
$$p\text{-value} = \Pr(|\text{Test Statistic}| \geq |W|)$$

Reject $H_0$ if $p < 0.05$ (5% significance level).

#### B. Ranking (Friedman Test)
Rank algorithms across all problems:

$$H_0: \text{All algorithms have equal average rank}$$
$$\chi^2 = \frac{12 N}{k(k+1)} \sum_j R_j^2 - 3N(k+1)$$

where $N$ = number of problems, $k$ = number of algorithms, $R_j$ = average rank of algorithm $j$.

#### C. Effect Size (Cohen's d)
Quantify practical significance:

$$d = \frac{\bar{x}_A - \bar{x}_B}{\sigma_{\text{pooled}}}$$

- $|d| < 0.2$: negligible effect
- $0.2 \leq |d| < 0.5$: small effect
- $0.5 \leq |d| < 0.8$: medium effect
- $|d| \geq 0.8$: large effect

#### D. Pareto Frontier
Plot solutions in (Quality, Runtime) space; identify non-dominated algorithms.

---

## Reporting Pipeline

### 1. Raw Results
File: `reports/[suite_name]_[date]/results.csv`

```
algorithm,problem,seed,final_fitness,best_fitness,elapsed_time,fitness_history
```

### 2. Aggregate Statistics
File: `reports/[suite_name]_[date]/summary.json`

```json
{
  "algorithms": {
    "Malta (FRPS)": {
      "mean_fitness": 150.23,
      "std_fitness": 12.45,
      "min_fitness": 125.00,
      "max_fitness": 175.00,
      "mean_runtime": 45.67,
      "std_runtime": 2.34
    },
    ...
  },
  "pairwise_tests": {
    "Malta vs XGBoost": {
      "wilcoxon_p_value": 0.0234,
      "cohens_d": 0.45,
      "winner": "Malta"
    }
  }
}
```

### 3. Visualizations

#### Figure 1: Convergence Curves
X-axis: Function evaluations  
Y-axis: Best fitness found so far  
Separate subplots for each problem.

#### Figure 2: Box Plots
Compare solution quality distributions across algorithms.

#### Figure 3: Runtime vs Quality (Pareto)
Scatter: each point = algorithm/problem pair  
Highlight non-dominated solutions.

#### Figure 4: Statistical Significance Heatmap
Rows/Cols = algorithms  
Color = p-value from pairwise Wilcoxon test  
Red = statistically significant difference

### 4. Publication-Quality Report
File: `reports/[suite_name]_[date]/publication.pdf` (auto-generated from LaTeX template)

**Sections:**
- Abstract: 200 words
- Introduction: Problem motivation + prior work
- Methods: Algorithms + benchmark selection
- Results: Figures + tables + statistical tests
- Discussion: Implications + limitations
- Conclusion + future work

---

## Implementation Checklist

### Infrastructure Setup
- [ ] Create `benchmarks/suites/` with loaders for each suite (CEC2017, TSPLIB, etc.)
- [ ] Create `benchmarks/baselines/` with implementations of GA, PSO, XGBoost, etc.
- [ ] Implement `benchmarks/harness.py` with parallel execution + timeout handling
- [ ] Create `reports/templates/comparison.tex` for LaTeX auto-generation

### Phase 1: Classical Benchmarks
- [ ] Run Malta vs GA/PSO on CEC2017 (10D, 30D)
- [ ] Collect 30 × 2 dimensions × 3 algorithms = 180 runs
- [ ] Perform statistical analysis (Wilcoxon, Friedman)
- [ ] Generate publication report
- [ ] Submit to conference (e.g., GECCO, CEC)

### Phase 2: Quantum-Inspired + NP-Hard
- [ ] Integrate superposition into Malta
- [ ] Test on TSPLIB (10 instances × 3 algorithms × 30 runs = 900 runs)
- [ ] Test on DIMACS SAT (small instances)
- [ ] Compare against QMEA baselines
- [ ] Publish: "Quantum-Inspired Membrane Algorithms for Combinatorial Optimization"

### Phase 3: Theoretical Quantum P-Systems
- [ ] Implement quantum circuit simulator (P-system rules → QASM)
- [ ] Test on QASM Bench
- [ ] Characterize complexity (BQP bounds, etc.)
- [ ] Publish: "Distributed Quantum Computing via Membrane Compartmentalization"

---

## Success Metrics

| Milestone | Target | Timeline |
|-----------|--------|----------|
| Phase 1 complete (classical benchmarks) | Malta competitive with GA/PSO | Month 6 |
| First publication submitted | CEC/GECCO conference paper | Month 9 |
| Phase 2 complete (QMEA) | Quantum inspiration shows 2–3× speedup on SAT | Month 12 |
| Second publication (QMEA) | Natural Computing or specialty journal | Month 15 |
| Phase 3 complete (theory) | Complexity bounds published | Month 24 |

---

## Related Documents

- `literatura_database.md` — Citation database for all benchmarks + papers
- `open_problems.md` — Theoretical challenges + research directions
- `../notes/TEMPLATE_paper_notes.md` — Template for capturing research findings
- `../../planning/research_strategy.md` — Long-term 5-year plan

---

**Last Updated:** 2025-09-15  
**Maintained By:** Mark Alexiuk  
**Project:** Malta (Membrane Computing Research Framework)
