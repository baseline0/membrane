"""Cyprus Membrane System Contracts.

## Specification Map

| Rule | Authority | Enforcement |
|------|-----------|------------|
| Membrane lifecycle (active/dissolved) | MembraneState enum | Type system + __post_init__ validation |
| Execution phases (stage1/stage2/halt) | ExecutionPhase enum | Type system + tests |
| Particle types (regular/osmose/dissolve) | ParticleKind enum | Type system |
| Maximal rule application | stage1_config dataclass | Field validation + unit tests |
| Non-deterministic ordering | stage1_config.non_deterministic bool | Unit tests verify shuffle behavior |
| Clock semantics (monolithic clock) | ExecutionModel dataclass | __post_init__ validation + tests |
| Termination condition | ExecutionModel.should_halt bool | Unit tests verify halting conditions |
| Membrane dissolution order | DissolutionParticleSpec dataclass | __post_init__ target validation + tests |
| Osmosis target resolution | OsmosisParticleSpec dataclass | __post_init__ target validation + tests |

Authority: src/cyprus/contracts.py, tests/unit/test_membrane_lifecycle.py
"""

from dataclasses import dataclass
from enum import Enum


class MembraneState(Enum):
    """Membrane lifecycle states.

    Cyprus membranes exist in one of two states during execution:

    - ACTIVE: The membrane is present and can execute rules. Reactions defined within
      the membrane apply to its contents. Walls are intact; particles may osmose through
      or the membrane may dissolve.

    - DISSOLVED: The membrane has been destroyed by a DissolveParticle. All rule definitions
      are lost, contents are moved to parent, and nested membranes are moved to parent.
      A dissolved membrane cannot transition back to ACTIVE.
    """

    ACTIVE = "active"
    DISSOLVED = "dissolved"


class ExecutionPhase(Enum):
    """Phases of the Cyprus execution model.

    Cyprus executes in a monolithic clock. Each tick passes through these phases:

    - STAGE1: Apply all reactions maximally and non-deterministically, obeying reaction
      priorities. Reactions with higher priority are applied before lower-priority ones,
      but the order within a priority level is non-deterministic (shuffled).

    - STAGE2: Apply side effects from Stage 1:
      - Process DissolveParticles: dissolve the target membrane or self
      - Process OsmoseParticles: move payload to target or parent membrane

    - HALT: No more reactions can be applied. The clock stops. Output is the final
      contents of all environments.
    """

    STAGE1 = "stage1"
    STAGE2 = "stage2"
    HALT = "halt"


class ParticleKind(Enum):
    """Kinds of particles in Cyprus.

    Particles are chemical symbols that react within membranes. Most are regular
    symbols consumed by reactions. Special particles trigger side effects:

    - REGULAR: Normal symbol; consumed/produced by reactions
    - OSMOSE: Carries a payload through membrane walls to a target or parent
    - DISSOLVE: Triggers membrane dissolution and payload release
    """

    REGULAR = "regular"
    OSMOSE = "osmose"
    DISSOLVE = "dissolve"


@dataclass(frozen=True)
class Stage1Config:
    """Configuration for Stage 1 (reaction application phase).

    Stage 1 applies all applicable reactions maximally and non-deterministically:
    - For each priority level (highest first): apply all applicable reactions
    - Reactions within the same priority are shuffled (non-deterministic order)
    - Continue applying until no reaction can be applied (maximal application)

    Attributes:
        max_iterations: Maximum number of reaction application cycles. If reached
            before reaching a fixed point, execution halts (prevents infinite loops).
        non_deterministic: If True, reactions at the same priority level are
            shuffled. If False, order is deterministic (for testing). Defaults to True.
        apply_maximally: If True, continue applying reactions until no more can apply
            (standard behavior). If False, apply each reaction once (non-standard,
            for research only).
    """

    max_iterations: int = 10000
    non_deterministic: bool = True
    apply_maximally: bool = True

    def __post_init__(self) -> None:
        if self.max_iterations < 1:
            raise ValueError(f"max_iterations must be >= 1, got {self.max_iterations}")


@dataclass(frozen=True)
class DissolutionParticleSpec:
    """Specification for a DissolveParticle.

    A DissolveParticle triggers membrane dissolution in Stage 2. It carries:
    - payload (optional): not used; kept for compatibility
    - target (optional): name of the membrane to dissolve. If None, self dissolves.

    When processed in Stage 2:
    1. If target is specified, look up membrane by name in the global table
    2. Call dissolve() on target (or self if no target)
    3. Contents move to parent; nested membranes move to parent; rules are lost
    4. Dissolved membrane is removed from global table

    Attributes:
        target: Name of membrane to dissolve. If None, membrane containing the
            particle dissolves itself.
        payload: Not used (kept for API compatibility). Should be None.

    Raises:
        ValueError: If target is specified but is an empty string.
    """

    target: str | None = None
    payload: str | None = None

    def __post_init__(self) -> None:
        if self.target is not None and self.target == "":
            raise ValueError("target must be None or a non-empty string")


@dataclass(frozen=True)
class OsmosisParticleSpec:
    """Specification for an OsmoseParticle.

    An OsmoseParticle carries a payload through a membrane wall to a target in
    Stage 2. It allows particles to traverse membrane boundaries.

    When processed in Stage 2:
    1. Extract payload from OsmoseParticle
    2. If target is specified, look up membrane by name and append payload
    3. If target is None and parent exists, append payload to parent
    4. If target is None and no parent (i.e., this is an environment), do nothing
       (particles cannot osmose through environment boundaries)

    Attributes:
        target: Name of the target membrane. If None, osmose to parent or
            environment boundary.
        payload: The symbol/particle to be osmosed. Must be non-empty.

    Raises:
        ValueError: If payload is None or empty.
    """

    target: str | None = None
    payload: str | None = None

    def __post_init__(self) -> None:
        if self.payload is None or self.payload == "":
            raise ValueError("payload must be a non-empty string")
        if self.target is not None and self.target == "":
            raise ValueError("target must be None or a non-empty string")


@dataclass(frozen=True)
class ExecutionModel:
    """Specification for the Cyprus execution model.

    Cyprus is governed by a single monolithic clock that ticks in lockstep across
    all environments. Each tick:
    1. Stage 1: Apply reactions maximally, non-deterministically, respecting priorities
    2. Stage 2: Process side effects (dissolution, osmosis)
    3. Check halt condition: if no reactions applied, halt; else loop

    The clock stops when no reaction application can occur in Stage 1.
    Output is the final contents of all environments.

    Attributes:
        stage1_config: Configuration for Stage 1 reaction application.
        current_phase: Current execution phase (for state machine tracking).
        should_halt: True if no reaction was applied in the last Stage 1,
            indicating termination.
        rule_applied_in_stage1: True if at least one rule was applied in
            the current Stage 1 phase.
    """

    stage1_config: Stage1Config
    current_phase: ExecutionPhase = ExecutionPhase.STAGE1
    should_halt: bool = False
    rule_applied_in_stage1: bool = False

    def __post_init__(self) -> None:
        if self.current_phase == ExecutionPhase.HALT and not self.should_halt:
            raise ValueError("current_phase cannot be HALT unless should_halt is True")
        if self.current_phase in (ExecutionPhase.STAGE1, ExecutionPhase.STAGE2) and self.should_halt:
            raise ValueError(f"should_halt cannot be True while in {self.current_phase.value}")

    @classmethod
    def default(cls) -> "ExecutionModel":
        """Create a default ExecutionModel with standard settings."""
        return cls(stage1_config=Stage1Config())
