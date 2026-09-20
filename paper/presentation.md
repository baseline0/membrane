---
marp: true
theme: default
paginate: true
math: katex
---

# P-Systems & Membrane Computing
## From Biology to Algorithms

**Formula-to-Code Traceability for Reproducible Research**

https://github.com/baseline0/membrane

---

# The Biological Inspiration

A cell is not just a balloon of fluid—it's a hierarchical factory.

**Three Key Features:**
- **Plasma Membrane**: Selectively controls what enters/exits
- **Organelles**: Specialized rooms for specific reactions
- **Parallelism**: Millions of reactions happen simultaneously

*Example: Lysosomes*
- Break down waste
- Isolated in membrane
- Prevent damage to cell
- Work in parallel with mitochondria

**Question (1998):** What if we could compute using cellular structures?

---

# Gheorghe Păun's Insight (1998)

*What if we use membranes to compute?*

Instead of binary (1s and 0s) on silicon, use three ingredients:

1. **Membrane Structure** ($\mu$): Nested hierarchical regions
2. **Multisets of Objects**: Abstract "molecules" with quantities
3. **Evolution Rules**: "Chemical reactions" that transform objects

**Key Innovation: Maximal Parallelism**
- All applicable rules fire *simultaneously* in each step
- No sequential processing—true parallel computation

---

# Formal Definition: A P-System

A P-system is a tuple: $(\mu, w_1, w_2, R)$

**Components:**
- $\mu$: Hierarchical membrane structure (tree of nested membranes)
  - Outermost = "skin membrane"
  - Regions are spaces inside membranes

- $w_i$: Initial multisets (objects in each region)
  - Example: $w_1 = \{a, a, a\}$ (three copies of $a$)

- $R$: Evolution rules (reactions)
  - Example: $a \to b \, b$ (an $a$ becomes two $b$'s)

**Evolution Process:**
1. Apply all applicable rules simultaneously
2. Objects transform and travel across membranes
3. Continue until no more rules apply (halt)
4. Read output from designated region

---

# Concrete Example: Compute 3 × 2

## Setup: Two Nested Membranes

**Membrane Structure:**
```
┌─────────────────┐
│  Membrane 1     │  (outer, "skin")
│  ┌───────────┐  │
│  │ Membrane2 │  │  (inner, "working")
│  └───────────┘  │
└─────────────────┘
```

**Initial State:**
- Membrane 2: $\{a, a, a\}$ (3 objects)
- Membrane 1: empty (output region)

**Goal:** Count objects in Membrane 1
**Expected:** 6 objects ($3 \times 2 = 6$)

---

# The Rules

We define two evolution rules:

**Rule 1:** $a \to b \, b$
- Each $a$ becomes two $b$'s
- Both $b$'s stay in Membrane 2

**Rule 2:** $b \to c$
- Each $b$ becomes a $c$ and exits to Membrane 1

Our formulas are defined in code:
- Rule 1: {{formula:mult_rule1}}
- Starting with: {{formula:mult_input}} objects

---

# Step 1: Rule 1 Fires Simultaneously

**Current State:** Membrane 2 has $\{a, a, a\}$

**Maximal Parallelism Rule:**
All three $a$ objects apply Rule 1 *at the same time*
- $a_1 \to b_1, b_2$
- $a_2 \to b_3, b_4$
- $a_3 \to b_5, b_6$

**After Step 1:**
- Membrane 2: {{formula:mult_step1_output}} objects
- Membrane 1: empty

**Interpretation:** {{formula:mult_input}} × 2 = {{formula:mult_step1_output}}

---

# Step 2: Rule 2 Fires Simultaneously

**Current State:** Membrane 2 has {{formula:mult_step1_output}} $b$ objects

**Rule 2 Application:**
All six $b$ objects are consumed simultaneously:
- Each $b$ transforms into a $c$
- Each $c$ is expelled to Membrane 1

**After Step 2:**
- Membrane 2: empty
- Membrane 1: {{formula:mult_final}} objects

**Computation Halts:**
- No more rules apply
- Final answer: count $c$'s in output = {{formula:mult_final}}

✓ **Verified:** $3 \times 2 = 6$

---

# Key Insight: Parallelism Power

**Classical Algorithm:**
```python
result = 0
for i in 1..3:
    result += 2
```
- Steps: ~3 iterations
- Time: $O(n)$

**P-System:**
```
Membrane 2: a, a, a
Rule 1: a → b b
Rule 2: b → c_out
```
- Steps: 2 (all objects react in parallel)
- Time: $O(\log n)$ or constant!

**Theoretical Speedup:** {{formula:time_complexity}}

With exponential parallelism over {{formula:time_complexity|t=10}} steps, we get:

$2^{10} = 1024$ potential parallel operations!

---

# Our Formulas: Defined in Code

All formulas are **source of truth** in `model.py`

**Membrane Structure:**
- {{formula:membrane_hierarchy}} (d levels of nesting)

**Multiset Cardinality:**
- {{formula:multiset_cardinality}} (distribute n objects among m types)

**Parallelism Bound:**
- {{formula:max_rules_per_step}} (max rules firing per step)

**Computational Complexity:**
- {{formula:time_complexity}} (exponential speedup)
- {{formula:objects_per_step}} (objects created per step)

---

# Formula-to-Code Traceability

**One source of truth:** `model.py`

```python
# model.py (SOURCE OF TRUTH)
mult_input = sp.Integer(3)
mult_rule1 = sp.Lambda((n,), 2 * n)

FORMULAS = {
    "mult_input": Formula(
        id="mult_input",
        expr=mult_input,
        source_line=65
    ),
    ...
}
```

**Auto-generated in this presentation:**
- Every formula substituted via `{{formula:id}}`
- Source line reference added as comment
- Change `model.py` → automatically updates this presentation

**Reproducible Research!**

---

# Why Membrane Computing?

## For Regulatory & Compliance
- Natural model of hierarchical domains (federal → enterprise → team)
- Bio-inspired parallelism solves distributed constraint satisfaction
- Tested against genetic algorithms & fuzzy inference

## For Research & AI
- Alternative algorithm class when NN and classical methods plateau
- Quantum-ready: P-systems map naturally to quantum computing
- Research-to-practice pipeline: theory → implementation → benchmarks

## For Reproducibility
- Formula-to-code traceability
- Every equation links to its source line
- Tests validate formulas match implementation

**This repository bridges academic theory with engineering practice.**

---

# Next Steps

## Phase 1: ✓ Complete
- [x] P-system formulas defined (SymPy)
- [x] Paper building with auto-generated formulas
- [x] Presentation slides with formula references

## Phase 2: In Progress
- [ ] Quantum-inspired P-systems (QIPS) formulation
- [ ] Benchmark suite integration (CEC2017)
- [ ] Performance comparisons (GA vs QIPS)

## Phase 3: Future
- [ ] Lean formalization (optional)
- [ ] Palomar registry integration
- [ ] Published paper & reproducible artifact

---

# The Future of Computation

**Biological Inspiration → Mathematical Formalism → Executable Code**

**Questions?**

Reproducible research via *formula-driven slides*

https://github.com/baseline0/membrane
