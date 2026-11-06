"""The structures a v1 P system is built from. Validation happens at construction, not during a run."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

HERE = "here"
OUT = "out"
# a target for a child membrane is ("in", child_name)
Target = str | tuple


class SystemError(ValueError):
    """A system that breaks the v1 rules. Raised at construction time."""


@dataclass
class Rule:
    """c u -> v. `catalyst` is required but not consumed; `input` is consumed; `output` is a list of (symbol, target)."""

    input: Counter
    output: list[tuple[str, Target]]
    catalyst: Counter = field(default_factory=Counter)

    def __post_init__(self) -> None:
        self.input = Counter(self.input)
        self.catalyst = Counter(self.catalyst)
        if sum(self.input.values()) == 0:
            raise SystemError("a rule needs a non-empty input")
        for symbol, _target in self.output:
            if not isinstance(symbol, str) or not symbol:
                raise SystemError(f"output symbol must be a non-empty string, got {symbol!r}")


@dataclass
class Region:
    """A membrane: a name, its contents, its rules, and its child regions."""

    name: str
    contents: Counter = field(default_factory=Counter)
    rules: list[Rule] = field(default_factory=list)
    children: list[Region] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.contents = Counter(self.contents)


class System:
    """A rooted tree of regions. The root is the skin. Names are unique."""

    def __init__(self, skin: Region) -> None:
        self.skin = skin
        self.parent: dict[str, str | None] = {}
        self.regions: dict[str, Region] = {}
        self._index(skin, None)
        self._validate_targets()

    def _index(self, region: Region, parent: str | None) -> None:
        if region.name in self.regions:
            raise SystemError(f"duplicate region name {region.name!r}")
        self.regions[region.name] = region
        self.parent[region.name] = parent
        for child in region.children:
            self._index(child, region.name)

    def _validate_targets(self) -> None:
        for region in self.regions.values():
            children = {child.name for child in region.children}
            for rule in region.rules:
                for _symbol, target in rule.output:
                    if target == HERE:
                        continue
                    if target == OUT:
                        if self.parent[region.name] is None:
                            raise SystemError(f"region {region.name!r} is the skin and has no parent for 'out'")
                        continue
                    if isinstance(target, tuple) and len(target) == 2 and target[0] == "in":
                        if target[1] not in children:
                            raise SystemError(
                                f"'in {target[1]}' in region {region.name!r}: {target[1]!r} is not a child of it"
                            )
                        continue
                    raise SystemError(f"unknown target {target!r} in region {region.name!r}")

    def configuration(self) -> dict[str, dict[str, int]]:
        return {name: dict(region.contents) for name, region in self.regions.items()}
