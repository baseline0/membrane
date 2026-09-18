# Research Strategy: QIPS at the Intersection

## The Landscape: 4 Open Problems

Academic consensus identifies four major unsolved challenges in Quantum-Inspired Membrane Computing (from curated papers):

### 1. **Measurement vs. Communication Dilemma** (Theoretical)
- **Problem:** True Quantum P-Systems face a paradox: passing superposed quantum states across membrane barriers requires measurement/filtering, but observation collapses superposition.
- **Status:** Unsolved. No consensus on non-destructive membrane transport rules.
- **Your angle:** Can we design P-system rules that preserve quantum coherence during inter-membrane communication?

### 2. **Dimensionality Collapse** (Empirical) ⭐ **MOST ADDRESSABLE**
- **Problem:** Quantum-inspired P-systems excel at 10D–30D (CEC2017), but degrade sharply at 50D–100D. Root cause: quantum rotation gates cause rapid diversity loss in sub-membranes.
- **Status:** Acknowledged but not solved. Papers report the problem, not fixes.
- **Your angle:** Propose an adaptive quantum-inspired exploration strategy that maintains diversity in high-D. Test on 10D CEC2017 subset first, scale to 30D+ if successful.

### 3. **Hardware Mapping** (Practice)
- **Problem:** All existing Quantum-Inspired Membrane Algorithms run sequentially or on classical GPUs. Mapping membranes to physical NISQ qubits is unexplored.
- **Status:** Unsolved. No implementations on real quantum hardware.
- **Your angle:** Out of scope for paper 1. Future work: "This framework could enable mapping to NISQ processors via..."

### 4. **Standardized Software** (Infrastructure)
- **Problem:** No unified open-source library combining P-lingua + Qiskit/Pennylane. Each research group rolls their own implementation.
- **Status:** Unsolved. Community pain point.
- **Your angle:** Use this project to build such a library. Position as reference implementation.

---

## Where QIPS Fits

### Hypothesis
**Quantum-Inspired P-Systems (QIPS) can address Problem #2 (Dimensionality Collapse) while advancing infrastructure (Problem #4).**

### Paper Structure Aligned with Open Problems

| Section | Open Problem | Contribution |
|---------|--------------|--------------|
| **Background** | Problems 1–4 | Literature review map |
| **Method: QIPS** | Problem #2 | Novel quantum-inspired + P-system combination; adaptive exploration strategy |
| **Benchmark Protocol** | Problem #2 | CEC2017 10D validation (pre-cursor to high-D work) |
| **Results** | Problem #2 | Demonstrate QIPS outperforms GA baseline on subset, doesn't collapse at 10D |
| **Infrastructure** | Problem #4 | math-trace reproducibility, open-source code framework |
| **Future Work** | Problems 1, 3 | Measurement paradox research; NISQ hardware mapping |

---

## Literature Review Mission

As you read the 10 papers, your **specific focus** is:

### ✅ MUST ANSWER
1. **Has anyone combined quantum-inspired + P-systems before?**
   - [ ] Yes → How? Can we differentiate?
   - [ ] No → This is our novelty claim

2. **What causes dimensionality collapse?**
   - [ ] Papers #1, #2, #7 should explain the mechanism
   - [ ] Extract: quantum rotation gate equations, population diversity metrics

3. **What adaptive strategies exist for preventing collapse?**
   - [ ] GA papers: tournament selection, adaptive mutation
   - [ ] PSO papers: inertia weight adaptation
   - [ ] P-system papers: membrane division strategy
   - [ ] Can we combine these in P-system rules?

4. **What's the baseline GA performance on CEC2017?**
   - [ ] Papers #1, #7 should provide tables
   - [ ] Extract: mean ± std for F1, F3–F8 (our subset)

### 🎯 BONUS QUESTIONS
5. **What makes P-systems well-suited for optimization?**
   - [ ] Parallelism (multiple membranes = multiple populations)
   - [ ] Hierarchy (skin membrane = global, elementary = local search)
   - [ ] Adaptability (rules can change per generation)

6. **What quantum concepts matter most?**
   - [ ] Superposition (parallel exploration)
   - [ ] Interference (rule interactions)
   - [ ] Measurement/collapse (when to exploit vs. explore)

---

## Novelty Statement Draft (to refine after reading)

**Current hypothesis** (to be validated/updated by lit review):

> "We propose **Quantum-Inspired P-Systems (QIPS)** for continuous optimization, combining quantum-inspired computing (superposition-based exploration, interference-based exploitation) with P-system formalism (hierarchical membranes, adaptive rules). To our knowledge, **this is the first integration of quantum-inspired concepts into membrane computing for global optimization**. We validate on CEC2017 benchmark (10D subset) against classical GA baseline, demonstrating that QIPS maintains solution diversity and convergence speed across problem classes where standard quantum-inspired algorithms degrade. This framework also serves as a reference implementation for standardized Quantum + P-system benchmarking (addressing infrastructure gap #4)."

---

## Literature Review Milestones

### Week 1: Reading & Extraction
- [ ] **Day 1–2:** Papers #1, #4, #6 (foundational: P-systems, quantum-inspired concepts, open problems)
- [ ] **Day 3–4:** Papers #2, #7, #8 (practical: real-coded algorithms, hybrid approaches, true quantum P-systems)
- [ ] **Day 5:** Papers #3, #5, #9, #10 (infrastructure: tools, combinatorial, GPU, synthesis)

**Daily output:** Fill LITERATURE_REVIEW.md with findings

### Week 2: Synthesis
- [ ] **Day 6–7:** Answer the 4 MUST-ANSWER questions; draft novelty statement
- [ ] **Day 8–9:** Extract specific equations/methods that will inform model.py
- [ ] **Day 10:** Finalize novelty statement + feedback loop

---

## What Success Looks Like

### After Lit Review
- ✅ You can answer: "What's novel about QIPS vs. existing QIGA/QiPSO/P-system work?"
- ✅ You have specific equations from literature to adapt (e.g., Zhang's superposition encoding)
- ✅ You have baseline GA numbers from CEC2017 to compare against
- ✅ You understand which P-system rules implement which quantum operations
- ✅ Novelty statement is defensible (not "we combined two things" but "we solved Problem X using this novel combination")

### After Implementation
- ✅ model.py contains SymPy formulas for QIPS (sourced from lit + your insight)
- ✅ cec2017_subset.py runs GA vs. QIPS on 10D, generates comparison plots
- ✅ main.typ paper auto-generates from model.py formulas + benchmark results
- ✅ Claim is verified: "QIPS outperforms GA on CEC2017 subset by X% without dimensionality collapse"

---

## Why This Matters

The four open problems aren't academic side-quests—they're blocking real progress:

1. **Measurement dilemma** blocks theoretical unification of quantum + P-systems
2. **Dimensionality collapse** blocks practical scalability (the reason QIGA hasn't replaced GA at D>30)
3. **Hardware mapping** blocks implementation on future quantum computers
4. **Software standardization** blocks reproducible research (everyone rebuilds)

**Your paper addresses #2 directly + #4 tangentially. That's a solid niche.**

---

## Next: Start Reading

1. Papers will arrive over next 24-48 hours (auto + manual fetches)
2. Open docs/LITERATURE_REVIEW_GUIDE.md
3. Use this strategy doc as your focus checklist
4. Fill LITERATURE_REVIEW.md as you read

The papers will teach you the landscape. Your job: find the gap and position QIPS to fill it.
