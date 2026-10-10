# membrane: Presentation & Benchmarking

Research benchmarking + publication framework for P-Systems.

---

## 🚨 Blockers - `blocker`

- [ ] **Phase 2: Reproducibility & metadata validators** (NEXT). Phases 3 and 4 depend on it. Effort 5–6h, tests ~50.
  - Code execution validator (sandbox, timeouts)
  - Data access validator (checksums, availability)
  - Results validator (output comparison ±5%)
  - License, author, and keyword validators
  - Archive integrity checking

## ⚡ Quick Wins - `quickwin`

- [ ] Add README documentation with verification story [TTV: 1h]
- [ ] Add QR code or link to the feedback form on slides [TTV: 30m]
- [ ] Prepare ICAI 2026 conference submission [TTV: 2h]
  - Finalize paper section
  - Extract 3–5 slides
  - Draft abstract (250 words)

## 🔧 Tech Debt - `techdebt`



## 📋 Features - `feature`

### Phase 3: Zenodo integration and DOI pipeline (blocked by Phase 2)

- [ ] Zenodo API client (upload archives, mint DOIs). Effort 3–4h, tests ~25.
- [ ] DOI minting with retry logic
- [ ] Handle duplicate DOI detection
- [ ] Publication state machine (draft → submitted → published)

### Phase 4: Release automation (blocked by Phases 1–3)

- [ ] Tie together: review → upload → DOI → publish
- [ ] Release notes generation
- [ ] GitHub release and archive linkage

### Phase 5b: Publication-quality visualization (NEXT)

- [ ] `ConvergenceCurvesMatplotlib` (300dpi PDF/PNG)
- [ ] `AlgorithmComparisonMatplotlib` (publication styling)
- [ ] Register with `UseCase.PUBLICATION`
- [ ] Test PDF export

### Phase 5c/5d: Dashboard and extended charts (FUTURE)

- Altair for embedding, HTML scaffold, filters
- Heatmaps, trend lines, scorecards

### Phase 6: Telemetry and monitoring (FUTURE)

Event schema, circuit breakers (deterministic, no retry loops), metrics aggregation. Ollama monitor agent (Phase 2, diagnostic only, requires human review).

### Future work (deferred)

- Insurance consulting track (Year 2+): insurance POC (homeowner premium rating via FRPS rules), regulatory reporting (audit trail, compliance export), cold outreach and pilot engagement
- Research publication (Year 2+): full benchmark paper (GA/PSO on CEC2017), quantum-inspired algorithms (QMEA paper), target venue IEEE CEC or GECCO
- Knowledge base (Year 2+): literature review (30+ papers on P-Systems, fuzzy, quantum), research synthesis docs

---

## Reference

### Phase 5a: Pluggable visualization ✅ COMPLETE
- Plotly interactive (convergence, algorithm comparison, 14 tests passing)

### Phase 6 design principles
- ✅ **Deterministic policy enforces; LLM advises only:** code makes safety decisions
- ✅ **No recursive retries:** max 1 local attempt, then fallback to API
- ✅ **No self-certification:** worker cannot grade its own output; emit from wrapper
- ✅ **Version everything:** model_digest, prompt_version, schema_version, ollama_version, evaluator_version in every event
- ✅ **Quarantine requires human review:** automatic protection stops dispatch, but re-enabling a quarantined route needs sign-off
- ✅ **No unconstrained autonomy:** monitor recommendation is advisory, not a command

### Commands
```bash
just present              # Full pipeline: export → build → validate → index
just formula-check        # Verify formula consistency (for CI)
just paper                # Build Typst paper (with formulas)
just paper-all            # Build everything (paper + presentation)
just test-unit            # Fast unit tests
just bench-example        # 3 seeds, 5 functions, 10D (quick validation)
just bench-metrics        # Collect metrics from benchmarks_example.csv
```

### Documentation
- **Formula-driven presentations:** See paper/presentation.md and math-trace/docs/FORMULA_SLIDES_MARKET_ASSESSMENT.md
- **Benchmarking metrics:** See docs/BENCHMARK_METRICS_FORMAT.md for schema and dashboard integration
- **P-Systems formulas:** See paper/model.py (source of truth)

## Done (removed)

- Formula CI check passes locally (`uv run python validate_formulas.py --strict` in `paper/`). Not yet confirmed on GitHub Actions.
- Gitignored the generated demo HTML files (`algorithm_comparison_demo.html`, `convergence_curves_demo.html`).
- Formula index PDF appendix: `just formula-index-pdf` renders `paper/formula_index.md` to `paper/generated/formula_index_appendix.pdf`. Including it in `main.typ` is an open editorial call.
