#set document(title: "Quantum-Inspired P-Systems for Optimization", author: "Mark Alexiuk")
#set page(numbering: "1")
#set heading(numbering: "1.")

= Quantum-Inspired P-Systems for Optimization: A Formula-to-Code Approach

#set text(font: "New Computer Modern")

== Abstract

#block[
  This paper introduces Quantum-Inspired P-Systems (QIPS), combining quantum-inspired
  computing concepts with membrane system formalism for continuous optimization.
  We validate the approach on the CEC2017 benchmark suite against classical
  genetic algorithms, demonstrating the viability of hybrid quantum-inspired
  P-system optimization. All formulas and source code are version-controlled
  and traceable, enabling reproducible research via the math-trace methodology.
]

---

== 1. Introduction

// TODO: Fill after literature review
// - What is the research gap?
// - Why combine quantum-inspired + P-systems?
// - What's novel about our approach?
// - What do we claim to show in this paper?

_Placeholder: Introduction to be written after literature review._

---

== 2. Background

=== 2.1 P-Systems (Membrane Computing)

// TODO: Brief intro to P-systems
// - Definition of P-system
// - Basic operations (rules, particles, reactions)
// - Why P-systems for optimization?

_Placeholder: Background on P-systems._

=== 2.2 Quantum-Inspired Optimization

// TODO: Brief intro to quantum-inspired algorithms
// - What makes an algorithm "quantum-inspired"?
// - Superposition, interference, measurement
// - Existing QIGA and QiPSO work
// - Performance on benchmarks

_Placeholder: Background on quantum-inspired algorithms._

=== 2.3 CEC2017 Benchmark Suite

The CEC2017 Special Session Benchmark Suite provides 29 continuous optimization
functions grouped by category:

- *Basic Unimodal:* F1, F3, F4 (3 functions)
- *Multimodal:* F5–F10 (6 functions)
- *Hybrid:* F11–F20 (10 functions)
- *Composition:* F21–F30 (10 functions)

For this paper, we focus on a representative subset: F1, F3, F4, F5, F6, F8,
F11, F14, F17, F21, F26 (11 functions, 10D).

---

== 3. Method: Quantum-Inspired P-Systems

// TODO: Fill after formalizing algorithm in model.py

// AUTO-GENERATED FORMULAS (from model.py)
#include "generated/formulas.typ"

_Placeholder: Algorithm description to follow after formulas are defined._

=== 3.1 Quantum Superposition in P-Systems

// TODO: How do we encode quantum superposition in P-system particles?

=== 3.2 Quantum Interference via P-System Rules

// TODO: How do P-system rules implement quantum interference?

=== 3.3 Measurement and Collapse

// TODO: How does measurement/collapse work in P-systems?

---

== 4. Experimental Setup

=== 4.1 Algorithms

We compare two algorithms on 10D CEC2017 subset:

1. *Genetic Algorithm (GA):* Baseline classical algorithm
   - Population: 50 individuals
   - Generations: 200
   - Crossover probability: 0.8
   - Mutation probability: 0.1

2. *Quantum-Inspired P-Systems (QIPS):* Our novel approach
   - // TODO: Add QIPS-specific parameters

=== 4.2 Benchmark Protocol

- *Dimensions:* 10D only (for initial validation)
- *Functions:* 11 selected CEC2017 functions
- *Runs per function:* 30 independent runs
- *Metrics:* Mean, standard deviation, best, worst
- *Statistical test:* Mann-Whitney U test (α = 0.05)

---

== 5. Results

#block[
  *Results to be updated after benchmarking*
]

// AUTO-GENERATED FIGURES (from benchmarks/results/)
// Placeholder: Benchmark comparison plots

#figure(
  align(center, text(size: 10pt, "[Convergence plot: GA vs. QIPS on CEC2017 subset]")),
  caption: [Placeholder for convergence comparison]
)

#figure(
  align(center, text(size: 10pt, "[Performance table: Mean, Std, Best across functions]")),
  caption: [Placeholder for numerical results]
)

---

== 6. Discussion

// TODO: Fill after seeing results

- How does QIPS compare to GA?
- Which functions favor QIPS over GA?
- Scalability to higher dimensions?
- Computational cost analysis?

---

== 7. Reproducibility

All code and formulas are version-controlled and traceable:

- *Repository:* https://github.com/baseline0/membrane
- *Formulas (source of truth):* `paper/model.py` (SymPy, line numbers linked)
- *Algorithm implementation:* `algorithms/quantum_inspired.py`
- *Benchmark runner:* `benchmarks/runners/cec2017_subset.py`
- *Results:* `benchmarks/results/` (CSV, plots)
- *Build pipeline:* `paper/build_paper.py` (auto-generates this PDF)

To rebuild this paper from scratch:

```
cd paper
python build_paper.py
```

This ensures formula-code traceability: every equation in this paper links
back to specific lines in `model.py`, enabling readers to verify correctness
and extend the work.

---

== 8. Conclusion

_To be written after results._

---

== References

_References to be added after literature review._

---

*Generated with math-trace: formula-to-code traceability for research papers*
