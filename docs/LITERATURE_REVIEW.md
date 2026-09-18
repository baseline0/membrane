# Literature Review: Quantum-Inspired Optimization & P-Systems

## Goal
Understand the current landscape before making novelty claims.

---

## Research Questions

### RQ1: Quantum-Inspired Optimization Algorithms
- What does "quantum-inspired" mean in optimization literature?
- Key papers (Han et al., Narayanan & Moore, others)?
- Current state-of-the-art implementations?
- Performance on CEC2017 benchmarks?

**Key terms to search:**
- "quantum-inspired genetic algorithm" (QIGA)
- "quantum-inspired particle swarm" (QiPSO)
- "quantum bits" (qubits) in classical optimization
- "superposition" and "interference" in algorithms

**Databases:**
- IEEE Xplore
- ACM Digital Library
- Google Scholar
- arXiv

**Papers to find:**
- [ ] Han et al. (2002) — Original QIGA
- [ ] Narayanan & Moore (1996) — Early quantum-inspired GA
- [ ] Recent QIGA papers on CEC2017
- [ ] PSO quantum variants (Coelho et al., others)

---

### RQ2: P-Systems for Optimization
- What optimization problems have P-systems tackled?
- Existing P-system algorithms in literature?
- P-systems vs. GA/PSO/other metaheuristics?
- Any existing quantum + P-system work?

**Key terms to search:**
- "membrane systems" + "optimization"
- "P-systems" + "genetic algorithm"
- "P-systems" + "benchmark"
- "membrane computing" + "evolution"

**Papers to find:**
- [ ] Georghe Păun — P-system foundational work
- [ ] Optimization using P-systems papers
- [ ] Comparisons: P-systems vs. GA/PSO
- [ ] Any quantum-inspired P-system papers

---

### RQ3: CEC2017 Benchmark Results
- What are typical performance levels on CEC2017?
- GA baseline performance (various papers)?
- PSO baseline performance (various papers)?
- State-of-the-art algorithms on CEC2017?

**Key papers to find:**
- [ ] CEC2017 competition papers
- [ ] Benchmark papers using CEC2017 (2017-2024)
- [ ] Typical GA/PSO results for reference
- [ ] Recent winners on CEC2017

**Metrics to note:**
- Mean function value (lower = better)
- Standard deviation
- Convergence speed (number of evaluations)
- Computational cost

---

## Findings Template

### Paper Summary
**Title:** [title]
**Authors:** [authors]
**Year:** [year]
**Link:** [DOI or URL]

**Key contribution:**
[One sentence on what's novel]

**Methods:**
- Algorithm: [QIGA, QiPSO, etc.]
- Benchmark: [CEC2017, etc.]
- Dimensions: [10D, 30D, etc.]
- Baseline: [GA, PSO, etc.]

**Results relevant to us:**
- Performance on CEC2017: [if tested]
- Comparison to GA/PSO: [if available]
- Novel aspects: [what makes it different]

**Relevant quotes:**
[Any key passages about quantum-inspired OR P-systems OR benchmarking]

---

## Checklist: What We Need to Learn

### Quantum-Inspired Optimization
- [ ] Definition of quantum-inspired (what makes it "quantum"?)
- [ ] How superposition is encoded (qubits vs. classical bits)
- [ ] How interference works (constructive vs. destructive)
- [ ] Measurement operation (collapse to classical state)
- [ ] Convergence properties (theoretical + empirical)
- [ ] CEC2017 performance for existing QIGA/QiPSO

### P-Systems for Optimization
- [ ] Basic P-system rules and operations
- [ ] How P-systems model optimization (population, fitness, rules)
- [ ] Comparison metrics: P-systems vs. GA/PSO
- [ ] Any existing quantum + P-system ideas

### Our Potential Novelty
- [ ] Is quantum-inspired + P-systems unique?
- [ ] What would make this different from existing QIGA?
- [ ] What would make this different from existing P-system optimization?
- [ ] What claim can we defend with CEC2017 results?

---

## Gaps to Fill (After Literature Review)

Once you've read key papers, come back and fill these:

### Gap 1: Quantum-Inspired P-Systems (QIPS)
**Question:** Has anyone combined quantum-inspired + P-systems?
- [ ] Yes — cite paper, understand their approach
- [ ] No — this could be our novelty claim
- [ ] Partial — similar but different enough to distinguish

### Gap 2: Our Algorithm's Innovation
**Question:** What makes our quantum-inspired P-system different?
- Encoding: How do we represent quantum states in P-system particles?
- Rules: How do quantum operations (superposition, interference) map to P-system rules?
- Performance: Why should it outperform standard GA/PSO on CEC2017?

### Gap 3: Novelty Statement (to be updated)
**Current hypothesis:**
"We apply quantum-inspired concepts (superposition, interference) to P-systems for the first time, creating a novel optimization algorithm. We validate on CEC2017 subset against GA baseline."

**To verify:**
- [ ] Is this actually novel? (lit review)
- [ ] Is it defensible? (can we show outperformance or unique properties?)
- [ ] What are the limitations? (when/why it works or doesn't)

---

## Research Log

### Session 1: [Date]
- **Papers read:** [list]
- **Key findings:** [bullet points]
- **Questions raised:** [new questions]
- **Next steps:** [what to research next]

### Session 2: [Date]
[To be filled as you research]

---

## Final Deliverable: Novelty Statement

After lit review, update this to reflect what we actually know:

> "We propose **Quantum-Inspired P-Systems (QIPS)** for optimization, combining quantum-inspired computing concepts (superposition, interference, measurement) with P-system formalism. To our knowledge, this is the first application of [SPECIFY: quantum-inspired OR P-systems OR BOTH] to [SPECIFY: CEC2017 OR optimization OR BOTH]. We validate against GA baseline on 10D CEC2017 subset, demonstrating [SPECIFY: faster convergence OR better solution quality OR unique behavior]."

---

## Success Criteria

- [ ] Read 5-10 key papers on quantum-inspired algorithms
- [ ] Read 3-5 papers on P-systems for optimization
- [ ] Read 2-3 CEC2017 benchmark papers
- [ ] Understand quantum-inspired concepts (superposition, interference, measurement)
- [ ] Understand P-system formalism (particles, rules, reactions)
- [ ] Identify what's novel about combining them
- [ ] Draft defensible novelty statement
