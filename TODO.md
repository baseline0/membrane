# Membrane Computing & Benchmarking + Formula-Driven Presentations

**Current Phase:**
- Phase 5 (Dashboard & Orchestration) — Primary work
- Phase 2 (Conference Presentation) — Formula-driven slides (NEW)

**Mission:**
- Build publication-quality benchmarking framework + dashboard for membrane/P-Systems research
- Demonstrate formula-to-code traceability for reproducible research talks
- Pilot production-grade formula-driven Marp presentation system

---

## Formula-Driven Presentations (Phase 1-2)

### Phase 1: Foundation & Hardening ✅ COMPLETE

**What we built:**
- ✅ Enhanced Formula class with locked SymPy options + symbol aliasing + assumptions
- ✅ Deterministic rendering (formula rendering identical across SymPy versions)
- ✅ Formula index generation with LaTeX hashing + commit hash
- ✅ Formula validation with actionable error messages
- ✅ `just present` one-command build pipeline
- ✅ SymPy version pinning (>=1.14.0,<1.15.0)
- ✅ Symbol assumption completeness checks
- ✅ Audit trail (commit hash + LaTeX hash in index)

**Repository:** https://github.com/baseline0/math-trace (market assessment in docs/)

### Phase 2: Conference Presentation & Friction Collection (NOW)

**Before using for conference talk:**
- [x] Add CI template (GitHub Actions with `--strict` mode) — DONE
- [x] Create pre-commit hook (validates formulas on `presentation.md` changes) — DONE
- [x] Stress test suite (5 tests, all passing) — DONE
- [x] Friction log for collecting real-world feedback — DONE
- [ ] Install pre-commit hook: `ln -sf ../../.git/hooks/pre-commit-formulas .git/hooks/pre-commit`
- [ ] Verify CI passes on a PR with formula changes
- [ ] Add README documentation with verification story
- [ ] Document troubleshooting guide (symbol aliasing, assumptions, etc.)
- [ ] Add QR code/link to feedback form on last slide
- [ ] Implement formula index PDF appendix (append to presentation PDF)

**During conference preparation:**
- [ ] Use `just present` for membrane P-Systems conference talk
- [ ] Collect friction points (see "Friction Collection" below)
- [ ] Log issues in "Feedback & Iteration Log" (math-trace/docs/)
- [ ] Ask collaborators: "Did formula index help verify correctness?"

**Friction Collection Checklist:**
```
Symbol Aliasing:
  [ ] Were mapping dicts easy to maintain?
  [ ] Did collaborators understand code-name → display-name?
  [ ] Any surprises with LaTeX symbol rendering?

Assumptions:
  [ ] Did any formulas render differently than expected?
  [ ] Were locked assumptions helpful for reproducibility?
  [ ] Any SymPy version-related issues?

CI/Workflow:
  [ ] Did `just present --strict` catch errors reliably?
  [ ] Any flakiness in Marp rendering or PDF export?
  [ ] Build times acceptable?

Presentation:
  [ ] Did reviewers find formula index useful?
  [ ] Was commit hash audit trail valuable?
  [ ] LaTeX hash verification story clear to audience?
```

**Phase 2 Exit Criteria:**
- [ ] Conference presentation delivered successfully
- [ ] 0 formula drift incidents (build would have caught them)
- [ ] Feedback log updated with friction points
- [ ] Ready to decide on Phase 3 (PyPI or internal-only)

### Phase 3: PyPI Decision (6+ months)

**Metrics for PyPI publication:**
- [ ] Used for 2+ conference presentations
- [ ] 3+ unsolicited requests from other researchers
- [ ] No critical workflow friction points
- [ ] Committed to long-term maintenance

---

## Phase 5: Dashboard & Metrics (PRIMARY)

**Status:** ✅ Metrics infrastructure complete. Dashboard visualization in progress.

**Done:**
- ✅ Benchmark metrics schema (GA/PSO convergence, algorithm comparison)
- ✅ Metrics collection pipeline (just bench-metrics)
- ✅ Historical metrics logger (fleet-wide compliance trends)
- ✅ Glossary ingestion metrics (progress tracking)
- ✅ MCP usage instrumentation (ops/day tracking)

**Next:**
- [ ] Dashboard visualization layer (trends, convergence curves, algorithm comparison)
- [ ] Fleet health reporting (monthly snapshots)
- [ ] ROI dashboard (MCP usage → tokens saved estimates)

---

## Future Work (Deferred)

### Insurance Consulting Track (Year 2+)
- [ ] Insurance POC (homeowner premium rating via FRPS rules)
- [ ] Regulatory reporting (audit trail, compliance export)
- [ ] Cold outreach & pilot engagement

### Research Publication (Year 2+)
- [ ] Full benchmark paper (GA/PSO on CEC2017)
- [ ] Quantum-inspired algorithms (QMEA paper)
- [ ] Target venue: IEEE CEC or GECCO

### Knowledge Base (Year 2+)
- [ ] Literature review (30+ papers on P-Systems, fuzzy, quantum)
- [ ] Research synthesis docs

---

## Commands

### Formula-Driven Presentations (NEW)
```bash
just present              # Full pipeline: export → build → validate → index
just formula-check        # Verify formula consistency (for CI)
just paper                # Build Typst paper (with formulas)
just paper-all            # Build everything (paper + presentation)
```

### Benchmarking (Phase 5)
```bash
just test-unit            # Fast unit tests
just bench-example        # 3 seeds, 5 functions, 10D (quick validation)
just bench-metrics        # Collect metrics from benchmarks_example.csv
```

### Documentation
- **Formula-driven presentations:** See paper/presentation.md and math-trace/docs/FORMULA_SLIDES_MARKET_ASSESSMENT.md
- **Benchmarking metrics:** See docs/BENCHMARK_METRICS_FORMAT.md for schema and dashboard integration
- **P-Systems formulas:** See paper/model.py (source of truth)
