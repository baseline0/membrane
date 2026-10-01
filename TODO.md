# membrane: Presentation & Benchmarking

Research benchmarking + publication framework for P-Systems.

---

## Phase 2: Conference Presentation (IN PROGRESS)

Formula-driven slides (Phase 1 foundation complete). Prepare for membrane P-Systems conference talk.

- [ ] Verify CI passes on formula changes (GitHub Actions `--strict`)
- [ ] Add README documentation with verification story
- [ ] Document troubleshooting guide (symbol aliasing, assumptions)
- [ ] Add QR code/link to feedback form on slides
- [ ] Implement formula index PDF appendix

**During preparation:** Collect friction points (symbol aliasing, assumptions, CI/workflow, presentation clarity).

**Exit criteria:** Conference talk delivered, 0 formula drift incidents, feedback logged.

---

## Phase 5: Dashboard & Metrics

### Phase 5a: Pluggable Visualization ✅ COMPLETE
- Plotly interactive (convergence, algorithm comparison, 14 tests passing)

### Phase 5b: Publication-Quality Viz (NEXT)
- [ ] `ConvergenceCurvesMatplotlib` (300dpi PDF/PNG)
- [ ] `AlgorithmComparisonMatplotlib` (publication styling)
- [ ] Register with `UseCase.PUBLICATION`
- [ ] Test PDF export

### Phase 5c/5d: Dashboard & Extended Charts (FUTURE)
- Altair for embedding, HTML scaffold, filters
- Heatmaps, trend lines, scorecards

---

## Phase 6: Telemetry & Monitoring (FUTURE)

Event schema, circuit breakers (deterministic, no retry loops), metrics aggregation.
Ollama monitor agent (Phase 2, diagnostic only, requires human review).

- ✅ **Deterministic policy enforces; LLM advises only** — Code makes safety decisions
- ✅ **No recursive retries** — Max 1 local attempt, then fallback to API
- ✅ **No self-certification** — Worker cannot grade its own output; emit from wrapper
- ✅ **Version everything** — model_digest, prompt_version, schema_version, ollama_version, evaluator_version in every event
- ✅ **Quarantine requires human review** — Automatic protection stops dispatch, but re-enabling a quarantined route needs sign-off
- ✅ **No unconstrained autonomy** — Monitor recommendation is advisory, not a command

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
