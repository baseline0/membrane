"""Run a v1 P system. The semantics are in docs/psystems/SPEC-v1.md, sections 4 to 6; the choice is in section 5.

Every step chooses, per region, a maximal multiset of rule instances against the configuration at the start of the
step, then applies all of them at once. The only randomness is the seeded generator, used in the choice procedure.
"""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum

from malta.psystem.model import HERE, OUT, Region, Rule, System


class Status(Enum):
    HALTED = "halted"
    TIMEOUT = "timeout"
    YES = "yes"
    NO = "no"
    UNDEFINED = "undefined"


@dataclass
class Result:
    status: Status
    steps: int
    final: dict[str, dict[str, int]]
    answer: int | None = None  # the output count, for output="count" on a halted run; None otherwise
    trace: list[dict[str, dict[str, int]]] = field(default_factory=list)


def _fits(consumed: Counter, catalysts: set[str], start: Counter) -> bool:
    """Spec section 4: consumption fits the start contents, and every catalyst keeps at least one copy."""
    for symbol, count in consumed.items():
        if count > start.get(symbol, 0):
            return False
    return all(start.get(symbol, 0) - consumed.get(symbol, 0) >= 1 for symbol in catalysts)


def choose_step(region: Region, rng: random.Random) -> list[Rule]:
    """Spec section 5, steps 2 and 3: a maximal multiset of instances for one region, from its start contents."""
    start = Counter(region.contents)
    consumed: Counter = Counter()
    catalysts: set[str] = set()
    chosen: list[Rule] = []
    while True:
        candidates: list[Rule] = []
        for rule in region.rules:  # declaration order, one entry per rule
            trial = consumed + rule.input
            trial_catalysts = catalysts | set(rule.catalyst)
            if _fits(trial, trial_catalysts, start) and all(start.get(s, 0) >= n for s, n in rule.catalyst.items()):
                candidates.append(rule)
        if not candidates:
            return chosen
        pick = candidates[rng.randrange(len(candidates))]  # always draw, so the draws line up across runs
        consumed = consumed + pick.input
        catalysts |= set(pick.catalyst)
        chosen.append(pick)


def _snapshot(system: System) -> dict[str, dict[str, int]]:
    return system.configuration()


def _step(system: System, rng: random.Random) -> bool:
    """One synchronous step. Returns False when no region has an applicable instance (terminal)."""
    plans: dict[str, list[Rule]] = {}
    for name in _preorder(system):
        plans[name] = choose_step(system.regions[name], rng)
    if not any(plans.values()):
        return False

    # consumption first, against the start contents; then all productions at once
    for name, instances in plans.items():
        region = system.regions[name]
        for rule in instances:
            region.contents -= rule.input
    for name, instances in plans.items():
        region = system.regions[name]
        for rule in instances:
            for symbol, target in rule.output:
                if target == HERE:
                    region.contents[symbol] += 1
                elif target == OUT:
                    system.regions[system.parent[name]].contents[symbol] += 1
                else:
                    system.regions[target[1]].contents[symbol] += 1
    return True


def _preorder(system: System) -> list[str]:
    order: list[str] = []

    def walk(region: Region) -> None:
        order.append(region.name)
        for child in region.children:
            walk(child)

    walk(system.skin)
    return order


def _answer(system: System, status: Status, output: dict) -> int | None:
    if status is Status.TIMEOUT:
        return None
    if output["mode"] == "count":
        region = system.regions[output.get("region", system.skin.name)]
        return region.contents.get(output["symbol"], 0)
    return None


def _status(system: System, output: dict) -> Status:
    if output["mode"] != "recognize":
        return Status.HALTED
    skin = system.skin.contents
    yes, no = skin.get(output["yes"], 0) > 0, skin.get(output["no"], 0) > 0
    if yes and not no:
        return Status.YES
    if no and not yes:
        return Status.NO
    return Status.UNDEFINED


def run(
    system: System,
    seed: int,
    max_steps: int,
    output: dict | None = None,
    record_trace: bool = False,
) -> Result:
    """Run until halting or until max_steps steps have been taken.

    `output` is {"mode": "count", "symbol": s, "region": name?} or {"mode": "recognize", "yes": y, "no": n}.
    With no output given, the status is reported and no count is.
    """
    output = output or {"mode": "none"}
    if output["mode"] == "recognize" and output["yes"] == output["no"]:
        raise ValueError("yes and no must be different symbols")
    rng = random.Random(seed)
    trace = [_snapshot(system)] if record_trace else []
    steps = 0
    while True:
        terminal = not _any_applicable(system)
        if terminal:
            status = _status(system, output)
            break
        if steps >= max_steps:
            status = Status.TIMEOUT
            break
        _step(system, rng)
        steps += 1
        if record_trace:
            trace.append(_snapshot(system))
    return Result(
        status=status,
        steps=steps,
        final=_snapshot(system),
        answer=_answer(system, status, output),
        trace=trace,
    )


def _any_applicable(system: System) -> bool:
    return any(choose_step_candidates_exist(system.regions[name]) for name in _preorder(system))


def choose_step_candidates_exist(region: Region) -> bool:
    """True when at least one rule instance is applicable to the region's start contents (section 4)."""
    start = Counter(region.contents)
    return any(
        _fits(Counter(rule.input), set(rule.catalyst), start)
        and all(start.get(s, 0) >= n for s, n in rule.catalyst.items())
        for rule in region.rules
    )
