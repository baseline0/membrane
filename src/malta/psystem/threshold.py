"""Tier 2 check: decide whether the count of an input symbol meets a threshold, on the v1 engine.

The system is one rule in the skin, a^k -> y, with the input a^n in the skin. The decision is read from the count of y
at halting: yes iff n >= k. See docs/psystems/TIER2-counting-threshold.md, which also explains why the recognizing
output cannot express the no-side in v1.
"""

from __future__ import annotations

from collections import Counter

from malta.psystem.engine import Result, run
from malta.psystem.model import Region, Rule, System, SystemError

YES = "y"


def counting_threshold(symbol: str, k: int, n: int) -> System:
    """The system for input symbol^n and threshold k. Raises SystemError on a bad encoding, at construction."""
    if not isinstance(symbol, str) or not symbol:
        raise SystemError(f"input symbol must be a non-empty string, got {symbol!r}")
    if symbol == YES:
        raise SystemError(f"input symbol must differ from the output symbol {YES!r}")
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise SystemError(f"threshold must be an integer >= 1, got {k!r}")
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise SystemError(f"input count must be an integer >= 0, got {n!r}")
    rule = Rule(input=Counter({symbol: k}), output=[(YES, "here")])
    return System(Region("0", Counter({symbol: n}), [rule]))


def decide(symbol: str, k: int, n: int, seed: int = 0) -> tuple[bool, Result]:
    """Run the threshold system to halting. Returns (yes, result); yes means n >= k."""
    system = counting_threshold(symbol, k, n)
    result = run(system, seed=seed, max_steps=max(1, n), output={"mode": "count", "symbol": YES})
    return bool(result.answer and result.answer > 0), result
