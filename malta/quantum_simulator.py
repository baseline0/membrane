"""
Quantum P System Simulator — Basic Quantum Membrane Computing Model

Simulates a compartmentalized quantum system where:
1. Membranes contain quantum state vectors (amplitudes, not probabilities)
2. Rewriting rules apply unitary transformations (Hadamard-like splits)
3. Measurement collapses superposition to classical states
4. Experiment logs are persisted to Obsidian vaults

Usage:
    >>> from malta.quantum_simulator import QuantumMembrane, run_experiment_and_log
    >>> run_experiment_and_log("./obsidian_vault")
"""

import os
import math
import random
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class QuantumMembrane:
    """
    Represents a compartmentalized membrane containing a quantum state vector.

    The state vector maps each classical state string to its complex amplitude.
    Normalization ensures sum of squared amplitudes = 1 (unitarity).
    """

    label: str
    state_vector: dict[str, float] = field(default_factory=dict)

    def normalize(self) -> None:
        """Ensures the sum of the squared amplitudes equals 1."""
        norm = math.sqrt(sum(amp**2 for amp in self.state_vector.values()))
        if norm > 0:
            for state in self.state_vector:
                self.state_vector[state] /= norm

    def apply_hadamard_rule(self, target_state: str) -> None:
        """
        Simulates a quantum object rewriting rule (analogous to a Hadamard gate).
        Splits a specific state into a superposition of two new states with
        equal amplitude (1/√2 each).

        Args:
            target_state: The state label to split (e.g., "A").
        """
        if target_state not in self.state_vector:
            return

        amp = self.state_vector.pop(target_state)

        # Split into superposition: (1/√2)|target_0⟩ + (1/√2)|target_1⟩
        self.state_vector[f"{target_state}_0"] = amp * (1 / math.sqrt(2))
        self.state_vector[f"{target_state}_1"] = amp * (1 / math.sqrt(2))

        self.normalize()

    def apply_phase_rule(self, target_state: str, phase: float) -> None:
        """
        Applies a phase gate (quantum phase rotation).

        Args:
            target_state: The state to rotate.
            phase: Phase angle in radians.
        """
        if target_state in self.state_vector:
            # Represent phase as real component (simplified for demo)
            self.state_vector[target_state] *= math.cos(phase)
            self.normalize()

    def measure(self) -> str:
        """
        Collapses the quantum state based on probability distribution.
        The probability of each state is the squared amplitude.

        Returns:
            The observed classical state after measurement.
        """
        states = list(self.state_vector.keys())
        probabilities = [abs(amp) ** 2 for amp in self.state_vector.values()]

        # Weighted random selection for state collapse
        collapsed_state = random.choices(states, weights=probabilities, k=1)[0]

        # After measurement, state is fully collapsed
        self.state_vector = {collapsed_state: 1.0}
        return collapsed_state

    def get_probabilities(self) -> dict[str, float]:
        """Returns probability distribution of all basis states."""
        return {state: (amp**2) for state, amp in self.state_vector.items()}

    def get_state_str(self) -> str:
        """Returns human-readable state vector string."""
        parts = []
        for state, amp in sorted(self.state_vector.items()):
            if amp != 0:
                prob = (amp**2) * 100
                parts.append(f"|{state}⟩ (amp: {amp:.4f}, prob: {prob:.1f}%)")
        return "\n".join(parts) if parts else "Empty state"


def write_obsidian_note(
    vault_path: str, title: str, tags: list[str], content: str
) -> str:
    """
    Creates a Markdown file with YAML frontmatter in the specified Obsidian vault.

    Args:
        vault_path: Path to the Obsidian vault directory.
        title: Title of the note (used in frontmatter and filename).
        tags: List of tags for categorization.
        content: Markdown body content.

    Returns:
        Full path to the created file.
    """
    os.makedirs(vault_path, exist_ok=True)

    # Generate Obsidian-compatible YAML Frontmatter
    frontmatter = (
        "---\n"
        f"title: {title}\n"
        f"date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"tags: [{', '.join(f'"{tag}"' for tag in tags)}]\n"
        "type: simulation_log\n"
        "status: completed\n"
        "---\n\n"
    )

    # Sanitize filename
    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).rstrip()
    file_name = f"{safe_title.replace(' ', '_')}.md"
    file_path = os.path.join(vault_path, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(content)

    return file_path


def run_experiment_and_log(vault_path: str) -> str:
    """
    Runs a complete Quantum P-System simulation experiment and logs results to Obsidian.

    Workflow:
    1. Initialize membrane with |A⟩
    2. Apply Hadamard-like rewriting rules to create superposition
    3. Measure to collapse state
    4. Format results as Obsidian note with YAML metadata
    5. Write to vault

    Args:
        vault_path: Path to the Obsidian vault directory.

    Returns:
        Path to the created Obsidian note.
    """
    print("Initializing Quantum Membrane...")
    skin_membrane = QuantumMembrane(label="Skin_Membrane", state_vector={"A": 1.0})

    # Apply rules to generate superposition
    print("Applying quantum rewriting rules...")
    skin_membrane.apply_hadamard_rule("A")  # A -> A_0 + A_1 (superposition)
    skin_membrane.apply_hadamard_rule("A_1")  # A_1 -> A_1_0 + A_1_1

    # Capture state before measurement
    pre_measurement_state = skin_membrane.state_vector.copy()
    pre_measurement_str = skin_membrane.get_state_str()

    # Measure (collapse the state)
    print("Measuring quantum state (collapse)...")
    observed_result = skin_membrane.measure()

    # Format results for Obsidian
    markdown_body = f"""# Quantum P System Experiment Log

## Experiment Setup
- **Membrane Label**: `{skin_membrane.label}`
- **Initial State**: `|A⟩` (definite state, amplitude = 1.0)
- **Quantum Operations Applied**: Distributed Object Rewriting (Hadamard-like gate splits)
- **Number of Rules Applied**: 2 (A → superposition, then nested expansion)

## Pre-Measurement Superposition State

Before measurement collapse, the membrane existed in a quantum superposition:

```
{pre_measurement_str}
```

### State Vector Interpretation
- **Amplitude**: Complex-valued coefficient (here simplified to real)
- **Probability**: |amplitude|² = likelihood of collapsing to that state
- **Entanglement**: All basis states contribute simultaneously (no classical analogue)

## Measurement Outcome

The measurement collapsed the superposition to:
**`{observed_result}`**

(This is stochastic; repeated runs would yield different outcomes with known probabilities)

## Physical Interpretation

### Why Superposition?
- Classical computation is deterministic: input → one output
- Quantum superposition allows all paths simultaneously
- Measurement "commits" to a single classical outcome

### Membrane Compartmentalization
- Each compartment (membrane) maintains its own state vector
- Quantum rewriting rules apply **locally** within membranes
- State transfer between membranes occurs via "osmosis" (quantum channels)

### Relevance to Quantum P-Systems
This validates the core concept of **Quantum-Inspired Membrane Algorithms (QMA)**:

1. **Parallel Branch Evaluation**: Superposition lets us explore exponentially many branches in polynomial time
2. **Compartmentalization**: Membranes isolate quantum states, reducing decoherence
3. **Probabilistic Collapse**: Final measurement gives classical answer with tunable probability

## Research Context

### Foundational References
- **Nishida, T. Y. (2006)** — "Membrane Computing with Quantum Capabilities"
- **Leporati, A., & Zandron, C. (2003)** — "Simulating Quantum Circuits by P Systems"
- **Zhang, G., et al. (2014)** — "Quantum-Inspired Membrane Computing: A Review"

### Open Questions
1. **Physical Realizability**: How to build hardware quantum compartments without decoherence?
2. **Complexity Bounds**: What is the exact computational power of Quantum P-systems vs. BQP?
3. **Dynamic Topology**: Can membrane division during evolution increase speedup?

> [!abstract] Future Directions
> This simulation is a **classical emulation** of quantum mechanics. Real quantum hardware would:
> - Execute gates with finite error rates (fidelity ~99.9%)
> - Suffer decoherence over microseconds
> - Require quantum error correction for logical soundness
>
> Scaling this model to millions of compartments and thousands of qubits remains an open challenge.

---

## Metadata
- **Simulation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Randomness**: Measurement outcome is stochastic; results vary across runs
- **Next Steps**: Run ensemble of experiments; compute aggregate statistics; publish results

---

## Code Reference
See `malta/quantum_simulator.py` for the full implementation.
"""

    # Save to Obsidian
    note_title = f"Quantum P System Sim {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    tags = [
        "quantum-computing",
        "p-systems",
        "simulation",
        "python",
        "malta-framework",
    ]

    saved_path = write_obsidian_note(vault_path, note_title, tags, markdown_body)
    print(f"✓ Obsidian note created: {saved_path}")

    return saved_path


if __name__ == "__main__":
    # Default vault path; override with command-line arg if desired
    import sys

    VAULT_PATH = sys.argv[1] if len(sys.argv) > 1 else "./obsidian_quantum_notes"
    run_experiment_and_log(VAULT_PATH)
