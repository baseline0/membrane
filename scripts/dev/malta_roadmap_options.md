# Malta Roadmap: Decision List

Based on scan of related projects + P-Systems research context, here are concrete paths forward.

## Scan Findings (from `scan_findings.md`)

✓ **Consistent patterns across active projects:**
- Python 3.13+ requirement
- Typer for CLI (malta already uses this ✓)
- uv package manager (malta already uses this ✓)
- justfile as task runner (malta already has this ✓)
- pre-commit hooks (malta has basic setup ✓)

✓ **Dependency themes in learn-ollama (most complete project):**
- Data: polars, duckdb, pyarrow (analytics/data processing)
- AI: ollama, pydantic, numpy (LLM/ML integration)
- Code: libcst, rich (code manipulation, TUI output)
- Network: httpx, fastapi, mcp (API/service communication)

---

## P-Systems Research Niches (user input)

1. **Fault Diagnosis** (FRPS for power grids, machinery) — hierarchical membranes as rule trees
2. **Swarm Robotics** (P-colony agents) — distributed control, formation
3. **Decision Tree Optimization** (global membrane algorithms) — tree evolution via crossover/mutation
4. **SN P Neural Systems** — time-series, pattern recognition

---

## Concrete Demo/App Options

### Option A: Fault Diagnosis (Closest to Current Malta)
**Rationale:** Hierarchical membranes naturally map to diagnostic rule trees.

**Stack:**
- Malta core (already handles rule firing, membrane hierarchy)
- Input: sensor readings (CSV or simple JSON)
- Output: fault hypothesis + confidence score
- Libs: `rich` (pretty TUI output), `pandas` (data ingestion)
- Example: Simple power distribution fault detection

**Effort:** Low–Medium (leverage existing sim structure)

### Option B: Decision Tree Optimizer
**Rationale:** Research niche with active papers; clear problem statement.

**Stack:**
- Malta core (membrane rules = tree transformation rules)
- `graphviz` (visualize evolved trees)
- `sklearn` (benchmark trees)
- Mechanism: Subtrees as membrane objects, crossover via membrane rules
- Example: Evolve decision tree on UCI ML dataset

**Effort:** Medium (requires tree encoding + evolutionary operators)

### Option C: Swarm Robotics Simulator
**Rationale:** P-colony as distributed control; modern robotics problem.

**Stack:**
- Malta core (agents as membranes, environment as parent)
- `gymnasium` or `sim2real` (robot sim interface)
- `numpy` (physics math)
- Example: Formation control, collision avoidance for robot swarm

**Effort:** Medium–High (physics + robotics knowledge needed)

### Option D: SN P Neural Network
**Rationale:** Biologically inspired, emerging research area.

**Stack:**
- Malta core (spike rules, synapse simulation)
- `numpy` (matrix ops for synapse weights)
- `matplotlib` (visualize spike rasters)
- Example: Time-series forecasting, edge detection on image

**Effort:** Medium (neural network background helpful)

---

## Decision Framework

**Pick ONE first demo based on:**

| Criteria | A (Diagnosis) | B (Tree Opt) | C (Swarm) | D (SN P) |
|----------|---------------|-------------|-----------|----------|
| Effort | ✓ Low | ✓ Medium | ✗ High | ✓ Medium |
| Leverages current malta | ✓ Strong | ✓ Strong | ~ Partial | ✓ Moderate |
| Research novelty | ~ Active | ✓✓ Active | ✓ Active | ✓ Emerging |
| Clarity of problem | ✓✓ Clear | ✓✓ Clear | ✓ Clear | ~ Less clear |
| Library synergy | ~ | ✓ (sklearn) | ✓ (gymnasium) | ✓ (numpy) |

---

## Recommendation: Start with A or B

**Option A (Fault Diagnosis)** if you want quick win + clear story.
**Option B (Decision Tree Opt)** if you want research publication potential + deeper malta showcase.

Either way, the scanner script in `scripts/dev/scan_related_projects.py` can be re-run to update findings.

---

## Checklist for Next Phase

- [ ] Pick one demo option (A/B/C/D)
- [ ] Sketch high-level architecture (membrane structure = ?)
- [ ] List required new dependencies
- [ ] Create `demos/[chosen]/` stub with README
- [ ] Implement MVP (few rules, small dataset)
- [ ] Test sim runs end-to-end
- [ ] Compare output to baseline (if applicable)
