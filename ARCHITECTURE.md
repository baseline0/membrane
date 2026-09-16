# Malta Architecture: Research Framework for Membrane Computing

## Overview

Malta is being evolved into a **publication-quality research framework** for comparing Membrane Systems (P-Systems) against conventional approaches. It supports two parallel tracks:

1. **Short-term (1–2 years):** Insurance regulatory compliance consulting (funds the research)
2. **Long-term (2–5+ years):** Quantum Membrane Computing as a niche research area

## Repository Structure

```
.
├── malta/                      # Core P-System simulator (pure library)
│   ├── cli/                    # Typer CLI for standalone execution
│   ├── config/                 # Example simulation configs
│   ├── fuzzy.py                # Fuzzy membership functions (FRPS support)
│   ├── simulation.py           # Main simulation loop
│   ├── environment.py          # Membrane hierarchy + rule application
│   └── ...                     # Other core modules
│
├── benchmarks/                 # Research benchmarking framework
│   ├── suites/                 # Problem suites (CEC, TSPLIB, UCI, etc.)
│   │   ├── cec2017.py         # Continuous optimization (CEC2017)
│   │   ├── tsplib.py          # Traveling Salesperson Problem
│   │   ├── uci.py             # Classification tasks (UCI ML)
│   │   └── sat.py             # Boolean satisfiability (SAT)
│   │
│   ├── baselines/              # Conventional algorithms
│   │   ├── xgboost.py         # Gradient boosting
│   │   ├── ga.py              # Genetic Algorithm (DEAP)
│   │   ├── pso.py             # Particle Swarm Optimization
│   │   ├── fuzzy.py           # Mamdani/Sugeno fuzzy inference
│   │   └── solver.py          # Exact solvers (Gurobi/CPLEX wrappers)
│   │
│   ├── datasets/               # Benchmark datasets (symlinked or fetched)
│   │   ├── cec2017/
│   │   ├── tsplib/
│   │   └── uci/
│   │
│   └── harness.py             # Unified benchmark runner (30+ runs, stats)
│
├── reports/                    # Generated comparison reports
│   ├── templates/              # LaTeX/Markdown templates for publications
│   │   ├── comparison.tex     # Algorithm comparison tables/figures
│   │   └── pareto_frontier.tex # Pareto analysis template
│   │
│   └── [generated]/            # Output: cec2017_comparison/, etc.
│       ├── results.csv        # Raw results (all runs)
│       ├── summary.json       # Aggregated stats (mean, std, sig tests)
│       ├── pareto_frontier.png # Pareto plot
│       └── publication.pdf    # Ready-to-submit comparison report
│
├── docs/
│   ├── planning/
│   │   ├── rollout.md         # Market + consulting roadmap (insurance)
│   │   └── research_strategy.md # Long-term quantum research plan
│   │
│   ├── quantum/                # Knowledge base on Quantum Membrane Computing
│   │   ├── research/           # Literature reviews + papers
│   │   │   ├── sota.md        # State-of-the-art survey
│   │   │   ├── qmea.md        # Quantum-inspired membrane algorithms
│   │   │   └── distributed_quantum.md # Modular quantum architecture
│   │   │
│   │   └── notes/              # Obsidian/local research notes
│   │       ├── 2025-09-14_quantum_niche.md
│   │       ├── 2025-09-14_frps_insurance.md
│   │       └── ideas/          # Brainstorms, hypotheses, todo items
│   │
│   └── ...
│
└── tests/                      # Unit + integration tests
    ├── unit/
    │   ├── test_malta_core.py
    │   └── test_benchmarks.py
    │
    └── integration/
        └── test_comparison_pipeline.py
```

---

## Execution Workflow (Benchmarking)

### Phase 1: Problem Selection
User selects a benchmark suite (CEC2017, TSPLIB, UCI dataset, SAT problem):

```python
from benchmarks import BenchmarkSuite

suite = BenchmarkSuite.load("cec2017", dimensions=[10, 30, 50])
```

### Phase 2: Algorithm Setup
Define Malta (P-System) and conventional baselines:

```python
from malta.cli import run as run_malta
from benchmarks.baselines import XGBoost, PSO, GeneticAlgorithm

algorithms = {
    "Malta (FRPS)": lambda problem: run_malta(problem),
    "XGBoost": XGBoost(max_depth=6),
    "PSO": PSO(n_particles=30),
    "GA": GeneticAlgorithm(pop_size=30),
}
```

### Phase 3: Execution
Run all algorithms across all problems, ≥30 independent seeds, dual-track metrics:

```python
results = suite.run(
    algorithms=algorithms,
    seeds=range(30),
    timeout=3600,  # 1 hour per algorithm/problem/seed
    track_flops=True,  # Hardware normalization (FLOPs)
    track_steps=True,  # Theoretical complexity (abstract steps)
)
```

### Phase 4: Analysis
Compute statistical significance and Pareto frontiers:

```python
from benchmarks.harness import ComparisonAnalysis

analysis = ComparisonAnalysis(results)
print(analysis.wilcoxon_summary())  # Pairwise significance tests
print(analysis.friedman_summary())  # Multi-algorithm ranking
analysis.plot_pareto_frontier().savefig("pareto.png")
```

### Phase 5: Publishing
Generate publication-quality report:

```python
from reports import PublicationReport

report = PublicationReport(analysis)
report.generate("reports/cec2017_comparison/")
# Output: results.csv, summary.json, pareto.png, publication.pdf
```

---

## Knowledge Base: Quantum Membrane Computing

All research findings are accumulated in `docs/quantum/`:

### Structure
```
docs/quantum/
├── research/
│   ├── sota.md                 # Literature survey (20+ papers)
│   ├── qmea.md                 # Quantum-inspired evolutionary algorithms
│   ├── distributed_quantum.md  # Modular quantum networks
│   └── niches.md               # Where do we fit? (publication strategy)
│
└── notes/                       # Obsidian notes (private, growing)
    ├── 2025-09-14_quantum_niche.md
    ├── ideas/
    │   ├── quantum_fuzzy_hybrid.md
    │   ├── distributed_qpe.md
    │   └── publication_roadmap.md
    └── [dated entries as research progresses]
```

### Why Obsidian Locally?

- **Private exploration:** Brainstorms, half-baked ideas, literature notes
- **Knowledge accumulation:** Dates, citations, hypotheses build over time
- **Mining for papers:** When ready to publish, selective findings → polished markdown → publication-quality docs/quantum/research/
- **Team-friendly:** Obsidian vaults can be synced (git) if collaborators join

---

## Two-Track Execution (Consulting + Research)

### Track A: Insurance Consulting (Short-term Revenue)

**Goal:** Build POC, get regulatory approval, generate case study.

1. **Problem:** Insurer's premium rating (10–50 features, 10k–1M historical policies)
2. **Solution:** FRPS rules + Malta simulator
3. **Benchmark:** Compare Malta vs XGBoost on same dataset
   - File results in `reports/[client_name]/`
   - Publish case study (anonymized) in `docs/planning/case_studies/`
4. **Outcome:** $250k–$500k engagement; funding for quantum research

### Track B: Quantum Membrane Research (Long-term Publications)

**Goal:** Publish 2–3 papers in natural computing / theoretical CS venues.

1. **Year 1–2:** Benchmark Malta against SOTA on CEC/TSPLIB (no quantum yet)
   - Publication: "Membrane Evolutionary Algorithms: Empirical Analysis vs GA/PSO"

2. **Year 2–3:** Implement Quantum-Inspired Membrane Algorithms (QMEAs)
   - Publication: "Quantum-Inspired Fuzzy Reasoning P-Systems for Combinatorial Optimization"

3. **Year 3+:** Theoretical Quantum P-Systems (distributed quantum architecture model)
   - Publication: "Membrane Compartmentalization as a Model for Distributed Quantum Computing"

---

## Immediate Priorities (Next 4 Weeks)

- [ ] Implement `benchmarks/suites/cec2017.py` (CEC2017 continuous optimization)
- [ ] Implement `benchmarks/baselines/ga.py` (baseline genetic algorithm)
- [ ] Implement `benchmarks/harness.py` (unified benchmark runner)
- [ ] Add `malta/fuzzy.py` (fuzzy membership functions for FRPS)
- [ ] Create initial report template (`reports/templates/comparison.tex`)
- [ ] Seed `docs/quantum/research/sota.md` with literature review

---

## Success Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| **Insurance consulting engagement** | 1 signed client | 6 months |
| **First publication (Malta benchmarks)** | 1 conference paper | 12 months |
| **Quantum QMEA implementation** | Working code + paper | 18 months |
| **Knowledge base size** | 50+ notes + 30+ papers cited | Ongoing |

---

## Why This Architecture?

1. **Separation of concerns:** Core malta/ is a library; benchmarks/ is the framework
2. **Publication-ready:** Reports auto-generate with statistical rigor (no manual tables)
3. **Modular baselines:** Easy to add new algorithms (add `benchmarks/baselines/new_algo.py`)
4. **Knowledge continuity:** Obsidian notes let you think out loud; published docs are polished
5. **Dual funding:** Insurance consulting funds quantum research without overselling P-Systems

---

## Next Document to Write

- `docs/planning/research_strategy.md` — 5-year plan for quantum membrane computing publications + partnerships
