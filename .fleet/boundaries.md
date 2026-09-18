# Repository Boundaries: membrane

**Use this file as your executable charter.**

---

## Domain & Bounded Context

Membrane is the coordination and workspace management platform. Owns task tracking, project organization, team collaboration features, and workflow automation. Serves as the central hub for organizing fleet activities.

---

## Explicitly NOT (Anti-Goals)

- [ ] **User applications** — That's flashcards, cv, income-ops
- [ ] **Fleet orchestration** — That's fleet-ops
- [ ] **Code refactoring** — That's rope-mcp
- [ ] **Authentication** — Delegates to fleet-ops (future)

---

## Upstream & Downstream Topology

### Provides

| Component | Type | Consumers | Contract |
|---|---|---|---|
| REST API | HTTP | Web/mobile clients | Tasks, projects, teams |
| Database | PostgreSQL | Internal | Tasks, workflows, collaboration |
| CLI | FleetCommand | fleet-ops | status, sync, validate |

### Depends On

| Dependency | Version | Why | Used By |
|---|---|---|---|
| fleet-base | ^0.1.0 | CLI foundation | CLI commands |

---

## Ownership

- @malexiuk

**Approval Required For:**
- ✅ API contract changes
- ✅ Workflow automation changes
- ✅ Collaboration feature changes

---

## Recent Changes

| Date | Change | ADR | Justification |
|---|---|---|---|
| 2026-09-17 | Established membrane as coordination domain | [ADR-404](./docs/adr/404-coordination-domain.md) | Fleet governance of workspace platform |
