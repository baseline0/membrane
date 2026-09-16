# Membrane Computing & Benchmarking (Phase 5+)

**Current Phase:** Phase 5 (Dashboard & Orchestration)

**Mission:** Build publication-quality benchmarking framework + dashboard for membrane/P-Systems research + commercial applications.

---

## Phase 5: Dashboard & Metrics (NOW)

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

```bash
just test-unit           # Fast unit tests
just bench-example       # 3 seeds, 5 functions, 10D (quick validation)
just bench-metrics       # Collect metrics from benchmarks_example.csv
```

See docs/BENCHMARK_METRICS_FORMAT.md for metrics schema and dashboard integration.
