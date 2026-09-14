# Related Projects Scan

Findings from scanning sibling projects for best practices, libraries, and patterns.

## learn-ollama

**Path:** `learn-ollama`

**Python Version:** >=3.13

**CLI Framework:** typer

**Key Dependencies:**
- duckdb>=1.5.5
- fastapi>=0.141.1
- httpx2>=2.12.0
- libcst>=1.9.0
- mcp>=1.0.0,<2
- numpy>=2.5.3
- ollama>=0.6.2
- polars>=1.44.2
- pyarrow>=25.0.1
- pydantic-settings>=2.15.0
- ... and 7 more

**Patterns Observed:**
- justfile (task runner)
- pre-commit hooks
- uv package manager

---

## etf-pulse

**Path:** `etf-pulse`

**Python Version:** >=3.10

**CLI Framework:** typer

**Key Dependencies:**
- arxiv
- rich
- typer

**Patterns Observed:**
- justfile (task runner)
- uv package manager

---

## task-tracker

**Path:** `task-tracker`

(No pyproject.toml found)

---

## accidentallyadjacent

**Path:** `accidentallyadjacent`

(No pyproject.toml found)

---

## Summary & Decision Points

Use this scan to identify:
1. **Proven patterns:** What works in active projects?
2. **Library ecosystem:** Which libraries are used consistently?
3. **Architecture:** How are CLI/testing/deployment structured?
4. **Tooling:** Are there gaps we should fill in malta?

### Next Steps
- [ ] Review CLI framework choice (Typer vs alternatives)
- [ ] Check testing best practices across projects
- [ ] Identify dependency patterns for demos/apps
- [ ] Consider pre-commit/CI/CD setup for malta
