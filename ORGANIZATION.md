# Membrane Repository Organization

## Goal
Clearly distinguish between third-party code, novel algorithms, and research outputs. Prepare for arXiv paper using math-trace.

---

## Directory Structure (Proposed)

```
membrane/
├── third-party/                    # Third-party, unmodified code
│   ├── malta/                      # Malta benchmarking framework (forked)
│   ├── cyprus/                     # P-system language (minor modifications)
│   └── cec2017/                    # CEC2017 benchmark suite (C source)
│
├── algorithms/                     # Novel algorithmic contributions
│   ├── quantum_inspired.py         # Quantum-inspired P-system algorithm (NOVEL)
│   ├── adaptive_evolution.py       # Adaptive evolution (NOVEL)
│   ├── convergence.py              # Convergence analysis (NOVEL)
│   └── __init__.py
│
├── benchmarks/                     # Benchmark infrastructure
│   ├── harness.py                  # Benchmark harness (from Malta)
│   ├── runners/                    # Run configurations for this paper
│   │   ├── cec2017_subset.py       # Run quantum-inspired on CEC2017 subset
│   │   ├── comparison.py           # Compare vs. classical algorithms
│   │   └── __init__.py
│   └── results/                    # Benchmark outputs (generated)
│
├── paper/                          # Research paper using math-trace
│   ├── model.py                    # Quantum-inspired algorithm (SymPy, SOURCE OF TRUTH)
│   ├── build_paper.py              # Build pipeline (formulas → Typst)
│   ├── main.typ                    # Typst paper
│   ├── generated/                  # Auto-generated (formulas, figures)
│   └── lean/                       # (Optional) Formal proofs
│
├── docs/
│   ├── QUANTUM.md                  # Quantum computing background
│   ├── NOVELTY.md                  # What's novel in this work
│   ├── CEC2017_SELECTION.md        # Which functions, why
│   └── ALGORITHMS.md               # Algorithm descriptions
│
├── tests/                          # Unit tests
│   ├── test_quantum_inspired.py
│   ├── test_algorithms.py
│   └── test_benchmarks.py
│
└── README.md                       # Updated: clarify roles of each part
```

---

## What's Third-Party vs. Novel

### Third-Party (Credit, but not our contribution)
- **Malta** — Benchmarking framework (forked, minor mods)
- **Cyprus** — P-system language (forked, minor mods)
- **CEC2017** — Benchmark functions (C source)

### Novel (Our contribution)
- **Quantum-inspired algorithm** — Application of quantum-inspired computing to P-systems
- **Adaptive evolution** — Novel adaptation mechanism
- **Convergence analysis** — Mathematical properties of our algorithms
- **Benchmark results** — Empirical validation on CEC2017 subset

### Infrastructure (Supporting, not core contribution)
- Benchmark harness (from Malta)
- Python bindings to CEC2017
- Test suite

---

## CEC2017 Function Selection (29 functions available)

### Categories

**Basic Unimodal (3 functions)**
- F1: Shifted and Rotated Bent Cigar
- F3: Shifted and Rotated Rosenbrock's
- F4: Shifted and Rotated Rastrigin's

**Multimodal (7 functions)**
- F5: Shifted and Rotated Expanded Scaffer's F6
- F6: Shifted and Rotated Lunacek Bi-Rastrigin
- F7: Shifted and Rotated Non-Continuous Rastrigin's
- F8: Shifted and Rotated Levy
- F9: Shifted and Rotated Schwefel's
- F10: Shifted and Rotated High Conditioned Elliptic
- [5 more optional]

**Hybrid (10 functions)**
- F11–F20: Various hybrid compositions

**Composition (10 functions)**
- F21–F30: Various compositions

### Proposed Subset for Paper (10-12 functions)

**Why subset?**
- Reduce computation time (10-12 functions vs. 29)
- Show diversity of problem types
- Make paper tractable (3 months timeline)

**Recommended:**

| Category | Functions | Reason |
|----------|-----------|--------|
| **Unimodal** | F1, F3, F4 | Baseline difficulty |
| **Multimodal** | F5, F6, F8 | Diverse landscapes |
| **Hybrid** | F11, F14, F17 | Mix composition levels |
| **Composition** | F21, F26 | Hardest cases |

**Total: 11 functions** (good balance of effort vs. diversity)

---

## Novel Algorithm: Quantum-Inspired P-System

### Current Understanding
The algorithm applies quantum-inspired computing concepts to P-systems for optimization:
- **Quantum superposition** → Parallel particle exploration
- **Quantum interference** → P-system rule interactions
- **Measurement** → Particle dissolution/consolidation

### What We Need to Document

1. **Mathematical formulation** (will go in model.py as SymPy)
   - Define quantum state encoding in P-systems
   - Define measurement/collapse in particle reactions
   - Convergence properties

2. **Algorithm pseudocode**
   - Initialization
   - Quantum update rules
   - Termination criteria

3. **Empirical validation**
   - Convergence speed vs. classical algorithms
   - Solution quality on CEC2017 subset
   - Scalability (dimension: 10D, 30D, 50D)

---

## Paper Structure (using math-trace)

### Sections

**1. Introduction**
- P-systems for optimization
- Quantum computing motivation
- Gap: no quantum-inspired P-systems yet
- Our contribution

**2. Background**
- P-systems basics (cite Cyprus language)
- Quantum-inspired computing overview
- CEC2017 benchmarks

**3. Method: Quantum-Inspired P-Systems** ← **Uses math-trace**
- Algorithm formulation (from model.py → auto-exported SymPy formulas)
- P-system encoding (particles, rules, reactions)
- Quantum operations (superposition, interference, measurement)

**4. Benchmarking Protocol**
- CEC2017 subset selection (table of 11 functions)
- Comparison algorithms (GA, PSO, baseline)
- Metrics (mean, std, convergence rate, statistical significance)
- Reproducibility (GitHub link, Docker isolation)

**5. Results**
- Performance tables (quantum-inspired vs. baselines)
- Convergence plots (generated by simulate.py)
- Statistical analysis (mean ± std, p-values)

**6. Discussion**
- Quantum-inspired P-systems advantages
- When to use (landscape characteristics)
- Limitations and future work

**7. Reproducibility**
- GitHub link to repo
- Instructions to rebuild paper from scratch
- Version control traceability (math-trace)

---

## Timeline (3 months)

| Phase | Timeline | Tasks |
|-------|----------|-------|
| **Organization** | Week 1 | Clean up repo structure, document novelty, select CEC2017 subset |
| **Formalization** | Week 2-3 | Write quantum-inspired algorithm in SymPy (model.py), Lean proofs (optional) |
| **Benchmarking** | Week 4-6 | Run experiments on CEC2017 subset, collect statistics |
| **Paper writing** | Week 7-8 | Draft full paper using math-trace |
| **Revision** | Week 9-10 | Peer review (internal), revise, finalize |
| **Submission** | Week 10-11 | Submit to arXiv |
| **Buffer** | Week 12 | Contingency |

---

## Key Files to Create/Modify

### Immediate (Week 1)
- [ ] Move code to third-party/ (Malta, Cyprus, CEC2017)
- [ ] Create algorithms/ directory structure
- [ ] Create paper/ directory (SymPy model + Typst template)
- [ ] Update README.md with organization

### Model (Week 2)
- [ ] `paper/model.py` — SymPy formulation of quantum-inspired algorithm
  - Define quantum superposition encoding
  - Define measurement/collapse rules
  - Export formulas for paper
- [ ] `algorithms/quantum_inspired.py` — Runnable implementation
  - Uses formulas from model.py
  - Validates they match

### Benchmarks (Week 4)
- [ ] `benchmarks/runners/cec2017_subset.py` — Run on selected functions
- [ ] `benchmarks/results/` — Store outputs (CSV, stats)
- [ ] Generate comparison tables

### Paper (Week 7)
- [ ] `paper/main.typ` — Typst template
- [ ] `paper/build_paper.py` — Pipeline (formulas → figures → PDF)
- [ ] `paper/lean/` — (Optional) Formal proofs of convergence

---

## Novelty Statement (for paper)

**What's new:**
1. **Quantum-inspired algorithm for P-systems** — First application of quantum concepts to membrane computing optimization
2. **Empirical validation on CEC2017** — Shows competitive performance vs. GA, PSO
3. **Formula-to-code traceability** — Demonstrates math-trace methodology for reproducible research

**What's not new:**
- Malta benchmarking framework (third-party)
- Cyprus P-system language (third-party, minor modifications)
- CEC2017 functions (standard benchmark)

---

## Success Criteria

- [ ] Repo cleanly organized (third-party / novel / paper)
- [ ] Quantum-inspired algorithm documented in SymPy (model.py)
- [ ] Benchmarks run on 11-function CEC2017 subset
- [ ] Paper drafted using math-trace
- [ ] Submitted to arXiv by week 11
