# Formula-Driven Presentation: Friction & Feedback Log

**Purpose:** Track real-world feedback and friction points from using formula-driven slides in conference talks and collaborations.

**How to contribute:** Add a new entry with today's date, your name, and what you observed.

---

## Feedback Template

```markdown
### [DATE] - [NAME] - [CONTEXT]

**What went smoothly:**
- [List things that worked well]

**What was confusing or broken:**
- [List friction points]
  - Specific error or issue
  - How it affected workflow

**Formula index usefulness:**
- Did it help you verify correctness? (Yes/No)
- [Comment]

**Assumptions & rendering:**
- Any formulas render differently than expected? (Yes/No)
- [Details]

**CI/Workflow:**
- Did `just present` work reliably? (Yes/No)
- Any flakiness? [Details]

**Symbol aliasing:**
- Were mapping dicts easy to maintain?
- Did collaborators understand code-name → display-name?

**Overall:**
- Would you use this again? (Yes/No/Maybe)
- [Why]
```

---

## Entries

### 2026-09-19 - Mark Alexiuk - Phase 1 Completion

**What went smoothly:**
- ✅ Phase 1 hardening complete (SymPy pinning, LaTeX hashing, commit audit trail)
- ✅ Formula validation with actionable error messages
- ✅ `just present` one-command build pipeline
- ✅ Stress tests pass (missing formulas, unused formulas, strict mode)

**What was confusing or broken:**
- None yet (Phase 1 is foundation only; Phase 2 will be conference real-world test)

**Formula index usefulness:**
- Not yet tested with reviewers (Phase 2 objective)

**Assumptions & rendering:**
- All symbols have assumptions recorded (membrane_hierarchy, multiset_cardinality, etc.)
- Deterministic rendering via locked SymPy options

**CI/Workflow:**
- GitHub Actions template created with strict mode
- Pre-commit hook implemented
- Ready for Phase 2 testing

**Symbol aliasing:**
- Not yet used in formulas (designed but not needed for P-Systems example)
- Will test in Phase 2 if more complex formulas are added

**Overall:**
- Foundation is production-grade; ready for Phase 2 conference talk
- Next: collect real feedback from collaborators and audience

---

## Analysis (Themes & Priorities)

*To be updated as entries accumulate.*

### Emerging Themes
- [None yet - add as friction points accumulate]

### Prioritized Fixes
*By frequency and severity*

1. [None yet]
2. [None yet]

---

## Phase 3 Decision Data

**Metrics for PyPI publication:**
- [ ] Used for 2+ conference presentations
- [ ] 3+ unsolicited requests from other researchers
- [ ] No critical workflow friction points
- [ ] Committed to long-term maintenance

**Evidence collected:**
- [To be filled in after Phase 2]
