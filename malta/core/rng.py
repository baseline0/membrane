"""Seeded randomness for the P-system path.

Every generator on this path takes a random.Random. None uses the global random module, so a run is reproducible
from its seed, and the seed is recorded with the run.
"""

from __future__ import annotations

import random

DEFAULT_SEED = 0

_shared = random.Random(DEFAULT_SEED)


def make_rng(seed: int | None = None) -> random.Random:
    """A fresh generator for one run. seed=None means DEFAULT_SEED, so an unseeded run is still reproducible."""
    return random.Random(DEFAULT_SEED if seed is None else seed)


def shared_rng() -> random.Random:
    """One process-wide generator, seeded once, used only for names so that names are distinct within a run."""
    return _shared
