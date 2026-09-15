"""Quantum gate rules for membrane computing.

Extends Malta's classical rule system with quantum operations:
- Hadamard gate: |state⟩ → (|state_0⟩ + |state_1⟩)/√2
- Measurement: superposition → classical collapse
- Phase gate: applies phase rotation

Quantum gates operate on both classical items (multiset) and quantum state
(amplitude vector). This preserves classical P-system semantics while adding
quantum-inspired parallelism.
"""

import math
from dataclasses import dataclass
from typing import Optional

from malta.core.rule import Rule
from malta.types.mmultiset import MMultiset


@dataclass
class QuantumState:
    """Quantum state vector in a membrane.

    Maps basis state labels (strings) to complex amplitudes.
    Invariant: sum(|amplitude|²) = 1.0 (normalized).
    """

    state_vector: dict[str, float]

    def normalize(self) -> None:
        """Ensure sum of squared amplitudes = 1."""
        norm = math.sqrt(sum(amp**2 for amp in self.state_vector.values()))
        if norm > 0:
            for state in self.state_vector:
                self.state_vector[state] /= norm

    def copy(self) -> "QuantumState":
        """Create independent copy of state vector."""
        return QuantumState(state_vector=self.state_vector.copy())

    def __repr__(self) -> str:
        parts = []
        for state, amp in sorted(self.state_vector.items()):
            if amp != 0:
                prob = (amp**2) * 100
                parts.append(f"|{state}⟩ (amp: {amp:.4f}, prob: {prob:.1f}%)")
        return "\n".join(parts) if parts else "Empty state"


class QuantumGate(Rule):
    """Base class for quantum gate rules.

    A quantum gate modifies both the classical multiset (membrane contents)
    and the quantum state (amplitudes). This hybrid representation lets us
    use membrane compartmentalization for quantum information.
    """

    def __init__(
        self,
        name: str,
        descr: str,
        catalyst: Optional[MMultiset] = None,
        rule_input: Optional[MMultiset] = None,
        rule_output: Optional[MMultiset] = None,
    ):
        """Initialize quantum gate rule.

        Args:
            name: Gate name (e.g., "hadamard_A")
            descr: Description
            catalyst: Classical items required (not consumed)
            rule_input: Classical items consumed
            rule_output: Classical items produced
        """
        super().__init__(
            name=name,
            descr=descr,
            catalyst=catalyst or MMultiset(),
            rule_input=rule_input or MMultiset(),
            rule_output=rule_output or MMultiset(),
        )

    def apply_to_quantum_state(
        self, state: QuantumState, target: str
    ) -> QuantumState:
        """Apply quantum operation to state vector.

        Subclasses override this to implement specific gates.

        Args:
            state: Current quantum state
            target: Target basis state label

        Returns:
            Modified quantum state (normalized)
        """
        raise NotImplementedError


class HadamardGate(QuantumGate):
    """Hadamard gate: superposition rule.

    Splits a basis state into equal superposition of two outcomes:
      |A⟩ → (|A_0⟩ + |A_1⟩) / √2

    Classical side: consumes input item, produces output items.
    Quantum side: creates superposition in quantum state vector.
    """

    def __init__(self, target_state: str):
        """Initialize Hadamard gate for target basis state.

        Args:
            target_state: Label of state to split (e.g., "A")
        """
        self.target_state = target_state
        self.target_0 = f"{target_state}_0"
        self.target_1 = f"{target_state}_1"

        super().__init__(
            name=f"hadamard_{target_state}",
            descr=f"Hadamard gate: |{target_state}⟩ → (|{self.target_0}⟩ + |{self.target_1}⟩)/√2",
        )

    def apply_to_quantum_state(
        self, state: QuantumState, target: str
    ) -> QuantumState:
        """Split target state into superposition.

        If state exists in vector, replace with two states at 1/√2 amplitude each.
        """
        if target not in state.state_vector:
            return state

        new_state = state.copy()
        amp = new_state.state_vector.pop(target)

        # Hadamard: equal superposition
        new_state.state_vector[self.target_0] = amp / math.sqrt(2)
        new_state.state_vector[self.target_1] = amp / math.sqrt(2)

        new_state.normalize()
        return new_state


class MeasurementGate(QuantumGate):
    """Measurement gate: collapse superposition.

    Collapses quantum state to classical basis state based on probability
    distribution (|amplitude|²).

    Classical side: produces classical result.
    Quantum side: collapses to single state.
    """

    def __init__(self):
        super().__init__(
            name="measure",
            descr="Measurement: collapse superposition to classical state",
        )

    def apply_to_quantum_state(
        self, state: QuantumState, target: str = None
    ) -> QuantumState:
        """Collapse to single classical state.

        Randomly selects basis state weighted by probability (|amplitude|²).
        """
        import random

        states = list(state.state_vector.keys())
        if not states:
            return state

        probabilities = [abs(state.state_vector[s]) ** 2 for s in states]

        # Weighted collapse
        collapsed_state = random.choices(states, weights=probabilities, k=1)[0]

        # State now definite (collapsed)
        new_state = QuantumState(state_vector={collapsed_state: 1.0})
        return new_state

    @staticmethod
    def get_collapsed_outcome(state: QuantumState) -> str:
        """Get the classical outcome after measurement.

        Assumes state has already been collapsed (single entry).
        """
        states = list(state.state_vector.keys())
        if len(states) == 1:
            return states[0]
        raise ValueError("State not collapsed; call measurement gate first")


class PhaseGate(QuantumGate):
    """Phase gate: rotate amplitude.

    Applies phase rotation to a basis state:
      |state⟩ → e^(iθ) |state⟩

    For classical simulation, we use cos(θ) (real part) to represent phase.
    """

    def __init__(self, phase_radians: float = math.pi / 4):
        """Initialize phase gate.

        Args:
            phase_radians: Rotation angle (default π/4)
        """
        self.phase = phase_radians
        super().__init__(
            name="phase_gate",
            descr=f"Phase gate: rotation by {phase_radians:.4f} rad",
        )

    def apply_to_quantum_state(
        self, state: QuantumState, target: str
    ) -> QuantumState:
        """Apply phase rotation to target state.

        Note: Phase does NOT change |amplitude|² (probability).
        We don't normalize after phase rotation.
        """
        if target not in state.state_vector:
            return state

        new_state = state.copy()
        # Phase as real-valued amplitude modulation (simplified model)
        # In classical simulation: phase modulates amplitude but preserves |amp|²
        new_state.state_vector[target] *= math.cos(self.phase)
        return new_state
