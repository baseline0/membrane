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
- [x] Install pre-commit hook: `ln -sf ../../.git/hooks/pre-commit-formulas .git/hooks/pre-commit`
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

**Status:** ✅ Metrics infrastructure complete. Phase 5a (visualization foundation) complete.

### Phase 5a: Pluggable Visualization System ✅ COMPLETE

**Architecture:**
- ✅ `VizStrategy` base class (ABC for all viz backends)
- ✅ `UseCase` enum (DEMO, PUBLICATION, DASHBOARD)
- ✅ `VizRegistry` + `VizFactory` (pluggable pattern)
- ✅ `SampleMetrics` loader (bundled sample data)
- ✅ `ConvergenceCurvesPlotly` (interactive)
- ✅ `AlgorithmComparisonPlotly` (interactive)
- ✅ 14 passing unit tests
- ✅ Demo script (generates HTML in one command)

**Available Now:**
```python
from benchmarks.visualization import VizFactory, UseCase, SampleMetrics
metrics = SampleMetrics.load_default()
viz = VizFactory.get('convergence_curves', UseCase.DEMO)
fig = viz.render(metrics)
fig.show()
```

### Phase 5b: Publication-Quality Strategy (NEXT)

- [ ] `ConvergenceCurvesMatplotlib` (static PDF/PNG, 300dpi)
- [ ] `AlgorithmComparisonMatplotlib` (publication styling)
- [ ] Register with `UseCase.PUBLICATION`
- [ ] Test PDF export

### Phase 5c: Dashboard Integration (THEN)

- [ ] Altair strategy for embeddable JSON
- [ ] HTML dashboard scaffold
- [ ] Filters (dimension, algorithm selector)
- [ ] Live refresh button (`just bench-metrics`)

### Phase 5d: Extended Chart Types (FUTURE)

- [ ] Heatmap (functions × algorithms, color-coded)
- [ ] Trend lines (historical optimization progress)
- [ ] Scorecard cards (mean convergence, success rate)

---

## Phase 6: Telemetry & Monitoring (Foundation)

**Goal:** Separate safety-critical enforcement (code) from diagnosis (optional Ollama monitor). No recursive retry loops. Deterministic policy engine first, LLM advice second.

### Phase 6a: Event Schema & Collection (NEXT AFTER 5b)

- [ ] Design event schema (JSON + documentation)
  - File: `benchmarks/monitoring/event_schema.json`
  - Include: `model_digest`, `task_class`, `accepted`, `fallback_used`, structured output validation results
  - Reference: consultant guidance (email thread, 2026-09-24)
  
- [ ] Implement event emission in dispatcher
  - Hook: emit structured event after every Ollama/local agent attempt
  - Storage: SQLite or JSONL to `benchmarks/monitoring/events.db`
  - Fields: `attempt_id`, `workitem_id`, `timestamp`, metrics tuple
  - **Do not trust agent self-reports; emit from wrapper**

- [ ] Wire deterministic circuit breakers (no LLM judgment)
  - Config file: `config/ollama_monitoring.yaml`
  - Automatic protective actions (hard thresholds):
    - `schema_failure_rate ≥ 10%` → quarantine this (model, task_class) pair
    - `deterministic_test_failure_rate ≥ 20%` → divert new tasks to API
    - `fallback_rate ≥ 30%` → trigger alert + human review required
    - `p95_end_to_end_latency ≥ 60s` → pause local dispatch
  - Code: Add checks to dispatcher before sending to local model
  - **Max 1 retry attempt; then fallback to API (no retry loops)**

### Phase 6b: Metrics Aggregation (FOLLOWING 6a)

- [ ] Metrics calculation layer
  - Compute rolling rates per `(model_digest, task_class, route, prompt_version)`
  - Windows: last 1h, last 24h, baseline 14d
  - File: `benchmarks/monitoring/metrics.py`
  - Output: compact JSON report (counts, rates, sampled failures)

- [ ] Integration with dispatcher
  - Emit metrics every 15–30 minutes OR on circuit-breaker trip
  - Store alongside events for historical analysis
  - Track: `cost_per_accepted_task`, `false_pass_rate`, `escalation_rate`

### Phase 6c: Monitor Agent (PHASE 2, DEFERRED)

**Not in Phase 1.** Phase 2 only, after we have real data:

- [ ] Ollama monitor agent (diagnostic only)
  - JSON-schema-constrained output (safe vocabulary)
  - Permitted actions: [continue, increase_sampling, route_to_api, quarantine, rollback, request_human_review]
  - Input: aggregated metrics + 3–5 sampled failures (no raw conversations)
  - Output: severity, status, primary_hypothesis, confidence, recommended_action
  - **Requires human review to implement any recommendation**

- [ ] Weekly accuracy review
  - Did monitor diagnosis match eventual root cause?
  - Refine thresholds based on observed patterns

### Success Metrics (Oct 15 Checkpoint)

- [ ] At least 100 tasks routed to local models with complete telemetry
- [ ] Circuit breaker thresholds not triggering false positives
- [ ] Cost per accepted task tracked (including retries + fallbacks)
- [ ] False-pass rate ≤ configured limit (silent errors caught)
- [ ] Deterministic evaluator results separate from semantic validation

### Critical Design Rules (Non-Negotiable)

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
