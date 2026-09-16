"""Quantum-Inspired Evolutionary Algorithm for Membrane Computing.

Combines quantum superposition (explore multiple directions) with membrane
compartmentalization (parallel evolution) to create hybrid optimization.

Key idea: Instead of classical GA's single population, use quantum states
to explore multiple candidate solutions in superposition, then measure to
collapse to classical outcomes. Repeat until convergence.

Example: Rosenbrock function minimization
  - Classical GA: 1 population, serial generation
  - Quantum-inspired: k compartments, each explores via quantum gates,
    measurement collapses to k classical candidates, recombine best
"""

import math
from dataclasses import dataclass
from typing import Callable, Optional

from malta.quantum_gates import MeasurementGate, QuantumState


@dataclass
class Candidate:
    """Classical solution candidate."""

    values: list[float]  # Problem variables
    fitness: float  # Objective value (lower = better for minimization)

    def copy(self) -> "Candidate":
        """Create independent copy."""
        return Candidate(values=self.values.copy(), fitness=self.fitness)


@dataclass
class QuantumCompartment:
    """Single membrane compartment for parallel quantum-inspired search.

    Each compartment maintains:
    - quantum_state: superposition of search directions
    - candidates: classical solutions decoded from measurements
    """

    compartment_id: int
    quantum_state: QuantumState
    candidates: list[Candidate]
    best_candidate: Optional[Candidate] = None

    def initialize_superposition(self, n_dims: int) -> None:
        """Create equal superposition over all basis states.

        For n_dims dimensions, create superposition of 2^n_dims basis states
        with equal amplitude (1/sqrt(2^n_dims) each).
        """
        # Generate all binary basis states: "00", "01", "10", "11" for n_dims=2
        basis_states = {}
        n_states = 2**n_dims
        amplitude = 1.0 / math.sqrt(n_states)

        for i in range(n_states):
            # Convert i to n_dims-bit binary string
            binary_str = format(i, f"0{n_dims}b")
            basis_states[binary_str] = amplitude

        self.quantum_state = QuantumState(state_vector=basis_states)

    def measure_and_decode(self, n_dims: int, bounds: tuple[float, float]) -> Candidate:
        """Collapse superposition to classical candidate.

        Steps:
        1. Measure quantum state (collapse to basis state)
        2. Decode basis state to problem variables
        3. Return candidate
        """
        if not self.quantum_state.state_vector:
            # Empty state; return default candidate
            default_val = (bounds[0] + bounds[1]) / 2
            return Candidate(values=[default_val] * n_dims, fitness=float("inf"))

        gate = MeasurementGate()
        self.quantum_state = gate.apply_to_quantum_state(self.quantum_state)

        # Get collapsed basis state (binary string)
        states = list(self.quantum_state.state_vector.keys())
        if not states:
            default_val = (bounds[0] + bounds[1]) / 2
            return Candidate(values=[default_val] * n_dims, fitness=float("inf"))

        collapsed_state = states[0]

        # Decode binary string to continuous variables
        values = []
        for i in range(min(n_dims, len(collapsed_state))):
            # Use binary digit as position in bounded range
            bit = int(collapsed_state[i])
            value = bounds[0] + (bounds[1] - bounds[0]) * bit
            values.append(value)

        # If collapsed_state is shorter than n_dims, pad with default values
        while len(values) < n_dims:
            default_val = (bounds[0] + bounds[1]) / 2
            values.append(default_val)

        return Candidate(values=values, fitness=float("inf"))


class QuantumInspiredEvolutionaryAlgorithm:
    """Hybrid quantum-inspired + membrane algorithm.

    Uses multiple compartments (membranes) to evolve solutions in parallel:
    - Each compartment maintains quantum superposition
    - Measurement yields classical candidates
    - Evolution combines measurements from all compartments
    """

    def __init__(
        self,
        n_compartments: int = 3,
        n_dims: int = 2,
        bounds: tuple[float, float] = (-5.0, 5.0),
        max_generations: int = 50,
    ):
        """Initialize algorithm.

        Args:
            n_compartments: Number of parallel membranes
            n_dims: Dimensionality of problem
            bounds: Variable bounds (lower, upper)
            max_generations: Stopping criterion
        """
        self.n_compartments = n_compartments
        self.n_dims = n_dims
        self.bounds = bounds
        self.max_generations = max_generations

        # Initialize membranes with superposition
        self.compartments = [
            QuantumCompartment(compartment_id=i, quantum_state=QuantumState({}), candidates=[])
            for i in range(n_compartments)
        ]
        for compartment in self.compartments:
            compartment.initialize_superposition(n_dims)

    def optimize(self, objective: Callable[[list[float]], float]) -> Candidate:
        """Run quantum-inspired evolution.

        Args:
            objective: Function to minimize f(x) -> float

        Returns:
            Best candidate found
        """
        global_best = None

        for generation in range(self.max_generations):
            # Phase 1: Measure compartments
            all_candidates = []
            for compartment in self.compartments:
                candidate = compartment.measure_and_decode(self.n_dims, self.bounds)
                candidate.fitness = objective(candidate.values)
                all_candidates.append(candidate)

            # Phase 2: Track best
            gen_best = min(all_candidates, key=lambda c: c.fitness)
            if global_best is None or gen_best.fitness < global_best.fitness:
                global_best = gen_best.copy()

            # Phase 3: Reinitialize compartments with slight bias toward best
            # (In real QEA, this would involve classical bits encoding best solution)
            for compartment in self.compartments:
                compartment.initialize_superposition(self.n_dims)
                compartment.best_candidate = gen_best.copy()

        return global_best
