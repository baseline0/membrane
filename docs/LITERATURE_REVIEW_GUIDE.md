# Literature Review Workflow

This guide orchestrates the end-to-end literature review process for the Quantum-Inspired P-Systems paper.

---

## Overview: Three-Stage Pipeline

```
Stage 1: FETCH          Stage 2: REVIEW           Stage 3: SYNTHESIZE
┌─────────────────┐    ┌─────────────────┐      ┌──────────────────┐
│ Automated Paper │    │ Extract Key     │      │ Write Novelty    │
│ Fetcher + Cache │    │ Findings Into   │      │ Statement &      │
│                 │    │ LITERATURE_     │      │ Research Summary │
│ Respects Rate   │───→│ REVIEW.md       │─────→│                  │
│ Limits          │    │ Template        │      │ Feed into        │
│ (local DB)      │    │                 │      │ paper/model.py   │
└─────────────────┘    └─────────────────┘      └──────────────────┘
```

### Timeline
- **Weeks 1–2:** Literature review (Stages 1–3)
- **Week 3 onwards:** Implement algorithm in model.py based on findings

---

## Stage 1: Fetch Papers (Automated)

### Quick Start

```bash
# Initial fetch: tries to download all 10 papers
python scripts/paper_fetcher.py

# Check status: see which papers are available
python scripts/paper_status.py

# Retry failed: attempts to fetch papers that failed before
python scripts/paper_fetcher.py --retry

# Clean and restart: wipe cache, try fresh
python scripts/paper_fetcher.py --clean
```

### What Happens

The fetcher:
1. **Attempts multiple sources per paper** (arXiv, MDPI, IEEE, DOI, Google Scholar)
2. **Respects rate limits** (1-2s between requests per domain)
3. **Caches locally** in `reference/lit_review/` with SHA256 hash verification
4. **Maintains audit trail** in `.manifest.json` (what was fetched, from where, when)
5. **Is resumable** (re-running skips already-fetched papers)

### What Gets Saved

```
reference/lit_review/
├── .manifest.json              # Fetch audit trail (JSON)
├── .fetch.log                  # Fetch log (text)
├── Zhang_QuantumInspiredMembrane_2023.pdf    # Fetched paper
├── Liu_NovelHybridQuantum_2021.pdf            # Fetched paper
└── [8 more papers...]
```

**Manifest entry example:**
```json
{
  "Zhang_QuantumInspiredMembrane_2023": {
    "paper_name": "Zhang_QuantumInspiredMembrane_2023",
    "title": "Quantum-Inspired Membrane Computing: A Survey and Perspective",
    "success": true,
    "source": "MDPI",
    "filepath": "reference/lit_review/Zhang_QuantumInspiredMembrane_2023.pdf",
    "content_hash": "a1b2c3d4...",
    "timestamp": "2025-09-18T15:32:10.123456",
    "url": "https://www.mdpi.com/...",
    "error": null
  }
}
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "No papers found" | Ensure `paper_fetcher.py` ran successfully: check `.fetch.log` |
| Some papers failed | Run `python scripts/paper_fetcher.py --retry` |
| Corrupted cache | Run `python scripts/paper_fetcher.py --clean` |
| Want to manually add papers | Place PDF in `reference/lit_review/Name_Title_Year.pdf`, update `.manifest.json` |

---

## Stage 2: Review Papers & Extract Findings

### Setup

Open your papers as they become available:

```bash
# See what's ready
python scripts/paper_status.py

# Results show:
# ✅ AVAILABLE (5 papers) — ready to review
# ⏳ PENDING (5 papers) — fetcher still working
```

### For Each Paper

Read the paper and fill in [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md) using the **Findings Template**:

**Template (copy and fill for each paper):**

```markdown
### [Paper Name] — [Author], [Year]

**Title:** [Full title]

**Key contribution:**
[One sentence: what's the main novel idea?]

**Methods:**
- Algorithm type: [QIGA, QiPSO, P-system, etc.]
- Problem domain: [Optimization, simulation, etc.]
- Benchmark: [CEC2017, TSP, etc. — if applicable]
- Dimensions tested: [10D, 30D, 100D, etc.]

**Results relevant to us:**
- Performance on CEC2017: [Numerical results or table reference]
- Comparison to GA/PSO: [How does it perform vs. baselines?]
- Scalability: [Does it work at higher dimensions?]
- Novel aspects: [What makes it different from prior work?]

**Relevant quotes:**
> "[Key passage from paper: definition, result, or limitation]"

**Relevance to QIPS:**
[1-2 sentences: How does this paper inform our quantum-inspired P-system approach?]

**Open problems this paper mentions:**
- [Problem 1 they identify but don't solve]
- [Problem 2]
```

### Research Log

As you finish each paper, add an entry to **Research Log** in [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md):

```markdown
### Session 1: [Date]
- **Papers read:** Zhang (2023), Liu (2021)
- **Key findings:**
  - Quantum-inspired + membrane systems not previously combined
  - CEC2017 performance: quantum QIGA outperforms GA on F1-F5 by ~15%
  - Open problem: dimensionality collapse at D>30 suggests need for different exploration strategy
- **Questions raised:** How do we prevent premature convergence in high-D?
- **Next steps:** Read P-Lingua paper (#3) to understand P-system implementation details
```

---

## Stage 3: Synthesize & Write Novelty Statement

### Gaps to Fill

As you read, your mission is to answer these questions in [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md):

**Gap 1: Is quantum-inspired + P-systems unique?**
- [ ] Has someone combined them before? (Check all papers)
- [ ] If yes: How does our approach differ?
- [ ] If no: This could be our novelty claim

**Gap 2: What's our algorithm's innovation?**
- Encoding: How do we represent quantum states in P-system particles?
- Rules: How do quantum operations (superposition, interference) map to P-system rules?
- Performance: Why should it outperform standard GA/PSO on CEC2017?

**Gap 3: What's our novelty statement?**
Draft in the **Final Deliverable** section (bottom of LITERATURE_REVIEW.md):

**Template:**
```markdown
## Final Deliverable: Novelty Statement

"We propose **Quantum-Inspired P-Systems (QIPS)** for optimization,
combining quantum-inspired computing concepts (superposition, interference,
measurement) with P-system formalism.

To our knowledge, this is the first [FILL: application of quantum-inspired
concepts to P-systems / P-system approach to quantum-inspired optimization /
BOTH].

We validate against GA baseline on 10D CEC2017 subset, demonstrating
[FILL: faster convergence / better solution quality / unique convergence
behavior on specific function categories]."
```

**Success criteria (fill these in as you read):**
- [ ] Understand quantum-inspired concepts (superposition, interference, measurement)
- [ ] Understand P-system formalism (particles, rules, reactions, membranes)
- [ ] Identified existing QIGA papers and their limitations
- [ ] Identified existing P-system optimization papers
- [ ] Confirmed quantum-inspired + P-systems is novel (or identified prior work)
- [ ] Drafted defensible novelty statement

---

## Integration with Paper Infrastructure

Once literature review is done, findings feed directly into paper-building:

### 1. Model Formulas (paper/model.py)

Fill in SymPy formulas based on your LITERATURE_REVIEW.md findings:

```python
# From finding: "Zhang 2021 defines quantum superposition as..."
superposition = Formula(
    name="quantum_superposition",
    expr=sp.Matrix([...]),  # Based on Zhang formulation
    description="Quantum superposition encoding in P-system particles",
    source_line=42,
)
```

### 2. Algorithm Pseudocode (algorithms/quantum_inspired.py)

Implement based on findings:
- Which quantum gates to use (from QIGA papers)
- How membrane rules implement quantum operations (from P-system papers)
- Parameter settings (from CEC2017 comparisons)

### 3. Benchmark Configuration (benchmarks/runners/cec2017_subset.py)

Set baseline parameters based on literature:
- GA population/generation from literature baselines
- Which CEC2017 functions favor quantum-inspired (from results review)

### 4. Paper Sections (paper/main.typ)

- **Background → P-Systems & Quantum-Inspired:** Cite papers #1, #4, #6
- **Background → CEC2017:** Cite benchmark paper
- **Method → QIPS:** Cite original QIGA papers, explain P-system adaptation
- **Results → Comparisons:** Reference GA/PSO baselines from literature

---

## Checklist: Literature Review Phases

### Phase 1: Fetch (Week 1, Day 1)
- [ ] Run `python scripts/paper_fetcher.py`
- [ ] Run `python scripts/paper_status.py` to see what's available
- [ ] Note any failed fetches (expected for some papers)

### Phase 2: Read (Week 1-2)
- [ ] Read all available papers (prioritize #1, #4, #6 — foundational)
- [ ] Fill LITERATURE_REVIEW.md template for each paper
- [ ] Add research log entry after each session
- [ ] Answer gaps to fill (novelty detection, algorithm components)

### Phase 3: Synthesize (Week 2 end)
- [ ] Draft novelty statement (bottom of LITERATURE_REVIEW.md)
- [ ] Verify success criteria (8 items above)
- [ ] Identify which papers inform model.py formulas
- [ ] Map quantum concepts to P-system rules

### Phase 4: Integrate (Week 3+)
- [ ] Fill paper/model.py with SymPy formulas
- [ ] Implement algorithms/quantum_inspired.py
- [ ] Configure benchmarks/runners/cec2017_subset.py
- [ ] Draft paper/main.typ sections with citations

---

## Key Papers by Priority

| Priority | Papers | Why |
|----------|--------|-----|
| **MUST READ** | #1 (Zhang survey), #4 (Leporati quantum circuits), #6 (Păun open problems) | Foundational concepts |
| **SHOULD READ** | #2 (Zhang real-coded), #7 (Liu hybrid), #8 (Nishimura true quantum) | Practical algorithms, theory |
| **NICE TO READ** | #3 (P-Lingua tools), #5 (Xiao combinatorial), #9 (Valencia GPU), #10 (Liu synthesis) | Implementation details, hardware |

---

## Open Problems You'll Encounter

From the papers, you'll find these unsolved challenges:

1. **Measurement vs. Communication (Theory)** — How to transport superposed quantum states across membrane barriers without collapsing them?

2. **Dimensionality Collapse (Empirical)** — Why does QIPS degrade at D>30? Is it exploration/exploitation balance? Population diversity loss?

3. **Hardware Mapping (Practice)** — How to map P-systems to NISQ quantum hardware with limited qubit connectivity?

4. **Standardized Software (Infrastructure)** — No unified Python library for hybrid P-lingua + quantum circuit frameworks.

**Your paper can address one of these** (e.g., "We tackle Problem #2 by...").

---

## Resources

- **LITERATURE_REVIEW.md** — Main template file (edit directly)
- **PAPER_SOURCES.md** — Direct links to download papers manually
- **scripts/paper_fetcher.py** — Automated fetcher (handles caching, rate limits)
- **scripts/paper_status.py** — Status report (which papers are ready)
- **reference/lit_review/.manifest.json** — Audit trail (reproducible record of what was fetched)

---

## Questions?

- **Papers not downloading?** Check `reference/lit_review/.fetch.log` for details
- **Want to manually add a paper?** Save as `reference/lit_review/Author_Title_Year.pdf` and update `.manifest.json`
- **Need more papers?** Check citations in the 10 papers; arXiv often has related work
- **Stuck on novelty?** Look for open problems sections — those are research gaps you could fill

**Next:** Run `python scripts/paper_fetcher.py` and see how many papers download automatically.
