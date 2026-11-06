# P-system semantics, v1

Status: draft for review. The conformance cases in section 8 are the acceptance tests. The engine is written after
this spec is agreed, and it must pass those cases before anything else.

## 1. Scope

v1 covers the basic transition model with symbol objects:

- a rooted tree of labelled membranes (regions); the root is the skin,
- a multiset of symbols in each region,
- catalytic and non-catalytic rules in each region,
- target indications `here`, `in <child>` and `out`,
- maximal parallelism within each region, and synchronous steps,
- halting, and output read as a count or as a yes/no object.

Out of v1 (see the backlog in `membrane/TODO.md`): membrane division, dissolution, creation, polarization, electrical
charges, symport and antiport, tissue and spiking variants, rule priorities, and any rule form not listed in
section 3.

## 2. Configurations

A **configuration** assigns to each region `r` a multiset `w_r` over the alphabet `Γ`. Regions form a tree `T`: the
root is the skin `0`, and every other region has exactly one parent.

## 3. Rules

A **rule** in region `r` has the form

    c u → v

- `c` is a multiset over `Γ`, the **catalyst**. It may be empty, in which case the rule is non-catalytic.
- `u` is a non-empty multiset over `Γ`, the **input**.
- `v` is a multiset of **targeted symbols** `(a, t)` with `a ∈ Γ` and `t ∈ {here} ∪ {in j : j a child of r} ∪ {out}`.
  Writing `a` alone means `(a, here)`. A rule in the skin may not target `out`.

The catalyst is required but not consumed, and it is not written again on the right-hand side: `c a → b` consumes one
`a`, needs one `c`, and produces one `b`, so the `c` stays. The input is consumed. Both are checked against the region's
contents.

## 4. Applicability and steps

Let `C` be the configuration at the start of a step.

A **rule instance** of rule `r : c u → v` in region `ρ` is a copy of `r` chosen to fire. Let `I` be a multiset of
instances in region `ρ`, with `U(I)` the total input it consumes and `K(I)` the set of symbols that serve as catalysts
of at least one instance in `I`.

A **step** is a choice, for every region, of a multiset of rule instances of that region's rules such that:

1. **Consumption fits.** For every symbol `s`, the copies of `s` consumed in the region do not exceed the copies present
   at the start of the step: `U(I)(s) ≤ C_ρ(s)`.
2. **Catalysts survive.** For every symbol `s` in `K(I)`, at least one copy remains after the step:
   `C_ρ(s) − U(I)(s) ≥ 1`. So a catalyst may be read by one instance and consumed by another in the same step only when
   a copy is left over; a catalyst is never used up.
3. **Maximality.** For each region, no further rule instance of that region can be added to the step without breaking
   condition 1 or condition 2.

These conditions depend only on the starting configuration `C` and on the chosen instances, never on the order in
which the instances are listed.

All regions are chosen against the same starting configuration `C`, so the step is synchronous.

Applying a step:

- remove every consumed input copy from its region,
- for each instance, produce its targeted symbols: `here` into the same region, `out` into the parent, `in j` into
  child `j`,
- the produced symbols become available only at the next step.

If no region has any applicable rule instance, the configuration is **terminal**: the computation halts.

## 5. Nondeterminism and reproducibility

Where more than one step is possible, the engine chooses one. The choice is the only source of nondeterminism.

v1 choice procedure, which is deterministic given the seed:

1. Visit regions in a fixed order: a pre-order traversal of the tree, children in their declared order.
2. In each region, keep the rules in declaration order, and keep a working multiset `R` (the residual) starting at the
   region's contents, and a chosen multiset `I` starting empty.
3. Repeat until no rule can be added:
   a. A rule `r` is a **candidate** when one more instance of `r` keeps conditions 1 and 2 of section 4 true, with
      `R` in place of `C` and `I` plus that instance in place of the chosen step.
   b. If there are no candidates, stop. Otherwise build the candidate list in declaration order, one entry per rule
      (not per copy), and draw `index = rng.randrange(len(candidates))` from the run's generator
      (`random.Random(seed)`). Always draw, even when there is one candidate, so that the draws line up across runs.
   c. Add one instance of the chosen rule to `I`, and remove its input from `R`.
4. Apply `I` as the step.

The loop ends only when no rule can be added, so the result satisfies maximality. The choice is uniform over applicable
rules, not over every maximal multiset; that distribution is documented, not assumed. Only the seeded generator and
declaration order decide the result, never hash order, so the same seed gives the same trace on any machine and any
`PYTHONHASHSEED`.

## 6. Halting, output and status

A run has one of four statuses:

- `halted`: a terminal configuration was reached within `max_steps`,
- `timeout`: `max_steps` steps were taken and the configuration is not terminal,
- `yes` / `no`: halted, and the skin contains the recognizing object `yes` (respectively `no`) and not the other,
- `undefined`: halted, and the skin contains both, or neither, of `yes` and `no` (for a recognizing system only).

The **output** under `output: count` is the number of copies of the designated symbol in the output region (the skin
unless a region is named), for every halted status: `halted`, `yes`, `no` and `undefined` alike. Under
`output: recognize` the answer is the status itself, and the count is not reported. A `timeout` yields no answer in
either mode.

If `max_steps = 0`, a configuration that is already terminal is `halted` with 0 steps. Otherwise the run is `timeout`
with 0 steps.

## 7. Parameters (v1)

- `seed`: required. The only source of nondeterminism.
- `max_steps`: required. The bound on steps.
- `output`: `count` with a symbol and a region, or `recognize` with the `yes`/`no` symbols.
- `record_trace`: boolean. When true, every configuration is returned; when false, only the final one.

No parameter changes the semantics above. Diagnostics go to logging, never to stdout.

## 8. Conformance cases (acceptance tests)

Each case gives a system, the expected result, and how the expected result was derived. Derivations are by hand from
sections 3 to 6. Every case states the full expected trace where the trace is unique.

**C1. Maximal parallel rewriting in one region.** Skin `0` holds `a^3`. Rules: `a → b b`.
Step 1: three instances of `a → b b` are applicable and all are applied (maximality). Result `b^6`.
Halts after 1 step. Output count of `b` = 6.

**C2. Two rules competing for the same input.** Skin holds `a^2`. Rules: `a → b`, `a → c`.
A step consumes both copies of `a`, one per instance. The maximal steps are `{b, b}`, `{c, c}` and `{b, c}`.
After one step the contents are one of `b^2`, `c^2`, `b c`. Halts. The test asserts that the result is one of the
three, that it contains no `a`, and that the total object count is 2. Every seed must give one of the three.

**C3. Catalyst is read, not consumed.** Skin holds `c a^3`. Rules: `c a → b`.
Each step applies three instances, sharing the one `c`. Result `c b^3`. Halts after 1 step.

**C4. Missing catalyst blocks the rule.** Skin holds `a^3`. Rules: `c a → b`.
No rule instance is applicable. Halts with 0 steps. Contents `a^3`.

**C5. Synchrony: produced objects wait one step.** Skin holds `a`. Rules: `a → b`, `b → c`.
Step 1: `a → b`. The new `b` cannot be consumed in the same step. Contents `b` after step 1.
Step 2: `b → c`. Contents `c`. Halts after 2 steps. The trace must have exactly these two transitions.

**C6. Target `out`.** Skin `0` is empty. Child `s` holds `a^2`. Rules in `s`: `a → (b, out)`.
Step 1: two instances, each sending `b` to the skin. Result: skin `b^2`, `s` empty. Halts after 1 step.

**C7. Target `in j`.** Skin holds `a^2`, child `s` is empty. Rules in the skin: `a → (b, in s)`.
Step 1: two instances, each sending `b` into `s`. Result: skin empty, `s` holds `b^2`. Halts after 1 step.

**C8. Regions run in the same step.** Skin holds `a`, child `s` holds `a`. Rules in both regions: `a → b`, the same
rule in each. Step 1: both regions apply their rule. Result: skin `b`, `s` holds `b`. Halts after 1 step.

**C9. Empty multiset halts immediately.** No objects anywhere; any rules. Halts with 0 steps.

**C10. Timeout.** Skin holds `a`. Rules: `a → a a`. With `max_steps = 5` the run stops with status `timeout`,
contents `a^(2^5)`, and no answer is reported.

**C11. Recognizing system.** Skin holds `a`. Rules: `a → yes`. Halts after 1 step with status `yes`.
A system with rules `a → no` on the same input gives `no`. A system with rules `a → yes yes no` gives `undefined`.

**C12. Determinism.** For the C2 system and the random systems used by the built-in examples, the same seed gives an
identical trace, including under different `PYTHONHASHSEED` values. Different seeds may give different traces.

**C13. Invalid targets are rejected.** A rule in the skin with target `out`, or `in j` with `j` not a child of the
skin, is an error at construction time, not a runtime event.

## 9. Invariants checked on every run

- Per step: no region's contents become negative. Every consumed input was present before the step.
- At halting: no rule instance is applicable in any region (terminal).
- Per step, every catalyst symbol keeps at least one copy (section 4, condition 2).
- Within a seed, the trace is a function of the system alone.

## 10. Open questions for review

1. Catalytic rules are in v1, in the form `c u → v`. Section 4, condition 2 is the rule for a catalyst that is also
   consumed in the same step; it was settled by an independent check of the spec.
2. Maximality is per region on the residual contents, as above. Confirm this matches the reference you want to
   cite.
3. Output by count, or only by yes/no object for v1? Both are specified here.
