#set document(title: "P-Systems & Membrane Computing: From Biology to Algorithms")
#set page(numbering: "1 / 1", margin: (top: 2em, bottom: 1.5em, left: 1.5em, right: 1.5em))
#set heading(numbering: "1.")
#set text(font: "New Computer Modern")

// Slide counter (manual)
#let slide(body) = {
  pagebreak()
  body
}

= P-Systems & Membrane Computing
<slide-title>

*From Biology to Algorithms*

Formula-to-Code Traceability for Reproducible Research

#align(center, text(size: 0.9em, gray)[
  https://github.com/baseline0/membrane
])

---

= The Biological Inspiration
<slide-bio>

A cell is not just a balloon of fluid—it's a hierarchical factory.

== Three Key Features

+ *Plasma Membrane*: Selectively controls what enters/exits
+ *Organelles*: Specialized rooms for specific reactions
+ *Parallelism*: Millions of reactions happen simultaneously

#block[
  *Example: Lysosomes*
  - Break down waste
  - Isolated in membrane
  - Prevent damage to cell
  - Work in parallel with mitochondria
]

*Question (1998):* What if we could compute using cellular structures?

---

= Gheorghe Păun's Insight (1998)
<slide-paun>

_What if we use membranes to compute?_

Instead of binary (1s and 0s) on silicon, use three ingredients:

+ *Membrane Structure* ($mu$): Nested hierarchical regions
+ *Multisets of Objects*: Abstract "molecules" with quantities
+ *Evolution Rules*: "Chemical reactions" that transform objects

#block[
  *Key Innovation:* Maximal Parallelism
  - All applicable rules fire *simultaneously* in each step
  - No sequential processing—true parallel computation
]

---

= Formal Definition: A P-System
<slide-definition>

A P-system is a tuple: $(mu, w_1, w_2, R)$

*Components:*

+ *$mu$*: Hierarchical membrane structure (tree of nested membranes)
  - Outermost = "skin membrane"
  - Regions are spaces inside membranes

+ *$w_i$*: Initial multisets (objects in each region)
  - Example: $w_1 = {a, a, a}$ (three copies of $a$)

+ *$R$*: Evolution rules (reactions)
  - Example: $a -> b space b$ (an $a$ becomes two $b$'s)

== Evolution Process

1. Apply all applicable rules simultaneously
2. Objects transform and travel across membranes
3. Continue until no more rules apply (halt)
4. Read output from designated region

---

= Concrete Example: Compute 3 × 2
<slide-example-setup>

== Setup: Two Nested Membranes

#columns(2, [
  *Membrane Structure:*
  ```
  ┌─────────────────┐
  │  Membrane 1     │  outer, "skin"
  │  ┌───────────┐  │
  │  │ Membrane2 │  │  inner, "working"
  │  └───────────┘  │
  └─────────────────┘
  ```

  #colbreak()

  *Initial State:*
  - Membrane 2: $a, a, a$ (3 objects)
  - Membrane 1: empty (output region)

  *Goal:* Count objects in Membrane 1 after rules apply

  *Expected:* 6 objects ($3 times 2 = 6$)
])

== Rules

+ Rule 1: $a -> b b$ (each $a$ becomes two $b$'s)
+ Rule 2: $b -> c_1$ (each $b$ becomes $c$ and exits to outer membrane)

---

= Step 1: Rule 1 Fires Simultaneously
<slide-step1>

*Current State:* Membrane 2 has ${a, a, a}$

== Maximal Parallelism

All three $a$ objects apply Rule 1 *at the same time*:
- $a_1 -> b_1, b_2$
- $a_2 -> b_3, b_4$
- $a_3 -> b_5, b_6$

Result:
- Membrane 2: ${b, b, b, b, b, b}$ (6 objects)
- Membrane 1: empty

*Interpretation:* $3 times 2 = 6$
- Each input ($a$) doubled
- No waiting—all happen in parallel

---

= Step 2: Rule 2 Fires Simultaneously
<slide-step2>

*Current State:* Membrane 2 has ${b, b, b, b, b, b}$

== Rule 2 Application

All six $b$ objects are consumed simultaneously:
- Each $b$ transforms into a $c$
- Each $c$ is expelled to Membrane 1 (outer region)

== After Step 2

- Membrane 2: empty
- Membrane 1: ${c, c, c, c, c, c}$ (6 objects)

*Computation Halts:*
- No more rules apply
- Final answer: count $c$'s in output = 6

#block[
  ✓ *Verified:* $3 times 2 = 6$
]

---

= Key Insight: Parallelism Power
<slide-parallelism>

Why is this remarkable?

#columns(2, [
  *Classical Algorithm:*
  ```
  result = 0
  for i in 1..3:
    result += 2
  ```
  Steps: ~3 iterations
  Time: $O(n)$

  #colbreak()

  *P-System:*
  ```
  Membrane 2: a, a, a
  Rule 1: a → b b
  Rule 2: b → c_out
  ```
  Steps: 2 (all objects react in parallel)
  Time: $O(log n)$ or constant!
])

*Theoretical Speedup:* $O(2^t)$ with exponential parallelism

This is why P-systems are powerful for constraint satisfaction and optimization!

---

= Our P-System Formulas
<slide-formulas>

All formulas are *source of truth* in code (`model.py`)

#columns(2, [
  *Membrane Structure:*
  $ 2^d $
  (d levels of nesting)

  *Multiset Cardinality:*
  $ binom(n + m - 1, m) $
  (distribute n objects among m types)

  *Parallelism Bound:*
  $ n $
  (max rules firing per step)

  #colbreak()

  *Multiplication Example:*
  - Input: $ 3 $
  - After Rule 1: $ 6 $
  - Final output: $ 6 $

  *Time Complexity:*
  $ 2^t $
  (exponential speedup potential)

  *Objects per Step:*
  $ 2n $
  (conservative upper bound)
])

#block[
  All formulas defined in `paper/model.py` and auto-generate into PDFs
]

---

= Formula-to-Code Traceability
<slide-traceability>

*One source of truth:* `model.py`

== Python (SOURCE OF TRUTH)

```python
# model.py
initial_a = sp.Integer(3)
rule1_output = initial_a * 2

FORMULAS = {
    "mult_example_input": Formula(
        expr=initial_a,
        description="...",
        source_line=65
    ),
}
```

== Typst (AUTO-GENERATED)

```typst
// presentation.typ (from model.py)
#let mult_example_input = $ 3 $
#let mult_example_step1 = $ 6 $
```

*Change one formula in `model.py` → automatically updates:*
- PDF paper
- This presentation
- All visualizations

*Reproducible research!*

---

= Why Membrane Computing?
<slide-why>

== For Regulatory & Compliance

- Natural model of hierarchical domains (federal → enterprise → team)
- Bio-inspired parallelism solves distributed constraint satisfaction
- Tested against genetic algorithms & fuzzy inference

== For Research & AI

- Alternative algorithm class when NN and classical methods plateau
- Quantum-ready: P-systems map naturally to quantum computing
- Research-to-practice pipeline: theory → implementation → benchmarks

== For Reproducibility

- Formula-to-code traceability (via math-trace)
- Every equation links to its source line
- Tests validate formulas match implementation

#block[
  *This repository bridges academic theory with engineering practice.*
]

---

= Next Steps
<slide-next>

== Phase 1: ✓ Complete

- [x] P-system formulas defined (SymPy)
- [x] Paper building with auto-generated formulas
- [x] Presentation slides with examples

== Phase 2: In Progress

- [ ] Quantum-inspired P-systems (QIPS) formulation
- [ ] Benchmark suite integration (CEC2017)
- [ ] Performance comparisons (GA vs QIPS)

== Phase 3: Future

- [ ] Lean formalization (optional)
- [ ] Palomar registry integration
- [ ] Published paper & reproducible artifact

---

= The Future of Computation
<slide-closing>

*Biological Inspiration → Mathematical Formalism → Executable Code*

#align(center + horizon, text(size: 1.2em, [
  Questions?
]))

Reproducible research via *math-trace*

https://github.com/baseline0/membrane
