"""Enhanced quantum-inspired evolutionary algorithm with adaptive capabilities.

Extends quantum_inspired.py with:
- Multi-bit encoding for fine-grained search
- Adaptive mutation rates based on convergence
- Population diversity monitoring
- Escape strategies from plateaus
"""

import math
import random
from dataclasses import dataclass

from malta.adaptive_evolution import (
    AdaptiveEvolutionController,
    DiversityMetrics,
    MutationOperator,
)
from malta.encoding import MultibitEncoder, ProgressiveEncoding
from malta.quantum_gates import MeasurementGate, QuantumState


@dataclass
class EnhancedCandidate:
    """Solution candidate with metadata."""

    values: list[float]
    fitness: float
    basis_state: str = ""  # Binary representation

    def copy(self):
        """Create independent copy."""
        return EnhancedCandidate(
            values=self.values.copy(),
            fitness=self.fitness,
            basis_state=self.basis_state,
        )


class EnhancedQuantumCompartment:
    """Membrane compartment with multi-bit encoding and mutation."""

    def __init__(self, compartment_id: int, encoder: MultibitEncoder):
        """Initialize compartment.

        Args:
            compartment_id: Unique identifier
            encoder: Multi-bit encoder for this compartment
        """
        self.compartment_id = compartment_id
        self.encoder = encoder
        self.quantum_state = QuantumState({})
        self.best_candidate = None

    def initialize_superposition(self) -> None:
        """Create equal superposition over all basis states."""
        n_states = self.encoder.get_basis_dimension()
        amplitude = 1.0 / math.sqrt(n_states)

        # Generate all basis states (for small n_bits this is feasible)
        # For large n_bits, sample a subset
        basis_states = {}
        if n_states <= 2**20:  # Up to 1M states
            for i in range(n_states):
                basis = format(i, f"0{self.encoder.total_bits}b")
                basis_states[basis] = amplitude
        else:
            # Sample for very large spaces
            for _ in range(min(2**16, n_states)):
                basis = self.encoder.random_basis_state()
                basis_states[basis] = amplitude

        self.quantum_state = QuantumState(state_vector=basis_states)

    def measure_and_decode(
        self,
        apply_mutation: bool = False,
        mutation_rate: float = 0.01,
    ) -> EnhancedCandidate:
        """Collapse superposition and optionally mutate.

        Args:
            apply_mutation: Whether to apply mutation operator
            mutation_rate: Mutation rate for bit-flip

        Returns:
            EnhancedCandidate with solution
        """
        if not self.quantum_state.state_vector:
            # Empty state; return default
            default_val = (self.encoder.bounds[0] + self.encoder.bounds[1]) / 2
            return EnhancedCandidate(
                values=[default_val] * self.encoder.n_dims,
                fitness=float("inf"),
                basis_state="",
            )

        # Measure
        gate = MeasurementGate()
        self.quantum_state = gate.apply_to_quantum_state(self.quantum_state)

        states = list(self.quantum_state.state_vector.keys())
        if not states:
            default_val = (self.encoder.bounds[0] + self.encoder.bounds[1]) / 2
            return EnhancedCandidate(
                values=[default_val] * self.encoder.n_dims,
                fitness=float("inf"),
                basis_state="",
            )

        basis_state = states[0]

        # Optional mutation
        if apply_mutation and random.random() < 0.5:  # 50% apply mutation
            basis_state = MutationOperator.bit_flip(basis_state, mutation_rate)

        # Decode to solution
        solution = self.encoder.basis_state_to_solution(basis_state)

        return EnhancedCandidate(
            values=solution,
            fitness=float("inf"),
            basis_state=basis_state,
        )


class EnhancedQuantumInspiredAlgorithm:
    """Enhanced quantum-inspired evolutionary algorithm.

    Features:
    - Multi-bit encoding for fine-grained search
    - Adaptive mutation rates
    - Diversity monitoring
    - Progressive encoding (optional)
    """

    def __init__(
        self,
        n_compartments: int = 5,
        n_dims: int = 10,
        bounds: tuple[float, float] = (-5.0, 5.0),
        max_generations: int = 1000,
        bits_per_dim: int = 8,
        use_progressive: bool = False,
    ):
        """Initialize enhanced algorithm.

        Args:
            n_compartments: Number of parallel compartments
            n_dims: Problem dimensionality
            bounds: Variable bounds
            max_generations: Maximum generations
            bits_per_dim: Bits per dimension (for encoding)
            use_progressive: Whether to increase encoding resolution over time
        """
        self.n_compartments = n_compartments
        self.n_dims = n_dims
        self.bounds = bounds
        self.max_generations = max_generations
        self.use_progressive = use_progressive

        # Encoding
        if use_progressive:
            self.progressive_encoder = ProgressiveEncoding(
                n_dims,
                min_bits_per_dim=2,
                max_bits_per_dim=bits_per_dim,
                bounds=bounds,
            )
            self.bits_per_dim = 2  # Start with minimum
        else:
            self.progressive_encoder = None
            self.bits_per_dim = bits_per_dim

        # Adaptation
        self.adaptation_controller = AdaptiveEvolutionController(max_generations)

        # Initialize compartments
        self.compartments = []
        self._reinit_compartments()

    def _reinit_compartments(self) -> None:
        """Initialize or reinitialize compartments with current encoding."""
        self.compartments = []
        encoder = MultibitEncoder(self.n_dims, self.bits_per_dim, self.bounds)
        for i in range(self.n_compartments):
            comp = EnhancedQuantumCompartment(i, encoder)
            comp.initialize_superposition()
            self.compartments.append(comp)

    def optimize(self, objective) -> EnhancedCandidate:
        """Run enhanced quantum-inspired optimization.

        Args:
            objective: Function to minimize

        Returns:
            Best candidate found
        """
        global_best = None
        prev_best_fitness = None

        for generation in range(self.max_generations):
            # Update encoding resolution if progressive
            if self.use_progressive:
                self.progressive_encoder.set_generation(generation, self.max_generations)
                self.bits_per_dim = self.progressive_encoder.current_bits
                # Reinit compartments with new encoding
                self._reinit_compartments()

            # Phase 1: Measure and evaluate
            all_candidates = []
            mutation_rate = self.adaptation_controller.get_mutation_rate()

            for compartment in self.compartments:
                candidate = compartment.measure_and_decode(
                    apply_mutation=True,
                    mutation_rate=mutation_rate,
                )
                candidate.fitness = objective(candidate.values)
                all_candidates.append(candidate)

            # Phase 2: Track best
            gen_best = min(all_candidates, key=lambda c: c.fitness)
            if global_best is None or gen_best.fitness < global_best.fitness:
                global_best = gen_best.copy()

            # Phase 3: Compute diversity
            basis_states = [c.basis_state for c in all_candidates if c.basis_state]
            if basis_states:
                diversity = DiversityMetrics.hamming_diversity(basis_states)
            else:
                diversity = 0.0

            # Phase 4: Update adaptation
            self.adaptation_controller.update(
                generation,
                global_best.fitness,
                prev_best_fitness=prev_best_fitness,
                population_diversity=diversity,
            )

            # Check if should restart population
            if self.adaptation_controller.should_restart_population():
                self._reinit_compartments()

            # Phase 5: Reinitialize compartments
            for compartment in self.compartments:
                compartment.initialize_superposition()
                compartment.best_candidate = gen_best.copy()

            prev_best_fitness = global_best.fitness

        return global_best
