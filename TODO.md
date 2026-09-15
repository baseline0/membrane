# Malta: Research & Commercial Roadmap

**Mission:** Build a publication-quality benchmarking framework for membrane computing (P-Systems) that funds quantum computing research through insurance consulting.

---

## Track A: Insurance Consulting (Year 1 Revenue)

**Goal:** Land first consulting engagement ($250k–$500k) for FRPS-based explainable AI in insurance.

### Phase 1: Insurance POC (Now)
- [ ] Build proof-of-concept: homeowner premium rating using FRPS rules
- [ ] Deliverable: End-to-end Malta simulation → audit trail → regulatory report
- [ ] Feature work:
  - [ ] Fuzzy membership functions (already: `malta/fuzzy.py`)
  - [ ] Rule tracing (membrane trace for audit trail)
  - [ ] Statistical harness (30+ runs, confidence intervals)
  - [ ] Export to compliance format (JSON + LaTeX tables)
- [ ] Demo: Insurance underwriter walk-through (show explainability vs SHAP)

### Phase 2: Cold Outreach (Q4 2025)
- [ ] Target: State insurance commissioners, NAIC researchers, mid-tier insurers
- [ ] Pitch: "FRPS for explainable underwriting—regulators won't second-guess rule engines"
- [ ] Channels: LinkedIn (compliance/AI officers), Insurance Thought Leaders conference, EU insurance tech roundtables

### Phase 3: Pilot (Early 2026)
- [ ] First client engagement: 14-day pilot ($15k–$30k)
- [ ] Deliverable: Custom FRPS model for their underwriting (actual data)
- [ ] Goal: Successful pilot → $250k–$500k long-term contract

---

## Track B: Research (Publication Path)

**Goal:** Publish peer-reviewed comparison of Membrane Evolutionary Algorithms vs SOTA (CEC2017).

### Year 1: Benchmark Comparison Paper

**Timeline:** Now → June 2025

**Deliverables:**
1. **Benchmark suite working:** CEC2017 + TSPLIB (10 functions, 30 dimensions, 30 seeds)
2. **Baseline algorithms:** Genetic Algorithm (DEAP), PSO, XGBoost
3. **Statistical harness:** Significance tests (Friedman + Wilcoxon)
4. **Publication-ready report:**
   - [ ] Results table (mean ± std, ranking)
   - [ ] Pareto frontier plot
   - [ ] Statistical significance matrix
   - [ ] LaTeX template for IEEE CEC/GECCO submission

**Current status:** ✅ CEC2017 Docker build working, benchmarking harness in place

**Next steps:**
- [ ] Run full benchmark suite (3 dimensions: 10D, 30D, 50D)
- [ ] Aggregate results → `reports/cec2017_comparison/`
- [ ] Draft paper: "Membrane Evolutionary Algorithms: Empirical Analysis" (sections 1–4)
- [ ] Target venue: IEEE CEC 2025 (deadline ~Dec 2024) or GECCO 2025 (March)

### Year 2: Quantum-Inspired Membrane Algorithms

**Goal:** Publish QMEA (Quantum-Inspired Membrane Evolutionary Algorithms) paper

**Scope:**
- [ ] Add quantum-bit representation to Malta
- [ ] Implement rotation gates (classical simulation)
- [ ] Benchmark on CEC2017 + combinatorial (knapsack, TSP variants)
- [ ] Paper: "Quantum-Inspired FRPS for Combinatorial Optimization"
- [ ] Venue: Journal of Membrane Computing or Natural Computing (peer-reviewed)

---

## Track C: Knowledge Base

**Goal:** Build authoritative reference for quantum membrane computing.

### Phase 1: Literature Review
- [ ] Create `docs/quantum/research/sota.md` (30+ papers catalogued)
  - Scope: P-Systems, fuzzy logic, quantum computing, membrane algorithms
  - Format: YAML metadata (title, authors, year, key ideas, relevance)
- [ ] Obsidian notes: `docs/quantum/notes/` with brainstorms

### Phase 2: Research Synthesis
- [ ] Publish selective synthesis → `docs/quantum/research/`
- [ ] Target: 3–4 polished research documents (100+ citations)

---

## Working Commands (For Agents)

```bash
cd /home/mark/projects/membrane

# Development
just test                # All tests (unit + integration)
just test-unit           # Fast feedback loop
just test-integration    # Slower, full component tests
just lint                # Ruff + pre-commit
just check               # Lint + test (CI-like)
just commit              # Make a commit

# Benchmarking
just bench-example       # 3 seeds, 5 functions, 10D (fast demo, ~2 min)
just bench-quick         # 10 seeds, 10 functions, 30D (medium, ~15 min)
just bench-full          # 30 seeds, all 29 functions, 10D (slow, ~1 hour)

# Maintenance
just clean               # Remove artifacts (sims/, output/, caches)
just tree                # Project structure + line counts
```

---

## Success Criteria (Q4 2025)

**Insurance Track:**
- [ ] POC complete and demo-ready
- [ ] Cold outreach campaign launched (15+ target companies identified)
- [ ] At least 2 warm leads for consulting engagement

**Research Track:**
- [ ] Full benchmark suite run (3 dimensions)
- [ ] Paper drafted (sections 1–5, results, figures)
- [ ] Submitted to IEEE CEC 2025 or GECCO 2025 (or both)

**Knowledge Base:**
- [ ] SOTA literature review (30+ papers catalogued)
- [ ] Brainstorm notes on quantum angles

---

## Dependencies & Blockers

**External:**
- CEC2017 C library build (Docker available, local gcc optional)
- Benchmark datasets (symlinked or fetched on first run)

**Internal:**
- [ ] Insurance domain expertise (you have this; leverage existing insurance consulting network)
- [ ] Publication readiness (figure quality, statistical rigor, writing clarity)
- [ ] Benchmark reproducibility (Docker, random seeds, isolation)

---

## Next Immediate Actions for Agents

1. **Insurance POC:**
   - Build homeowner rating example with FRPS rules
   - Ensure audit trail traces membrane execution
   - Export to LaTeX table format

2. **Benchmarking:**
   - Run `just bench-example` to validate pipeline (all seeds/functions complete)
   - If successful → schedule `just bench-full` for longer run

3. **Research:**
   - Start SOTA literature review (docs/quantum/research/sota.md)
   - List 30+ key papers on P-Systems, fuzzy, quantum computing

---

**Timeline:** Insurance POC (Week 1–2) → Benchmark Paper (Week 3–8) → Outreach (Week 9+)
