# Membrane Computing Framework Roadmap & Backlog

> Looking to contribute or dispatch a task? Pick an item from **Next Up (Ready for Contribution)** or reference its item ID when enqueuing to nightshift.

## Contribution Workflow
To claim an item for manual contribution or dispatch to an automated worker:
1. Verify the item is in **Next Up** and has not been claimed.
2. For agent execution: reference the repository and ID (e.g. `just nightshift-enqueue membrane mem-010`).
3. Ensure all tests in `tests/` pass and pre-commit checks pass before merging.

---

## 🟢 Active (In Progress)

- [ ] **Technical Whitepaper Artifacts (pub-012)** <!-- id: mem-pub-012 -->
  - **Scope:** `paper/`, `paper/build_paper.py`, `paper/formula_appendix_builder.py`
  - **Context:** Technical whitepaper on membrane-inspired structures for governed agentic systems [roadmap: pub-012].
  - **Acceptance Criteria:** `just paper-all` builds `paper.pdf`, presentation slides, and validated formula appendix with zero Typst compilation errors.
  - **Complexity:** Medium

---

## 🟡 Next Up (Ready for Contribution)

- [ ] **Tier 2 Counting-Threshold Spec Implementation** <!-- id: mem-tier2-spec -->
  - **Scope:** `src/membrane/psystems/`, `tests/test_psystem_conformance.py`
  - **Context:** Count-based decisions specification in `docs/psystems/`
  - **Acceptance Criteria:** Implement deterministic threshold counting rules for P-system execution with 100% test coverage on boundary cases.
  - **Complexity:** Medium (1-2 days)

- [ ] **CEC2017 Benchmark Evaluation Harness** <!-- id: mem-cec2017-eval -->
  - **Scope:** `src/membrane/benchmarks/`, `docs/BENCHMARK_METRICS_FORMAT.md`
  - **Acceptance Criteria:** Execute bound-constrained benchmark suite against baseline genetic algorithms; export JSON metrics adhering to `BENCHMARK_METRICS_FORMAT.md`.
  - **Complexity:** Medium (2-3 days)

- [ ] **Community Contribution Guide and Documentation Polish** <!-- id: mem-docs-contrib -->
  - **Scope:** `CONTRIBUTING.md`, `docs/tutorial.md`
  - **Acceptance Criteria:** Provide end-to-end tutorial for defining membranes, rules, and catalysts, with runnable doctests.
  - **Complexity:** Low (1 day)

---

## 🔵 Later / Horizon

- [ ] **Release Membrane v1.5** <!-- id: mem-release-v15 -->
  - **Scope:** Package metadata, release notes, and publication package
  - **Context:** Strategic open-source deliverable [roadmap: oss-001].
  - **Acceptance Criteria:** Conference presentation materials, verified benchmark datasets, and methodology blog compiled for public release.
  - **Complexity:** High (1 week)

- [ ] **Quantum Membrane Hybrids Spikes** <!-- id: mem-quantum-spike -->
  - **Scope:** `docs/quantum/`
  - **Acceptance Criteria:** Formalize mathematical mappings between membrane transition states and quantum walk state vectors.
  - **Complexity:** Research Spike
