"""The built-in example systems, on the v1 engine.

example 1 and 2 are the hand-written systems of the old malta engine, with the same contents and rule: a catalysed
conversion c -> w in sub0, with b as the catalyst. examples 3 and 4 were random in the old engine. Here they are
seeded: the same seed gives the same system, and the same system gives the same run. Their results are not the old
runs' results, because the generator is a different one.
"""

from __future__ import annotations

import random
from collections import Counter

from malta.psystem.model import Region, Rule, System

ALPHABET_3 = ["a", "b", "c", "w"]
ALPHABET_4 = list("abcdefghijk")


def _catalysed_conversion(contents: dict[str, int]) -> System:
    rule = Rule(catalyst=Counter({"b": 1}), input=Counter({"c": 1}), output=[("w", "here")])
    sub0 = Region("sub0", Counter(contents), [rule])
    return System(Region("root", Counter(), [], [sub0]))


def example1() -> System:
    return _catalysed_conversion({"a": 1, "b": 4, "c": 2})


def example2() -> System:
    return _catalysed_conversion({"a": 1, "b": 2, "c": 3})


def _random_rules(alphabet: list[str], n: int, rng: random.Random) -> list[Rule]:
    """n random rules. With three or more letters, a rule has a catalyst, an input and an output, all distinct."""
    rules = []
    for _ in range(n):
        if len(alphabet) >= 3:
            catalyst, source, target = rng.sample(alphabet, 3)
            rules.append(Rule(catalyst=Counter({catalyst: 1}), input=Counter({source: 1}), output=[(target, "here")]))
        else:
            source, target = rng.sample(alphabet, 2)
            rules.append(Rule(input=Counter({source: 1}), output=[(target, "here")]))
    return rules


def random_system(alphabet: list[str], n_regions: int, n_rules: int, seed: int) -> System:
    """A random tree of n_regions membranes under the skin, with random contents and rules applied in every region."""
    rng = random.Random(seed)
    rules = _random_rules(alphabet, n_rules, rng)
    regions = [Region("0", Counter(), [])]
    for i in range(1, n_regions):
        parent = regions[rng.randrange(i)]
        contents = Counter({s: rng.randint(0, 3) for s in alphabet})
        region = Region(str(i), contents, [])
        parent.children.append(region)
        regions.append(region)
    for region in regions:
        region.rules = [Rule(input=r.input, output=list(r.output), catalyst=r.catalyst) for r in rules]
    return System(regions[0])


def example3(seed: int) -> System:
    return random_system(ALPHABET_3, n_regions=2, n_rules=10, seed=seed)


def example4(seed: int) -> System:
    return random_system(ALPHABET_4, n_regions=10, n_rules=10, seed=seed)


EXAMPLES = {1: example1, 2: example2, 3: example3, 4: example4}
