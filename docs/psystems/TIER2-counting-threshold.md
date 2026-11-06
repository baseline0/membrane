# Tier 2 check: counting-threshold decision, v1

Status: draft for review. Builds on `SPEC-v1.md`; no engine semantics change. The engine is `src/malta/psystem/engine.py`,
the constructor is `src/malta/psystem/threshold.py`, the tests are `tests/unit/test_psystem_tier2_threshold.py`.

## 1. Problem

Decide whether the count of an input symbol meets a threshold: is `n >= k`, where `n` is the number of copies of the
input symbol `a` and `k >= 1` is the threshold.

## 2. Encoding

- **Input.** The skin holds `a^n`, `n >= 0`, and nothing else. The input is the multiset, so no other object is needed.
- **Threshold.** `k` is fixed in the system: one system per `k`. It is the size of the rule's input, `a^k`.
- **Alphabet.** The input symbol is any non-empty string other than `y`. `y` is the output symbol.

## 3. System

A single rule in the skin:

    a^k → y        (non-catalytic, target `here`)

No other rules, no child membranes.

## 4. Output condition

Read under `output: count` with symbol `y` in the skin.

- **yes** iff the skin holds at least one `y` at halting, that is `n >= k`.
- **no** iff the skin holds no `y` at halting, that is `n < k`.

The decision is read from the count; the status is `halted` in both cases. The count itself is `floor(n / k)`.

## 5. Why a count and not the recognizing output

Under `output: recognize`, a yes/no object must decide. The natural pair `a^k → yes` and `a → no` is a race: when
`n >= k`, both rule instances are candidates in the same step, and the seeded choice can pick `a → no` first, which
leaves a residual `a` and gives the wrong status. Rules in v1 are monotone (a rule's applicability only depends on
present objects, and absence cannot be tested), so no "else" branch exists. With only `a^k → yes`, the `n < k` case
halts with neither object, which the spec reports as `undefined`, not `no`. So the recognizing output cannot express
the no-side of this family in v1. See the open question in section 7.

## 6. Expected results (derived by hand from SPEC-v1 sections 4 to 6)

| case | n | k | step 1 instances | residual `a` | `y` count | steps | yes/no |
|------|---|---|------------------|--------------|-----------|-------|--------|
| T1   | 3 | 2 | 1 (`a^2`, then `a^1` cannot fire) | 1 | 1 | 1 | yes |
| T2   | 4 | 2 | 2 | 0 | 2 | 1 | yes |
| T3   | 2 | 2 | 1 | 0 | 1 | 1 | yes |
| T4   | 1 | 2 | 0 (no instance applicable) | 1 | 0 | 0 | no |
| T5   | 0 | 1 | 0 | 0 | 0 | 0 | no |
| T6   | 5 | 1 | 5 | 0 | 5 | 1 | yes |

Derivation for T1: the only candidate rule instance needs two copies of `a`; the first instance consumes two of the
three, and the residual `a` cannot support a second. Maximality (section 4, condition 3) stops the step. The result is
terminal, so the run halts after one step. Count of `y` is 1, so the answer is yes.

Every case is seed-independent: there is one rule, so the choice procedure (section 5) draws from a one-entry
candidate list each time and the result is the same for any seed.

## 7. Open questions

1. **Recognizing output for the no-side.** Not expressible in v1 without a priority or a negation test. Under
   `output: recognize` the system above gives `yes` for `n >= k` and `undefined` for `n < k`. Either the decision is
   read from the count (as specified here), or the spec gains a priority rule form in v2.
2. **Other Tier 2 problems.** SAT and Subset Sum are deferred to the later division variant and are not implemented.
